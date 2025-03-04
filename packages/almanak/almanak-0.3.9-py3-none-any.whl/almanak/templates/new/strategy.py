import datetime
import sys
import os
from time import sleep

from states.initialization import initialization
from states.teardown import teardown

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from almanak.strategy.models import PersistentStateBase, StrategyConfigBase
from almanak.strategy.strategy_base import StrategyUniV3
class Strategy(StrategyUniV3):
    # TODO: Replace Strategy_Template with your strategy name, both here as well as in config.json
    STRATEGY_NAME = "Strategy_Template"

    def __init__(self, **kwargs):
        """
        Initialize the strategy with given configuration parameters.

        Args:
            **kwargs: Strategy-specific configuration parameters.
        """
        super().__init__()
        self.name = self.STRATEGY_NAME.replace("_", " ")
        # TODO: Initialize the strategy with the given configuration parameters
        self.initialize_persistent_state()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"chain={self.chain}, network={self.network}, protocol={self.protocol}, "
            f"wallet_address={self.wallet_address}, mode={self.mode})"
        )

    def initialize_persistent_state(self):
        """Initialize the strategy's persistent state."""
        self.persistent_state = {
            "current_state": "INITIALIZATION",
            "current_flowstatus": "PREPARING_ACTION",
            "current_actions": [],
            "initialized": False,
            "completed": False,
        } 

    @classmethod
    def get_persistent_state_model(cls):
        # TODO: Replace PersistentState with your strategy persistent state model
        return PersistentStateBase

    @classmethod
    def get_config_model(cls):
        # TODO: Replace StrategyConfig with your strategy configuration model
        return StrategyConfigBase

    @property
    def is_locked(self):
        """Check if the strategy is locked."""
        # TODO: Implement the strategy lock logic
        return True

    def restart_cycle(self)-> None:
        """A Strategy should only be restarted when the full cycle is completed."""
        # TODO: Implement the restart cycle logic
        return False

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
        # TODO: Implement the main strategy execution logic
        print("Running the strategy")
        print(self.persistent_state)

        match self.persistent_state["current_state"]:
            case "INITIALIZATION":
                initialization(self)
                self.persistent_state["current_state"] = "TEARDOWN"
            case "TEARDOWN":
                teardown(self)
                self.persistent_state["current_state"] = "INITIALIZATION"
            case _:
                raise ValueError(f"Unknown state: {self.persistent_state['current_state']}")
        
    def log_strategy_balance_metrics(self, action_id: str):
        """Logs strategy balance metrics per action. It is called in the StrategyBase class."""

        # TODO: Implement custom metrics logging logic
