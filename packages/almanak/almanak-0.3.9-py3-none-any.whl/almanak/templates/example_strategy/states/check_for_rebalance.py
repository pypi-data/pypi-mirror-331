from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytz

from almanak.strategy.utils.price_volatility import get_price_and_volatility
from almanak.strategy.utils.utils import convert_time_window
from almanak.utils.utils import load_env_var_bool

from states.complete import complete
from models import RebalanceCondition, PriceDriftType, VolatilitySpreadType

if TYPE_CHECKING:
    from ..strategy import Strategy
    
DEBUG_ALWAYS_REBALANCE = load_env_var_bool("DEBUG_ALWAYS_REBALANCE")


def check_for_rebalance(strategy: "Strategy") -> None:
    """
    Evaluates the need for rebalancing the strategy based on market conditions and strategy parameters.

    This method checks various conditions to determine if a rebalance is needed:
    - Rebalance frequency (time-based)
    - Out-of-position period
    - Rebalance conditions based on price drift or volatility spread
    - Optional grace period to avoid frequent rebalances

    Sets the strategy's next state accordingly.

    Returns:
        None
    """
    date_now = datetime.now(pytz.utc)

    # Check if enough time has passed since the last rebalance check
    if not DEBUG_ALWAYS_REBALANCE and strategy.persistent_state.last_check_for_rebalance_time:
        time_passed = date_now - strategy.persistent_state.last_check_for_rebalance_time
        time_needed = timedelta(
            seconds=convert_time_window(strategy.recalculate_frequency, strategy.granularity, "1s")
        )
        if time_passed < time_needed:
            print(
                f"Skipping rebalance check based on recalculate frequency. "
                f"Passed: {time_passed}, Needed: {time_needed}"
            )
            complete(strategy, snapshot=False)
            return

    print("Checking for rebalance...")

    # Initialize rebalance flags
    rebalance_needed = False

    # Force rebalance for testing purposes
    if DEBUG_ALWAYS_REBALANCE:
        rebalance_needed = True

    # TODO: Add or remove any additional rebalance conditions
    
    # Check if rebalance is needed based on frequency
    if strategy.rebalance_frequency:
        if strategy.persistent_state.last_rebalance_time is None:
            raise ValueError("Last rebalance time is None. This should not happen.")
        window_minutes = convert_time_window(strategy.rebalance_frequency, strategy.granularity, "1m")
        time_passed = date_now - strategy.persistent_state.last_rebalance_time
        time_needed = timedelta(minutes=window_minutes)
        if time_passed > time_needed:
            rebalance_needed = True
            # Suggestion for logging the out-of-position rebalance trigger
            rebalance_frequency_context = {
                "rebalance_needed": True,
                "time_last_rebalance": str(strategy.persistent_state.last_rebalance_time),
                "time_now": str(date_now),
                "time_passed": str(time_passed),
                "time_needed": str(time_needed),
                "rebalance_frequency": strategy.rebalance_frequency,
            }
    else:
        time_passed = None
        time_needed = None

    # Check if rebalance is needed based on out-of-position period
    if strategy.rebalance_out_of_position_period:
        if check_out_of_position(strategy):
            if strategy.persistent_state.out_of_position_time is None:
                strategy.persistent_state.out_of_position_time = date_now
            else:
                window_seconds = convert_time_window(
                    strategy.rebalance_out_of_position_period, strategy.granularity, "1s"
                )
                time_passed_outofpos = date_now - strategy.persistent_state.out_of_position_time
                time_needed_outofpos = timedelta(seconds=window_seconds)
                if time_passed_outofpos > time_needed_outofpos:
                    rebalance_needed = True
                    # Suggestion for logging the out-of-position rebalance trigger
                    rebalance_outofpos_context = {
                        "rebalance_needed": True,
                        "time_outofpos": str(strategy.persistent_state.out_of_position_time),
                        "time_now": str(date_now),
                        "time_passed": str(time_passed_outofpos),
                        "time_needed": str(time_needed_outofpos),
                        "rebalance_frequency": strategy.rebalance_out_of_position_period,
                    }
        else:
            strategy.persistent_state.out_of_position_time = None

    # Check if rebalance is needed based on conditions and grace period
    if strategy.rebalance_grace_period:
        rebalance_needed_grace, rebalance_graceperiod_context = handle_grace_period(strategy)
        if rebalance_needed_grace:
            rebalance_needed = True
    else:
        rebalance_needed_conditions, rebalance_conditions_context = check_rebalance_condition(strategy)
        if rebalance_needed_conditions:
            rebalance_needed = True

    # Log the rebalance trigger(s)
    if rebalance_needed:
        print("Rebalance needed based on conditions.")
        # Set the next state to close position if a rebalance is needed
        if strategy.persistent_state.position_id != -1:
            strategy.persistent_state.current_state = strategy.State.CLOSE_POSITION
        else:
            print("Rebalance needed without an open position. Skipping close position.")
            # Handle cases where there is no position to close
            # strategy.persistent_state.current_state = strategy.State.OPEN_POSITION
    else:
        print("No rebalance needed.")
        strategy.persistent_state.current_state = strategy.State.COMPLETED

    # Log metrics if needed
    if rebalance_needed:
        # TODO: Implement logging of rebalance trigger metrics
        pass

    # Update the last check time
    strategy.persistent_state.last_check_for_rebalance_time = datetime.now(pytz.utc)

    # No actions required
    strategy.persistent_state.current_flowstatus = strategy.InternalFlowStatus.PREPARING_ACTION


def handle_grace_period(strategy: "Strategy") -> tuple[bool, dict]:
    """
    Manages a grace period before initiating a rebalance to avoid frequent rebalances.

    Returns:
        tuple[bool, dict]: A tuple containing a boolean indicating if rebalance is needed,
                           and a context dictionary with grace period information.
    """
    rebalance_needed = False
    current_time = datetime.now(pytz.utc)

    # TODO: Set the grace period time based on the strategy's rebalance grace period
    rebalance_grace_period_seconds = convert_time_window(
        strategy.rebalance_grace_period, strategy.granularity, "1s"
    )

    if check_rebalance_condition(strategy)[0] and strategy.persistent_state.grace_period_time is None:
        # Out of bounds detected and no grace period started -> start one.
        strategy.persistent_state.grace_period_time = current_time
        print(f"Rebalance needed at {strategy.persistent_state.grace_period_time}. Grace period started.")
    elif strategy.persistent_state.grace_period_time is not None:
        # Grace period started, check if over or not.
        if (current_time - strategy.persistent_state.grace_period_time) >= timedelta(
            seconds=rebalance_grace_period_seconds
        ):
            # Grace period has passed, check if position still needs rebalance.
            if check_rebalance_condition(strategy)[0]:
                rebalance_needed = True
            # Reset the grace period time regardless of rebalancing or not.
            strategy.persistent_state.grace_period_time = None
        else:
            print("Still within grace period, waiting...")

    # For metrics
    grace_period_context = {
        "rebalance_needed": rebalance_needed,
        "grace_period_time": str(strategy.persistent_state.grace_period_time),
        "current_time": str(current_time),
        "grace_period": str(strategy.rebalance_grace_period),
    }
    return rebalance_needed, grace_period_context


def check_out_of_position(strategy: "Strategy") -> bool:
    """
    Checks if the current price is out of the position bounds.

    Returns:
        bool: True if out of position, False otherwise.
    """
    pos_info = strategy.get_active_position_info(strategy.persistent_state.position_id)
    pool_tick = strategy.uniswap_v3.get_pool_current_tick(strategy.pool_address)

    if pos_info is None:
        raise ValueError(f"Position info not found for position ID {strategy.persistent_state.position_id}.")
    if pool_tick is None:
        raise ValueError("Pool tick is None. This should not happen.")

    lower_tick = pos_info[5]
    upper_tick = pos_info[6]

    # Ensure the bounds are correct (lower < upper)
    if lower_tick >= upper_tick:
        raise ValueError(f"Invalid position bounds: lower_tick {lower_tick} >= upper_tick {upper_tick}.")

    # Check if the current pool tick is outside the position bounds
    if pool_tick < lower_tick or pool_tick > upper_tick:
        return True  # Out of bounds
    return False  # In bounds


def check_rebalance_condition(strategy: "Strategy") -> tuple[bool, dict]:
    """
    Checks if a rebalance is needed based on the strategy's rebalance condition.

    Returns:
        tuple[bool, dict]: A tuple containing a boolean indicating if rebalance is needed,
                           and a context dictionary with condition details.
    """
    # Define supported conditions
    supported_conditions = [item.value for item in RebalanceCondition]

    if strategy.strategy_update_params.rebalance_condition.value not in supported_conditions:
        raise NotImplementedError(
            f"Rebalance condition {strategy.strategy_update_params.rebalance_condition} not supported."
        )

    # Check rebalance conditions
    if strategy.strategy_update_params.rebalance_condition in {
        RebalanceCondition.VSNPD,
        RebalanceCondition.VSOPD,
        RebalanceCondition.VOLATILITY_SPREAD,
        RebalanceCondition.PRICE_DRIFT,
    }:
        return check_rebalance_vspd(strategy)
    else:
        raise NotImplementedError(
            f"Rebalance condition {strategy.strategy_update_params.rebalance_condition} not supported."
        )


def check_rebalance_vspd(strategy: "Strategy") -> tuple[bool, dict]:
    """
    Checks for rebalance based on volatility spread and price drift.

    Returns:
        tuple[bool, dict]: A tuple containing a boolean indicating if rebalance is needed,
                           and a context dictionary with calculation details.
    """
    # Determine if price drift and volatility spread checks are needed
    price_drift_needed = strategy.strategy_update_params.rebalance_condition in {
        RebalanceCondition.PRICE_DRIFT,
        RebalanceCondition.VSNPD,
        RebalanceCondition.VSOPD,
    }
    volatility_spread_needed = strategy.strategy_update_params.rebalance_condition in {
        RebalanceCondition.VOLATILITY_SPREAD,
        RebalanceCondition.VSNPD,
        RebalanceCondition.VSOPD,
    }

    # Fetch price and volatility data
    price_window_multiplier = 1 if strategy.price_drift_type != PriceDriftType.AVERAGE_WINDOW else 2
    volatility_window_multiplier = (
        1 if strategy.volatility_spread_type != VolatilitySpreadType.AVERAGE_WINDOW else 2
    )
    price, volatility = get_price_and_volatility(
        price_model=strategy.price_model,
        volatility_model=strategy.volatility_model,
        pool=strategy.pool,
        granularity=strategy.granularity,
        price_window_multiplier=price_window_multiplier,
        volatility_window_multiplier=volatility_window_multiplier,
    )

    # Check price drift
    if price_drift_needed:
        price_drift_ratio, price_drift_context = calculate_price_drift_ratio(strategy, price.to_list())
        rebalance_on_drift = price_drift_ratio > strategy.price_drift_threshold
    else:
        rebalance_on_drift = False
        price_drift_context = {}

    # Check volatility spread
    if volatility_spread_needed:
        vol_spread_ratio, vol_spread_context = calculate_volatility_spread_ratio(strategy, volatility)
        rebalance_on_spread = vol_spread_ratio > strategy.volatility_spread_threshold
    else:
        rebalance_on_spread = False
        vol_spread_context = {}

    # Determine if rebalance is needed based on the condition
    match strategy.strategy_update_params.rebalance_condition:
        case RebalanceCondition.VOLATILITY_SPREAD:
            rebalance_needed = rebalance_on_spread
        case RebalanceCondition.PRICE_DRIFT:
            rebalance_needed = rebalance_on_drift
        case RebalanceCondition.VSNPD:
            rebalance_needed = rebalance_on_spread and rebalance_on_drift
        case RebalanceCondition.VSOPD:
            rebalance_needed = rebalance_on_spread or rebalance_on_drift
        case _:
            raise ValueError(f"Unsupported Rebalance Condition: {strategy.strategy_update_params.rebalance_condition}")

    # Prepare context for logging or debugging
    rebalance_context = {
        "rebalance_needed": rebalance_needed,
        "rebalance_on_spread": rebalance_on_spread,
        "rebalance_on_drift": rebalance_on_drift,
        "price_drift_context": price_drift_context,
        "volatility_spread_context": vol_spread_context,
    }

    return rebalance_needed, rebalance_context


def calculate_price_drift_ratio(strategy: "Strategy", price_list: list) -> tuple[float, dict]:
    """
    Calculates the price drift ratio based on the strategy's configuration.

    Args:
        strategy (Strategy): The strategy instance.
        price_list (list): A list of price data.

    Returns:
        tuple[float, dict]: A tuple containing the price drift ratio and a context dictionary.
    """
    if not price_list:
        raise ValueError("Price data is empty.")

    price_drift_ratio = None
    price_drift_context = {}

    match strategy.price_drift_type:
        case PriceDriftType.RAW_POSITION:
            pos_info = strategy.get_active_position_info(strategy.persistent_state.position_id)
            pos_lower = strategy.uniswap_v3.tick_to_price(
                pos_info[5], strategy.token0.decimals, strategy.token1.decimals
            )
            pos_upper = strategy.uniswap_v3.tick_to_price(
                pos_info[6], strategy.token0.decimals, strategy.token1.decimals
            )
            cur_price = price_list[-1]
            pos_price = pos_lower + ((pos_upper - pos_lower) * strategy.lp_bounds_ratio)
            price_drift = abs(cur_price - pos_price)
            price_drift_ratio = price_drift / pos_price
            price_drift_context = {
                "cur_price": cur_price,
                "pos_price": pos_price,
                "price_drift": price_drift,
                "price_drift_ratio": price_drift_ratio,
            }
        case PriceDriftType.MODEL_POSITION:
            last_open_model_price = strategy.persistent_state.last_open_model_price
            cur_price = price_list[-1]
            price_drift = abs(cur_price - last_open_model_price)
            price_drift_ratio = price_drift / last_open_model_price if last_open_model_price > 0 else float('inf')
            price_drift_context = {
                "cur_price": cur_price,
                "last_open_model_price": last_open_model_price,
                "price_drift": price_drift,
                "price_drift_ratio": price_drift_ratio,
            }
        case PriceDriftType.AVERAGE_WINDOW:
            price_window = strategy.price_model.params["price_window"]
            price_last_window = price_list[-price_window:]
            cur_price = price_last_window[-1]
            mean_abs_drift = np.mean(np.abs(np.diff(price_last_window)))
            price_drift_ratio = mean_abs_drift / np.mean(price_last_window[:-1])
            price_drift_context = {
                "cur_price": cur_price,
                "price_drift_ratio": price_drift_ratio,
                "mean_abs_drift": mean_abs_drift,
            }
        case _:
            raise ValueError(f"Unsupported Price Drift Type: {strategy.price_drift_type}")

    return price_drift_ratio, price_drift_context


def calculate_volatility_spread_ratio(strategy: "Strategy", volatility_df: pd.DataFrame) -> tuple[float, dict]:
    """
    Calculates the volatility spread ratio based on the strategy's configuration.

    Args:
        strategy (Strategy): The strategy instance.
        volatility_df (pd.DataFrame): A DataFrame containing volatility data.

    Returns:
        tuple[float, dict]: A tuple containing the volatility spread ratio and a context dictionary.
    """
    if volatility_df is None or volatility_df.empty:
        raise ValueError("Volatility data is empty.")

    vol_spread_ratio = None
    volatility_spread_context = {}

    match strategy.volatility_spread_type:
        case VolatilitySpreadType.RAW_POSITION:
            pos_info = strategy.get_active_position_info(strategy.persistent_state.position_id)
            pos_lower = strategy.uniswap_v3.tick_to_price(
                pos_info[5], strategy.token0.decimals, strategy.token1.decimals
            )
            pos_upper = strategy.uniswap_v3.tick_to_price(
                pos_info[6], strategy.token0.decimals, strategy.token1.decimals
            )
            volatility_last = volatility_df.iloc[-1]
            current_spread = abs(volatility_last["Upper Bound"] - volatility_last["Lower Bound"])
            position_spread = abs(pos_upper - pos_lower)
            vol_spread_ratio = abs(position_spread - current_spread) / position_spread
            volatility_spread_context = {
                "current_spread": current_spread,
                "position_spread": position_spread,
                "vol_spread_ratio": vol_spread_ratio,
            }
        case VolatilitySpreadType.AVERAGE_WINDOW:
            volatility_window = strategy.volatility_model.params["volatility_window"]
            volatility_last_window = volatility_df.iloc[-volatility_window:]
            spreads = abs(volatility_last_window["Upper Bound"] - volatility_last_window["Lower Bound"])
            current_spread = spreads.iloc[-1]
            vol_spread_ratio = abs(np.mean(spreads) - current_spread) / np.mean(spreads)
            volatility_spread_context = {
                "current_spread": current_spread,
                "mean_spread": np.mean(spreads),
                "vol_spread_ratio": vol_spread_ratio,
            }
        case _:
            raise ValueError(f"Unsupported Volatility Spread Type: {strategy.volatility_spread_type}")

    return vol_spread_ratio, volatility_spread_context
