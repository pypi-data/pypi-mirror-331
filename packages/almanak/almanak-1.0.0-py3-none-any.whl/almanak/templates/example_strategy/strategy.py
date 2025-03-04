import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from decimal import Decimal
from almanak.enterprise_library.metrics.metrics_agg import METRICS_DB_CONNECTION_STRING, MetricsAggHandler
from almanak.enterprise_library.models.action_bundle import ActionBundle
from almanak.strategy.strategy_base import StrategyUniV3
from almanak.strategy.utils.pool_token import Token, pooltoken_service
from almanak.strategy.utils.price_volatility import get_current_price
from almanak.strategy.utils.utils import to_readable
from almanak.utils.utils import (
    get_protocol_sdk,
    get_web3_by_network_and_chain,
)
from metrics import log_strategy_balance_metrics
from states import (
    initialization,
    check_for_rebalance,
    open_position,
    close_position,
    teardown,
    complete,
    swap_assets
)
from models import State, InternalFlowStatus, StrategyConfig, PersistentState, SubState

class Strategy(StrategyUniV3):
    # TODO: Replace Strategy_Template with your strategy name
    STRATEGY_NAME = "Strategy_Template"

    def __init__(self, **kwargs):
        """
        Initialize the strategy with given configuration parameters.

        Args:
            **kwargs: Strategy-specific configuration parameters.
        """
        super().__init__()
        self.name = self.STRATEGY_NAME.replace("_", " ")

        # Parse and validate the strategy configuration
        try:
            self.config = StrategyConfig(**kwargs)
        except Exception as e:
            raise ValueError(f"Invalid Strategy Configuration: {e}")

        # Assign configuration parameters to class variables for easy access
        self.State = State
        self.SubState = SubState
        self.id = self.config.id
        self.chain = self.config.chain
        self.network = self.config.network
        self.protocol = self.config.protocol
        self.wallet_address = self.config.wallet_address
        self.pool_address = self.config.pool_address
        self.granularity = self.config.granularity
        self.strategy_update_params = self.config.strategy_update_params
        self.initialization = self.config.initialization
        self.price_model = self.config.price_model
        self.volatility_model = self.config.volatility_model
        self.slippage = self.config.slippage
        self.pause_strategy = self.config.pause_strategy
        # --- Strategy Update Params ---
        self.strategy_update_params = self.config.strategy_update_params
        self.rebalance_condition = self.config.strategy_update_params.rebalance_condition
        self.recalculate_frequency = self.config.strategy_update_params.recalculate_frequency
        self.price_drift_threshold = self.config.strategy_update_params.price_drift_threshold
        self.price_drift_type = self.config.strategy_update_params.price_drift_type
        self.volatility_spread_threshold = self.config.strategy_update_params.volatility_spread_threshold
        self.volatility_spread_type = self.config.strategy_update_params.volatility_spread_type
        self.rebalance_grace_period = self.config.strategy_update_params.rebalance_grace_period
        self.rebalance_frequency = self.config.strategy_update_params.rebalance_frequency
        self.rebalance_out_of_position_period = (
            self.config.strategy_update_params.rebalance_out_of_position_period
        )
        self.lp_bounds_calculation = self.config.strategy_update_params.lp_bounds_calculation
        self.lp_bounds_ratio = self.config.strategy_update_params.lp_bounds_ratio
        # TODO: Add or remove configuration parameters as needed

        # Initialize protocol SDKs and services
        self.metrics_agg_handler = MetricsAggHandler(db_connection_string=METRICS_DB_CONNECTION_STRING)
        self.web3 = get_web3_by_network_and_chain(self.network, self.chain)
        self.uniswap_v3 = get_protocol_sdk(self.protocol, self.network, self.chain)

        self.pooltoken = pooltoken_service.get_registry(
            protocol=self.protocol,
            chain=self.chain,
            network=self.network,
            web3=self.web3,
            pool_abi=self.uniswap_v3.POOL_ABI,
            token_abi=self.uniswap_v3.ERC20_ABI,
        )

        self.pool = self.pooltoken.get_pool(self.pool_address)
        self.token0 = self.pool.token0
        self.token1 = self.pool.token1
        self.fee = self.pool.fee

        # Load or initialize the persistent state
        if not self.check_for_persistent_state_file():
            self.initialize_persistent_state()
        try:
            self.load_persistent_state()
        except Exception as e:
            raise ValueError(f"Unable to load persistent state: {e}")

        self.show_state(show_persistent_state=True)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"chain={self.chain}, network={self.network}, protocol={self.protocol}, "
            f"wallet_address={self.wallet_address}, mode={self.mode})"
        )

    @classmethod
    def get_persistent_state_model(cls):
        return PersistentState

    @classmethod
    def get_config_model(cls):
        return StrategyConfig

    def restart_cycle(self)-> None:
        """A Strategy should only be restarted when the full cycle is completed."""
        if (
            self.persistent_state.current_state == self.State.COMPLETED
            or self.persistent_state.current_state == self.State.CHECK_FOR_REBALANCE
        ):
            # Properly restart the cycle
            self.persistent_state.current_flowstatus = self.InternalFlowStatus.PREPARING_ACTION
            self.persistent_state.current_state = self.State.CHECK_FOR_REBALANCE
            self.persistent_state.completed = False

            # Dump the state to the persistent state because we load it when called.
            # NOTE: this is dangerous if reached halfway through a state. (hence the raise above!)
            self.save_persistent_state()
        elif self.persistent_state.current_state == self.State.TERMINATED:
            print("Strategy is terminated, nothing to restart.")
        else:
            raise ValueError("The strategy is not completed yet, can't restart.")

    def initialize_persistent_state(self):
        """
        Initializes the persistent state for the strategy.
        This method should be called when no existing state is found.
        """
        # TODO: Define the initial persistent state
        self.persistent_state = PersistentState(
            current_state=State.INITIALIZATION,
            current_flowstatus=InternalFlowStatus.PREPARING_ACTION,
            current_substate=SubState.INITIALIZATION_SWAP0,
            current_actions=[],
            initialized=False,
            completed=False,
            sadflow_counter=0,
            sadflow_actions=[],
            not_included_counter=0,
            position_id= -1,
            last_open_amounts=[0, 0],
            last_close_amounts=[0, 0],
            last_open_bounds=[0, 0],
            initialize_token_amounts=[0, 0],
            last_rebalance_time=datetime.datetime(2000, 1, 1),
            last_check_for_rebalance_time=datetime.datetime(2000, 1, 1),
            last_open_model_price=0,
            last_open_unallocated_amounts=[0, 0],
            last_close_amounts_total=[0, 0],
            last_close_amounts_fees=[0, 0],
            last_close_amounts_liquidity=[0, 0],
            last_swap_amounts=[0, 0],
            out_of_position_time=None,
            teardown_close_amounts_total=[0, 0],
            teardown_unwrap_target_amount=0,
            teardown_swap_amounts=[0, 0],
            teardown_unwrap_amount=0,
            unallocated_amounts=[0, 0],
            grace_period_time=None,
            # Initialize other state variables as needed
        )
        self.save_persistent_state()

    def run(self):
        """
        Executes the strategy by progressing through its state machine based on the current state.

        This method orchestrates the transitions between different states of the strategy,
        performing actions as defined in each state, and moves to the next state based on the
        actions' results and strategy's configuration.

        Returns:
            dict: A dictionary containing the current state, next state, and actions taken or
                recommended, depending on the execution mode.

        Raises:
            ValueError: If an unknown state is encountered, indicating a potential issue in state management.

        Notes:
            - This method is central to the strategy's operational logic, calling other methods
            associated with specific states like initialization, rebalancing, or closing positions.
            - It integrates debugging features to display balances and positions if enabled.
        """
        if self.config.pause_strategy:
            print("Strategy is paused.")
            return None

        try:
            self.load_persistent_state()
        except Exception as e:
            raise ValueError(f"Unable to load persistent state: {e}")

        # Check for teardown initiation
        if self.config.initiate_teardown and self.persistent_state.current_state in [
            State.COMPLETED,
            State.CHECK_FOR_REBALANCE,
        ]:
            self.persistent_state.current_state = State.TEARDOWN
            self.persistent_state.current_flowstatus = InternalFlowStatus.PREPARING_ACTION

        actions = None
        while self.is_locked and not actions:
            self.show_state()
            self.show_balances()
            self.show_positions()

            # TODO: Validate the state machine logic
            match self.persistent_state.current_state:
                case State.INITIALIZATION:
                    actions = initialization.initialization(self)
                case State.CHECK_FOR_REBALANCE:
                    actions = check_for_rebalance.check_for_rebalance(self)
                case State.OPEN_POSITION:
                    actions = open_position.open_position(self)
                case State.SWAP_ASSETS:
                    actions = swap_assets.swap_assets(self)
                case State.CLOSE_POSITION:
                    actions = close_position.close_position(self)
                case State.COMPLETED:
                    complete.complete(self)
                    actions = None
                case State.TEARDOWN:
                    actions = teardown(self)
                case State.TERMINATED:
                    print("Strategy is terminated.")
                    actions = None
                case _:
                    raise ValueError(f"Unknown state: {self.persistent_state.current_state}")

        # Save actions to persistent state
        if actions is None:
            self.persistent_state.current_actions = []
        elif isinstance(actions, ActionBundle):
            self.persistent_state.current_actions = [actions.id]
        elif isinstance(actions, list):
            self.persistent_state.current_actions = [action.id for action in actions]
        else:
            raise ValueError(f"Invalid actions type: {type(actions)}")

        # Save the persistent state before exiting
        self.save_persistent_state()
        return actions

    def get_initialize_amount(
        self,
        tokenX: Token,
        tokenX_available: int,
        value_USD: float,
    ) -> int:
        """
        Calculates the amount of a specific token needed to reach a specified USD value in the portfolio,
        considering the current market price of the token.

        Args:
            tokenX_symbol (str): Symbol of the token for which the amount is being calculated.
            tokenX_available (int): The amount of the token currently available/allocated for this strategy, in smallest unit (e.g., Wei for Ether).
            tokenX_decimals (int): The number of decimal places the token uses.
            value_USD (float): The target value in USD that needs to be reached with the token.

        Returns:
            int: The additional amount of the token required to reach the target USD value, in native format.
                 NOTE: Could be negative if the token amount available/provided exceeds the target value.

        IMPORTANT:
            - If the DataSource is Binance, we assume USD means USDT. (no correcting factor yet USDT/USD)
        """
        # Get the current prices for tokenX in USD
        price = get_current_price(
            data_source=self.price_model.data_source,
            pool=self.pool,
            base_symbol=tokenX.symbol,
            quote_symbol="USD",
            chain=self.chain,
        )

        # Calculate total amount needed in the native unit (int)
        amount_total = Decimal(value_USD) / Decimal(price)
        amount_total_native = int(amount_total * (10**tokenX.decimals))

        # Calculate amount required in the native unit (int)
        amount_required_native = max(0, amount_total_native - tokenX_available)

        # Convert amounts to human-readable format for printing
        tokenX_available_readable = to_readable(tokenX_available, tokenX.decimals)
        amount_required_readable = to_readable(amount_required_native, tokenX.decimals)

        print(f"Price of {tokenX.symbol} = {price:.4f} USD")
        print(
            f"Total Amount: {amount_total:.6f} {tokenX.symbol} = {tokenX_available_readable:.6f} (available) + {amount_required_readable:.6f} (needed)"
        )

        return amount_required_native

    def get_available_capital(self, include_last_swap_amounts: bool, verbose: bool = True) -> tuple:
        # Calculate the "new total capital" (close + last unallocated + swap readjustment)
        last_close_amounts = self.persistent_state.last_close_amounts_total
        if last_close_amounts[0] == 0 and last_close_amounts[1] == 0:
            raise ValueError("No amounts from the last close position. This should not happen.")

        last_unallocated_amounts = self.persistent_state.last_open_unallocated_amounts

        amount0 = last_close_amounts[0] + last_unallocated_amounts[0]
        amount1 = last_close_amounts[1] + last_unallocated_amounts[1]
        if include_last_swap_amounts:
            # Note: last_swap_amounts is formatted (+/-t0, +/-t1) tokens leaving the wallet has negative sign.
            last_swap_amounts = self.persistent_state.last_swap_amounts  # TODOM: Missing
            amount0 += last_swap_amounts[0]
            amount1 += last_swap_amounts[1]

        if verbose:
            print(
                f"Available Capital = {amount0}, {amount1} : Close = {self.persistent_state.last_close_amounts_total}, Unallocated = {self.persistent_state.last_open_unallocated_amounts}, Swap = {self.persistent_state.last_swap_amounts if include_last_swap_amounts else 'N/A'}"
            )
        return amount0, amount1
    
    def log_strategy_balance_metrics(self, action_id: str):
        """Logs strategy balance metrics per action. It is called in the StrategyBase class."""

        log_strategy_balance_metrics(self, action_id)
