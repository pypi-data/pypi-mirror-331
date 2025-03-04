from datetime import datetime
from functools import partial
from typing import TYPE_CHECKING

import pytz

from almanak.enterprise_library.enums import ActionType, ExecutionStatus, TransactionType
from almanak.enterprise_library.models.action import Action
from almanak.enterprise_library.models.action_bundle import ActionBundle
from almanak.enterprise_library.models.params import OpenPositionParams
from almanak.strategy.utils.price_volatility import get_current_price_and_volatility
from almanak.strategy.utils.utils import create_approve_2tokens_actions, to_readable

from models import LPBoundsCalculation

if TYPE_CHECKING:
    from ..strategy import Strategy


def open_position(strategy: "Strategy") -> ActionBundle:
    """
    Opens a new liquidity position based on the current market conditions and strategy settings.

    Args:
        strategy (Strategy): The strategy instance.

    Returns:
        ActionBundle: A bundle of actions including token approvals and the open/mint transaction.
    """

    # TODO: Add or remove any additional open position logic
    
    # Handle the state with actions
    return strategy.handle_state_with_actions(
        prepare_fn=partial(prepare_open_position, strategy),
        validate_fn=partial(validate_open_position, strategy),
        sadflow_fn=partial(sadflow_open_position, strategy),
        next_state=strategy.State.COMPLETED,
    )


def prepare_open_position(strategy: "Strategy") -> ActionBundle:
    """
    Prepares the open position actions.

    Returns:
        ActionBundle: A bundle of actions including token approvals and the open/mint transaction.
    """
    print(f"Opening new position with {strategy.lp_bounds_calculation} calculation...")

    # Calculate the new position amounts and price bounds
    position = calculate_position(strategy)
    amount0, amount1 = position["amounts"]
    price_lower, price_upper = position["range"]
    open_slippage = max(strategy.slippage.slippage_open, position["open_slippage"])

    # Save the model price at the time of open for future drift calculations
    strategy.persistent_state.last_open_model_price = position["model_price"]

    print(
        f"New Position (expected): {to_readable(amount0, strategy.token0.decimals):.6f} {strategy.token0.symbol} | "
        f"{to_readable(amount1, strategy.token1.decimals):.6f} {strategy.token1.symbol} "
        f"[{price_lower}, {price_upper}], slippage={open_slippage*100:.1f}%"
    )

    # Create approval actions for the tokens
    action_approve0, action_approve1 = create_approve_2tokens_actions(
        token0_address=strategy.token0.address,
        token1_address=strategy.token1.address,
        from_address=strategy.wallet_address,
        spender_address=strategy.uniswap_v3.UNISWAP_V3_POSITION_MANAGER_ADDRESS,
        amount0=int(amount0),  # Buffer added at the SDK level
        amount1=int(amount1),  # Buffer added at the SDK level
        protocol=strategy.protocol,
    )

    # Create the open position action
    action_open = Action(
        type=ActionType.OPEN_LP_POSITION,
        params=OpenPositionParams(
            token0=strategy.token0.address,
            token1=strategy.token1.address,
            fee=strategy.fee,
            price_lower=price_lower,
            price_upper=price_upper,
            amount0_desired=int(amount0),
            amount1_desired=int(amount1),
            recipient=strategy.wallet_address,
            slippage=open_slippage,
        ),
        protocol=strategy.protocol,
    )

    # Return the action bundle
    return ActionBundle(
        actions=[action_approve0, action_approve1, action_open],
        chain=strategy.chain,
        network=strategy.network,
        strategy_id=strategy.id,
        config=strategy.config,
        persistent_state=strategy.persistent_state,
    )


def validate_open_position(strategy: "Strategy") -> bool:
    """
    Validates the open position actions and retrieves the executed amounts in the execution details.

    Returns:
        bool: True if the open position actions were successful and the amounts were retrieved correctly.
    """
    actions = strategy.executioner_status.get("actions", None)

    if not actions:
        raise ValueError("Validation failed (Open): No actions found. Cannot skip an Open Position.")

    # Ensure the actions were successful
    if actions.status != ExecutionStatus.SUCCESS:
        raise ValueError(f"Validation failed (Open): Expected SUCCESS, Received: {actions.status}")

    # Ensure there are three actions: approve0, approve1, and open position
    if len(actions.actions) != 3:
        raise ValueError(f"Validation failed: Expected 3 actions, Received: {len(actions.actions)}")
    if actions.actions[2].type != ActionType.OPEN_LP_POSITION:
        raise ValueError(
            f"Validation failed: Expected action[2] OPEN_LP_POSITION, Received: {actions.actions[2].type}"
        )

    # Get the execution details of the open position action
    position_opened = actions.actions[2].get_execution_details()
    if not position_opened:
        raise ValueError("Validation failed: No receipt found for open position")

    if position_opened.type != ActionType.OPEN_LP_POSITION:
        raise ValueError(
            f"Validation failed: Expected receipt OPEN_LP_POSITION, Received: {position_opened.type}"
        )

    # Update persistent state with position ID and amounts
    strategy.persistent_state.position_id = position_opened.position_id
    strategy.persistent_state.last_open_amounts = (position_opened.amount0, position_opened.amount1)
    strategy.persistent_state.last_open_bounds = (
        position_opened.bound_tick_lower,
        position_opened.bound_tick_upper,
    )

    if not actions.executed_at:
        raise ValueError(
            f"Validation failed: no executed_at timestamp found for open position actions. {actions}"
        )

    # Update last rebalance time and reset the last check for rebalance time
    strategy.persistent_state.last_rebalance_time = datetime.fromtimestamp(
        actions.executed_at, pytz.utc
    )
    strategy.persistent_state.last_check_for_rebalance_time = strategy.persistent_state.last_rebalance_time

    # Calculate unallocated amounts
    amount0, amount1 = strategy.get_available_capital(include_last_swap_amounts=True)
    unallocated_amount0 = amount0 - position_opened.amount0
    unallocated_amount1 = amount1 - position_opened.amount1
    strategy.persistent_state.last_open_unallocated_amounts = (unallocated_amount0, unallocated_amount1)

    if any([x < 0 for x in strategy.persistent_state.last_open_unallocated_amounts]):
        raise ValueError(
            f"Negative unallocated assets after opening a position: {strategy.persistent_state.last_open_unallocated_amounts}"
        )

    # Debug prints
    print(position_opened)
    print("Available Capital:", (amount0, amount1))
    print("Unallocated Amounts:", strategy.persistent_state.last_open_unallocated_amounts)

    return True


def sadflow_open_position(strategy: "Strategy") -> ActionBundle:
    """
    Handles the sadflow (error handling) for the open position state.
    Calls the appropriate function based on the status of the actions.
    """
    actions = strategy.executioner_status.get("actions", None)
    if not actions:
        raise ValueError("Sadflow open position: No actions found.")

    match actions.status:
        case ExecutionStatus.FAILED | ExecutionStatus.CANCELLED | ExecutionStatus.NOT_INCLUDED:
            return sadflow_retry(strategy)
        case ExecutionStatus.PARTIAL_EXECUTION:
            return sadflow_partial_retry(strategy)
        case ExecutionStatus.SUCCESS:
            raise ValueError("Sadflow open position with SUCCESS Status. Should not happen.")
        case _:
            raise ValueError(f"Invalid status for validate open position: {actions.status}")


def sadflow_retry(strategy: "Strategy") -> ActionBundle:
    """
    Handles the basic retry sadflow for open position.

    Returns:
        ActionBundle: A new action bundle to retry the open position.
    """
    print("Sadflow Retry: Retrying open position...")
    # TODO: Set your own retry logic here
    # Example:
    return prepare_open_position(strategy)  # Retrying the same state


def sadflow_partial_retry(strategy: "Strategy") -> ActionBundle:
    """
    Handles the partial retry sadflow for open position.

    Returns:
        ActionBundle: A new action bundle to retry the open position.
    """
    # TODO: Set your own retry logic here
    # Example:

    # Only support 1 retry attempt to avoid infinite loops
    if strategy.persistent_state.sadflow_actions and len(strategy.persistent_state.sadflow_actions) > 0:
        raise ValueError(
            "Partial Retry (Open): Sadflow Partial Retry already attempted. Halting strategy for human intervention."
        )

    actions = strategy.executioner_status["actions"]
    if actions.status != ExecutionStatus.PARTIAL_EXECUTION:
        raise ValueError("Partial Retry (Open): Expected PARTIAL_EXECUTION status.")

    print("Entering Partial Retry (Open) - last attempted actions:", actions)

    # Find the approve transactions
    approve_txs = [tx for tx in actions.transactions if tx.type == TransactionType.APPROVE]
    if len(approve_txs) != 2:
        raise ValueError(
            f"Partial Retry (Open): Expected 2 approve transactions, Received: {len(approve_txs)}"
        )

    # Check if any approve transaction failed
    if any(tx.tx_status != ExecutionStatus.SUCCESS for tx in approve_txs):
        print("Partial Retry: Approve failed, restarting the state.")
        strategy.persistent_state.current_flowstatus = strategy.InternalFlowStatus.PREPARING_ACTION
        return prepare_open_position(strategy)

    # Find the open position transaction
    open_txs = [tx for tx in actions.transactions if tx.type == TransactionType.MINT]
    if not open_txs:
        raise ValueError(f"Partial Retry (Open): Expected 1 open transaction, received: {len(open_txs)}")
    open_tx = open_txs[0]

    # Check if the open position transaction failed
    if open_tx.tx_status != ExecutionStatus.SUCCESS:
        try:
            revert_reason = str(strategy.execution_manager.get_revert_reason(strategy.web3, open_tx.tx_hash))
        except Exception as e:
            print(f"Partial Retry: Failed to get revert reason. {e}")
            revert_reason = "Unknown"

        print(f"Partial Retry: Open failed with revert reason: {revert_reason}")
        if "slippage" in revert_reason.lower():
            print("Partial Retry: Slippage error detected, restarting the state.")
        elif "stf" in revert_reason.lower():
            print("Partial Retry: STF error detected, restarting the state.")
        else:
            print("Partial Retry: Unknown revert reason, restarting the state.")

        # Retry the open position
        strategy.persistent_state.current_flowstatus = strategy.InternalFlowStatus.PREPARING_ACTION
        return prepare_open_position(strategy)

    # We shouldn't reach this point
    raise ValueError("Partial Retry (Open): Unknown partial flow status.")


####################################################################################
# Shared/Helper Functions
####################################################################################
def calculate_position(
    strategy: "Strategy",
    include_last_swap_amounts: bool = True,
    use_specified_amounts: bool = False,
    amount0: int | None = 0,
    amount1: int | None = 0,
    verbose: bool = True,
) -> dict:
    """
    Calculate the optimal position for a LP strategy based on the given parameters.

    Args:
        strategy (Strategy): The strategy instance.
        include_last_swap_amounts (bool): Whether to include last swap amounts in capital calculation.
        use_specified_amounts (bool, optional): If True, use the specified `amount0` and `amount1`. Defaults to False.
        amount0 (Optional[int], optional): Specified amount of token0. Defaults to 0.
        amount1 (Optional[int], optional): Specified amount of token1. Defaults to 0.
        verbose (bool, optional): If True, prints additional debug information. Defaults to True.

    Returns:
        dict: A dictionary containing the calculated position details.

    Raises:
        ValueError: If there are issues with calculations.
        NotImplementedError: If an unsupported LP bounds calculation method is used.
    """
    if strategy.lp_bounds_calculation == LPBoundsCalculation.VOLATILITY:
        price, (price_lower, price_upper) = get_current_price_and_volatility(
            price_model=strategy.price_model,
            volatility_model=strategy.volatility_model,
            pool=strategy.pool,
            granularity=strategy.granularity,
        )

        # Re-align around the current pool price
        range_abs = abs(price_upper - price_lower)
        pool_price = strategy.uniswap_v3.get_pool_spot_rate(strategy.pool_address)
        price_lower = pool_price - (range_abs * strategy.lp_bounds_ratio)
        price_upper = pool_price + (range_abs * (1 - strategy.lp_bounds_ratio))

        if price_lower is None or price_upper is None or price_lower >= price_upper or price_lower < 0:
            raise ValueError(
                f"Invalid price bounds for the new position: [{price_lower}, {price_upper}], range={range_abs}, pool_price={pool_price}"
            )
    else:
        raise NotImplementedError("Only volatility model is supported for LP bounds calculation.")

    if not use_specified_amounts:
        # Get available capital
        amount0, amount1 = strategy.get_available_capital(include_last_swap_amounts=include_last_swap_amounts)

    if not isinstance(amount0, int) or not isinstance(amount1, int):
        raise ValueError(f"Invalid types for the new position amounts: ({type(amount0)}, {type(amount1)})")
    if amount0 < 0 or amount1 < 0:
        raise ValueError(f"Negative amounts for the new position: ({amount0}, {amount1})")

    try:
        # Calculate the possible position amounts
        calculated_amounts, calculated_range, calculated_open_slippage = (
            strategy.uniswap_v3.calculate_open_position_amount(
                token0_amount=int(amount0),
                token1_amount=int(amount1),
                lower_price=price_lower,
                upper_price=price_upper,
                pool_address=strategy.pool_address,
                slippage_spot_rate=strategy.slippage.slippage_spot_rate,
            )
        )

        if not calculated_amounts or not calculated_range or calculated_open_slippage is None:
            raise ValueError("Error while calculating the amounts to open a position.")

        if any([x < 0 for x in calculated_amounts]):
            raise ValueError("Negative calculated amounts for the new position.")

        if calculated_amounts[0] > amount0 or calculated_amounts[1] > amount1:
            raise ValueError("Calculated amounts are greater than the available amounts.")

        if calculated_open_slippage > 1 or calculated_open_slippage < 0:
            raise ValueError("Calculated open slippage is out of bounds.")

        if verbose:
            print(
                f"Position calculated amounts: initial = ({amount0}, {amount1}) vs calculated = ({calculated_amounts}); "
                f"initial open slippage = {strategy.slippage.slippage_open*100}% vs calculated open slippage = {calculated_open_slippage*100:.1f}%"
            )

        # Calculate unallocated amounts
        unallocated_amounts = (
            int(amount0 - calculated_amounts[0]),
            int(amount1 - calculated_amounts[1]),
        )

        # Return the calculated position details
        return {
            "amounts": calculated_amounts,
            "range": calculated_range,
            "unallocated": unallocated_amounts,
            "open_slippage": calculated_open_slippage,
            "model_price": price,
        }
    except Exception as e:
        raise ValueError(f"Error while calculating the amounts to open a position: {e}")
