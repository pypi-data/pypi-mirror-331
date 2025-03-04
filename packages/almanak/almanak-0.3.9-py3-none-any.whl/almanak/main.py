import copy
import json
import sys
import time
import traceback
from datetime import datetime, timedelta
from pprint import pprint

import pytz
from almanak.enterprise_library.constants import MainStatus
from almanak.enterprise_library.custom_exceptions import SimulationError
from almanak.enterprise_library.init_sdk import initialize_sdks
from almanak.enterprise_library.profiler.time_block import ProfileType
from almanak.enterprise_library.profiler.utils import time_block
from almanak.executer.execution_manager import ExecutionManager
from almanak.post_processing.post_process_manager import PostProcessManager
from almanak.signer.account_manager import AccountManager
from almanak.strategy.models import Mode
from almanak.strategy.strategy_factory import (
    create_strategy_from_config,
    get_strategy_ids_from_config,
)
from almanak.strategy.strategy_id_iterator import StrategyIDIterator
from almanak.transaction_builder.builder_manager import TransactionManager
from almanak.utils.logger import get_logger, get_non_alert_logger, setup_logging
from almanak.utils.utils import load_env_var, load_env_var_bool
from google.api_core.exceptions import GoogleAPICallError, NotFound
from google.cloud import logging as cloud_logging
from google.cloud import storage
from retry import retry

setup_logging()
logger = get_logger(__name__)
logger.info("Running main application.")

IS_AGENT_DEPLOYMENT = True
DEBUG = True

if IS_AGENT_DEPLOYMENT:
    import os

    print("Environment Variables:")
    pprint({**os.environ})

# --------------------------------------------------------------
# Suppress specific UserWarning related to Google Cloud credentials
import warnings

warnings.filterwarnings(
    "ignore",
    message="Your application has authenticated using end user credentials from Google Cloud SDK without a quota project.",
)
# --------------------------------------------------------------

cloud_logging_service_name = load_env_var("CLOUD_LOGGING_SERVICE_NAME")
cloud_logger = cloud_logging.Client().logger(cloud_logging_service_name)

TRANSIENT_TIME_MINUTES = 30
transient_time_threshold = timedelta(minutes=TRANSIENT_TIME_MINUTES)
transient_exception_types = (SimulationError,)
transient_exception_tracker = {}

MAINLOOP_DELAY_SECONDS = int(load_env_var("MAINLOOP_DELAY_SECONDS"))
if MAINLOOP_DELAY_SECONDS <= 0:
    raise ValueError(f"MAINLOOP_DELAY_SECONDS must be >0. Found {MAINLOOP_DELAY_SECONDS}")

SHUTDOWN = load_env_var_bool("SHUTDOWN")
READ_ONLY_MODE = load_env_var_bool("READ_ONLY_MODE")
CONFIG_FILE_NAME = "config.json"
MAX_ALLOWED_TRANSIENT_EXCEPTIONS = 3


def read_config_file():
    """
    Read the main configuration file from Google Cloud Storage. The path is provided via environment variables.
    """
    GCS_BUCKET_NAME = load_env_var("GCS_BUCKET_NAME")
    CLIENT_NAME = load_env_var("CLIENT_NAME")
    DEPLOYMENT_NAME = load_env_var("DEPLOYMENT_NAME")

    try:
        if not all([GCS_BUCKET_NAME, CLIENT_NAME, DEPLOYMENT_NAME, CONFIG_FILE_NAME]):
            # Read config file from local file system
            config_file_path = os.path.join(load_env_var("WORKING_DIR"), "local_storage", "config", CONFIG_FILE_NAME)
            with open(config_file_path, "r") as f:
                config = json.load(f)
                return config


        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob_name = f"{CLIENT_NAME}/{DEPLOYMENT_NAME}/config/{CONFIG_FILE_NAME}"
        blob = bucket.blob(blob_name)

        if not blob.exists():
            raise FileNotFoundError(f"Config file does not exist at {blob_name}")

        json_data = blob.download_as_text()
        config = json.loads(json_data)
        return config

    except NotFound:
        # logger.info(f"Blob {blob_name} not found in GCS bucket.")
        raise FileNotFoundError(f"Blob {blob_name} not found in GCS bucket.")
    except GoogleAPICallError as e:
        # logger.info(f"Failed to access Cloud Storage: {str(e)}")
        raise GoogleAPICallError(f"Failed to access Cloud Storage: {str(e)}")
    except json.JSONDecodeError as e:
        # logger.info(f"Error decoding JSON from the configuration file: {str(e)}")
        raise ValueError(f"Error decoding JSON from the configuration file: {str(e)}")
    except Exception as e:
        # logger.info(f"Unexpected error occurred: {str(e)}")
        raise Exception(f"Unexpected error occurred: {str(e)}")


def single_main_iteration(config: dict, strategy_id: str):
    """
    Runs a single iteration of the main loop for a given strategy.
    If the strategy raises/crashes, the main will loop thru other strategies and come back to this one later.
    """
    # logger.info("Starting main iteration")

    transaction_manager = TransactionManager()
    account_manager = AccountManager()
    execution_manager = ExecutionManager()
    post_process_manager = PostProcessManager()

    try:
        copied_config = copy.deepcopy(config)
        strategy = create_strategy_from_config(copied_config, strategy_id)
        if DEBUG:
            import json

            print("Strategy Config:")
            print(json.dumps(copied_config, indent=4))
            print("Strategy id:")
            print(strategy_id)
    except Exception as e:
        logger.error(f"Error creating strategy from config: {config}. {e}")
        traceback.print_exc()
        return MainStatus.MAIN_ERROR

    print("================================================================")
    print("Starting Strategy:", strategy_id)

    if not strategy.is_paused:
        # Restarting strategy if it was previously completed. (not initializing! very different)
        if not strategy.is_locked:
            strategy.restart_cycle()

        # TODO: Add timeout/killswitch for each strategy iteration (avoid deadend)?
        # TODO: Add a watchdog for strategies that are stuck in a loop (avoid infinity loop)?

        # A Strategy loops over its state machine until a "cycle" is completed (i.e. going back to checking market conditions).
        while strategy.is_locked:
            with time_block(
                name="strategy_run",
                type=ProfileType.STRATEGY,
                strategy_id=strategy.id,
                strategy_state=strategy.persistent_state.current_state.value,
                strategy_substate=strategy.persistent_state.current_substate.value,
            ):
                actions = strategy.run()

            if strategy.mode == Mode.EXECUTION and actions:
                with time_block(
                    name="build_transaction",
                    type=ProfileType.BUILD_TRANSACTION,
                    strategy_id=strategy.id,
                    strategy_state=strategy.persistent_state.current_state.value,
                    action_type=actions.get_action_types(),
                    action_id=actions.id,
                ):
                    transaction_manager.build_transactions_from_action_bundle(actions)
                with time_block(
                    name="sign_transaction",
                    type=ProfileType.SIGN_TRANSACTION,
                    strategy_id=strategy.id,
                    strategy_state=strategy.persistent_state.current_state.value,
                    action_type=actions.get_action_types(),
                    action_id=actions.id,
                ):
                    account_manager.sign_transactions(actions)
                with time_block(
                    name="execute_transaction",
                    type=ProfileType.EXECUTE_TRANSACTION,
                    strategy_id=strategy.id,
                    strategy_state=strategy.persistent_state.current_state.value,
                    action_type=actions.get_action_types(),
                    action_id=actions.id,
                ):
                    execution_manager.execute_transaction_bundle(actions)
                with time_block(
                    name="post_process",
                    type=ProfileType.POST_PROCESS,
                    strategy_id=strategy.id,
                    strategy_state=strategy.persistent_state.current_state.value,
                    action_type=actions.get_action_types(),
                    action_id=actions.id,
                ):
                    post_process_manager.process_bundle(actions)

        if strategy.mode == Mode.RECOMMENDATIONS and actions:
            print("=========== RECOMMENDATIONS ==================")
            print(actions)
            print("==============================================")
            raise NotImplementedError("Recommendations not implemented yet.")
    else:
        print("Strategy is paused. Skipping.")

    print("Releasing Strategy:", strategy_id)
    print("================================================================")

    return MainStatus.MAIN_SUCCESS


def main(strategy_id_iterator: StrategyIDIterator):
    """
    Continuously run the main iteration of the enterprise service.
    The retry function has exponential backoff and jitter to prevent
    overloading the system with retries.

    NOTE: This is a simple retry mechanism. It is not a robust solution
    for handling errors. It is only used to prevent the service from
    crashing due to transient errors.

    NOTE: This could cause a cascading alerts if the error is not transient.
    """
    initialize_sdks()
    config = read_config_file()

    print("-----------------------------------------------")
    print("Strategies:", strategy_ids)
    pprint(config)
    print("-----------------------------------------------")

    strategy_loop_counter = 0
    while True:
        try:
            # Re-read the config file every time we loop through all strategies (note: will ignore new ones).
            # TODO: [V1] Move this into the strategy code with a "reread config" timer.
            if strategy_loop_counter % len(strategy_ids) == 0:
                config = read_config_file()

            strategy_id = strategy_id_iterator.get_active_strategy_id()
            strategy_id_iterator.update_to_next_strategy()  # Moves to next in case we raise in single_main_iteration
            with time_block(name="single_main_iteration", type=ProfileType.TOTAL, strategy_id=strategy_id):
                single_main_iteration(config=copy.deepcopy(config), strategy_id=strategy_id)
            strategy_loop_counter += 1
            sleep_time = min(MAINLOOP_DELAY_SECONDS, 3600)
            # logger.info(f"Waiting {sleep_time} seconds to check again.")
            print(f"Waiting {sleep_time} seconds to check again.")
            time.sleep(sleep_time)
        except Exception as e:
            tb_str = traceback.format_exc()
            print(tb_str)
            raise e


if __name__ == "__main__":
    """
    If any errors are raised, just retry the main function
    """
    max_retries = sys.maxsize

    if IS_AGENT_DEPLOYMENT:
        max_retries = 1

    current_retries = 0

    # Helper functionality for infra buffer shutdown
    if SHUTDOWN or READ_ONLY_MODE:
        print(
            f"SHUTDOWN={SHUTDOWN} | READ_ONLY_MODE={READ_ONLY_MODE} environment variables detected. Sleeping indefinitely..."
        )
        while True:
            time.sleep(999999)  # Large number for indefinite sleep
    else:
        print("SHUTDOWN environment variable not found. Continuing normal operation.")

    config = read_config_file()
    strategy_ids = get_strategy_ids_from_config(config)
    strategy_id_iterator = StrategyIDIterator
    strategy_id_iterator.initialize(strategy_ids)

    # Continuously run the main function
    while current_retries < max_retries:
        try:
            main(strategy_id_iterator)
        except KeyboardInterrupt:
            print("Detected KeyboardInterrupt. Exiting.")
            break
        except Exception as e:
            current_retries += 1
            strategy_id = strategy_id_iterator.get_active_strategy_id()

            # Check if the exception is transient
            if isinstance(e, transient_exception_types):

                if strategy_id not in transient_exception_tracker:
                    transient_exception_tracker[strategy_id] = {
                        type(e): {"time": datetime.now(tz=pytz.UTC), "count": 0}
                    }

                last_transient_exception = transient_exception_tracker[strategy_id][type(e)]
                last_transient_exception_count = last_transient_exception["count"]
                last_transient_exception_time = last_transient_exception["time"]

                current_time = datetime.now(tz=pytz.UTC)

                if current_time - last_transient_exception_time < transient_time_threshold:
                    transient_exception_tracker[strategy_id][type(e)]["time"] = current_time
                    transient_exception_tracker[strategy_id][type(e)]["count"] += 1
                else:
                    transient_exception_tracker[strategy_id][type(e)] = {
                        "time": current_time,
                        "count": 1,
                    }

                if (
                    transient_exception_tracker[strategy_id][type(e)]["count"]
                    >= MAX_ALLOWED_TRANSIENT_EXCEPTIONS
                ):
                    error_message = f"Same transient error of type '{type(e).__name__}' occurred 3 times in a row for {strategy_id}: {e}"
                    logger.error(error_message)
                    traceback.print_exc()

                    # reset the counter
                    transient_exception_tracker[strategy_id][type(e)] = {
                        "time": current_time,
                        "count": 0,
                    }

            else:
                traceback.print_exc()
                logger.error(f"main enterprise loop crashed at retry {current_retries}. Error: {e}")
