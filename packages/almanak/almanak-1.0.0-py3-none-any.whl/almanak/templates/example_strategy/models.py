from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, confloat, conint
from web3 import Web3

from almanak.enterprise_library.enums import Chain, Network, Protocol
from almanak.strategy.models import (
    InternalFlowStatus,
    Mode,
    PersistentStateBase,
    StrategyConfigBase,
)
from almanak.strategy.utils.utils import DataFormat, DataSource

class State(Enum):
    """Enum representing the main states of the strategy."""

    INITIALIZATION = "INITIALIZATION"
    CHECK_FOR_REBALANCE = "CHECK_FOR_REBALANCE"
    CLOSE_POSITION = "CLOSE_POSITION"
    SWAP_ASSETS = "SWAP_ASSETS"
    OPEN_POSITION = "OPEN_POSITION"
    COMPLETED = "COMPLETED"  # A "Cycle" is completed between checks for rebalance
    TEARDOWN = "TEARDOWN"
    TERMINATED = "TERMINATED"  # The strategy is terminated (manual intervention required)
    # TODO: Add or remove any states relevant to your strategy

class SubState(Enum):
    """Enum representing the substates within the main states of the strategy."""

    NO_SUBSTATE = "NO_SUBSTATE"
    # Example substates during initialization
    INITIALIZATION_SWAP0 = "INITIALIZATION_SWAP0"
    INITIALIZATION_SWAP1 = "INITIALIZATION_SWAP1"
    INITIALIZATION_OPEN = "INITIALIZATION_OPEN"
    # Example substates during teardown
    TEARDOWN_CLOSE = "TEARDOWN_CLOSE"
    TEARDOWN_SWAP0 = "TEARDOWN_SWAP0"
    TEARDOWN_SWAP1 = "TEARDOWN_SWAP1"
    TEARDOWN_UNWRAP = "TEARDOWN_UNWRAP"
    # TODO: Add or remove any substates relevant to your strategy

class PersistentState(PersistentStateBase):
    """Model of the state of the strategy across executions"""

    current_state: State
    current_substate: SubState
    current_flowstatus: InternalFlowStatus
    current_actions: list[UUID]
    sadflow_counter: int
    sadflow_actions: list[UUID]
    not_included_counter: int
    position_id: int
    last_open_amounts: tuple[int, int]
    last_close_amounts: tuple[int, int]
    last_open_bounds: tuple[int, int]
    initialize_token_amounts: tuple[int, int]
    last_rebalance_time: datetime
    last_check_for_rebalance_time: datetime
    last_open_model_price: float
    last_open_unallocated_amounts: tuple[int, int]
    last_close_amounts_total: tuple[int, int]
    last_close_amounts_fees: tuple[int, int]
    last_close_amounts_liquidity: tuple[int, int]
    last_swap_amounts: tuple[int, int]
    out_of_position_time: datetime | None
    teardown_close_amounts_total: tuple[int, int]
    teardown_unwrap_target_amount: int
    teardown_swap_amounts: tuple[int, int]
    teardown_unwrap_amount: int
    unallocated_amounts: tuple[int, int]
    grace_period_time: datetime | None  # The "None" mechanism is used to reset.
    # TODO: Add or remove any fields to track the state of your strategy

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data["current_state"] = self.current_state.value
        data["current_substate"] = self.current_substate.value
        data["current_flowstatus"] = self.current_flowstatus.value
        data["current_actions"] = [str(action) for action in self.current_actions]
        data["sadflow_actions"] = [str(action) for action in self.sadflow_actions]
        data["not_included_counter"] = self.not_included_counter
        data["last_check_for_rebalance_time"] = self.last_check_for_rebalance_time.isoformat()
        data["last_rebalance_time"] = self.last_rebalance_time.isoformat()
        if self.out_of_position_time is not None:
            data["out_of_position_time"] = self.out_of_position_time.isoformat()
        else:
            data["out_of_position_time"] = None
        if self.grace_period_time is not None:
            data["grace_period_time"] = self.grace_period_time.isoformat()
        else:
            data["grace_period_time"] = None

        # TODO: Add or remove any fields to track the state of your strategy

        return data

class InitializationConfig(BaseModel):
    """Model for the initialization configuration of the strategy"""

    initial_position_value_USD: confloat(ge=0)  # Ensure the value is greater than or equal to 0
    initial_funding_token: str  # Address of the funding token
    initial_token0_pool: str  # Address of the pool for token0
    initial_token1_pool: str  # Address of the pool for token1
    initial_funding_token0_amount: conint(ge=0)  # Non-negative amount
    initial_funding_token1_amount: conint(ge=0)  # Non-negative amount
    # TODO: Add ore remove any initialization parameters required

class ModelConfig(BaseModel):
    """Model for the configuration of a model used in the strategy (e.g., price and volatility models)"""

    method: str
    params: dict[str, Any]
    data_source: DataSource
    data_format: DataFormat

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data["data_source"] = self.data_source.value
        data["data_format"] = self.data_format.value
        return data

class RebalanceCondition(Enum):
    VOLATILITY_SPREAD = "VOLATILITY_SPREAD"
    PRICE_DRIFT = "PRICE_DRIFT"
    VSNPD = "VSNPD"  # Volatility Spread AND Price Drift
    VSOPD = "VSOPD"  # Volatility Spread OR Price Drift
    # TODO: Add or remove any additional rebalance conditions

class LPBoundsCalculation(Enum):
    VOLATILITY = "VOLATILITY"
    # TODO: Add or remove any additional LP bounds calculation methods

class PriceDriftType(Enum):
    RAW_POSITION = "RAW_POSITION"
    MODEL_POSITION = "MODEL_POSITION"
    AVERAGE_WINDOW = "AVERAGE_WINDOW"
    # TODO: Add or remove any additional price drift types

class VolatilitySpreadType(Enum):
    RAW_POSITION = "RAW_POSITION"
    AVERAGE_WINDOW = "AVERAGE_WINDOW"
    # TODO: Add or remove any additional volatility spread types

class StrategyUpdateParamsConfig(BaseModel):
    """Model for the configuration of strategy update parameters"""

    recalculate_frequency: conint(ge=0)  # Frequency to check for rebalance in granularity units
    rebalance_condition: RebalanceCondition
    lp_bounds_calculation: LPBoundsCalculation
    lp_bounds_ratio: confloat(ge=0, le=1)  # Ratio between 0 and 1
    price_drift_threshold: float | None  # Threshold for price drift (e.g., 0.05 for 5%)
    price_drift_type: PriceDriftType | None
    volatility_spread_threshold: float | None  # Threshold for volatility spread
    volatility_spread_type: VolatilitySpreadType | None
    rebalance_frequency: int | None  # Frequency to force a rebalance
    rebalance_grace_period: int | None  # Grace period for rebalance
    rebalance_out_of_position_period: int | None  # Out-of-position period before rebalancing
    # TODO: Add or remove additional parameters

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        data["recalculate_frequency"] = self.recalculate_frequency
        data["rebalance_condition"] = self.rebalance_condition.value
        data["lp_bounds_calculation"] = self.lp_bounds_calculation.value
        data["lp_bounds_ratio"] = self.lp_bounds_ratio
        if self.price_drift_threshold:
            data["price_drift_threshold"] = self.price_drift_threshold
        if self.price_drift_type:
            data["price_drift_type"] = self.price_drift_type.value
        if self.volatility_spread_threshold:
            data["volatility_spread_threshold"] = self.volatility_spread_threshold
        if self.volatility_spread_type:
            data["volatility_spread_type"] = self.volatility_spread_type.value
        if self.rebalance_frequency:
            data["rebalance_frequency"] = self.rebalance_frequency
        if self.rebalance_grace_period:
            data["rebalance_grace_period"] = self.rebalance_grace_period
        if self.rebalance_out_of_position_period:
            data["rebalance_out_of_position_period"] = self.rebalance_out_of_position_period
        return data

class SlippageConfig(BaseModel):
    """Model for the configuration of slippage parameters"""

    slippage_swap: confloat(ge=0, le=1)  # Between 0 and 1
    slippage_open: confloat(ge=0, le=1)  # Between 0 and 1
    slippage_close: confloat(ge=0, le=1)  # Between 0 and 1
    slippage_spot_rate: confloat(ge=0, le=1)  # Between 0 and 1

# If your strategy uses a secondary position, include its configuration
# TODO: If your strategy does not use a secondary position, remove this class
class SecondaryPositionConfig(BaseModel):
    width: confloat(ge=0, le=1)  # Width ratio relative to primary position
    offset: confloat(ge=0, le=1)  # Offset ratio relative to primary position
    buffer: int  # Buffer amount
    # TODO: Add or remove additional parameters for the secondary position

class StrategyConfig(StrategyConfigBase):
    """Model for the configuration of the strategy"""
    id: str
    network: Network
    chain: Chain
    protocol: Protocol
    wallet_address: str
    pool_address: str
    granularity: str
    initiate_teardown: bool
    pause_strategy: bool
    mode: Mode
    initialization: InitializationConfig
    price_model: ModelConfig
    volatility_model: ModelConfig
    strategy_update_params: StrategyUpdateParamsConfig
    slippage: SlippageConfig
    # TODO: Add or remove any fields to configure your strategy
    # For example:
    # max_sadflow_retries: int 
    # max_not_included_retries: int
    # Include secondary position configuration if applicable
    # secondary_position: SecondaryPositionConfig | None

    def validate_ethereum_address(cls, value):
        if not Web3.is_address(value):
            raise ValueError("Invalid Ethereum address")
        return value

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        data["network"] = self.network.value
        data["chain"] = self.chain.value
        data["protocol"] = self.protocol.value
        data["mode"] = self.mode.value
        data["initialization"] = self.initialization.model_dump()
        data["price_model"] = self.price_model.model_dump()
        data["volatility_model"] = self.volatility_model.model_dump()
        data["strategy_update_params"] = self.strategy_update_params.model_dump()
        data["slippage"] = self.slippage.model_dump()
        # TODO: Add or remove any fields that you want configured in the strategy
        
        return data