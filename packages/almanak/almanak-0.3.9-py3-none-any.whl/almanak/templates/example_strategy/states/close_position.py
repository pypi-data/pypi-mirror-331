from functools import partial
from typing import TYPE_CHECKING

from almanak.enterprise_library.enums import ActionType, ExecutionStatus
from almanak.enterprise_library.models.action import Action
from almanak.enterprise_library.models.action_bundle import ActionBundle
from almanak.enterprise_library.models.params import ClosePositionParams

if TYPE_CHECKING:
    from ..strategy import Strategy


def close_position(strategy: "Strategy") -> ActionBundle | None:
    """
    Closes the current liquidity position(s) in the pool.

    This function constructs actions to close liquidity positions identified by position IDs.
    The liquidity and the fees are collected, and the NFT position is burned. The assets will
    be used in subsequent strategy steps.

    Returns:
        ActionBundle | None: An action bundle with the close position action(s).
    """
    # Handle substates if your strategy uses them
    if strategy.persistent_state.current_substate == strategy.SubState.NO_SUBSTATE:
        strategy.persistent_state.current_substate = strategy.SubState.INITIALIZATION_OPEN

    # TODO: Add or remove any additional close position logic
    
    # Handle the state with actions
    return strategy.handle_state_with_actions(
        prepare_fn=partial(prepare_close_position, strategy),
        validate_fn=partial(validate_close_position, strategy),
        sadflow_fn=partial(sadflow_close_position, strategy),
        next_state=strategy.State.SWAP_ASSETS,
    )


def prepare_close_position(strategy: "Strategy") -> ActionBundle | None:
    """
    Prepares the close position actions.

    Returns:
        ActionBundle | None: An action bundle with the close position action(s).
    """
    # Retrieve the position ID(s) from the persistent state
    position_id = strategy.persistent_state.position_id

    if position_id is None or position_id == -1:
        print("No position to close. Skipping close position.")
        return None  # If there's no position to close, return None to skip this state

    print(f"Closing position (ID: {position_id})...")

    # Create the close position action
    action_close = Action(
        type=ActionType.CLOSE_LP_POSITION,
        params=ClosePositionParams(
            position_id=position_id,
            recipient=strategy.wallet_address,
            token0=strategy.token0.address,
            token1=strategy.token1.address,
            slippage=strategy.slippage.slippage_close,
            pool_address=strategy.pool_address,
        ),
        protocol=strategy.protocol,
    )

    # Return the action bundle
    return ActionBundle(
        actions=[action_close],
        chain=strategy.chain,
        network=strategy.network,
        strategy_id=strategy.id,
        config=strategy.config,
        persistent_state=strategy.persistent_state,
    )


def validate_close_position(strategy: "Strategy") -> bool:
    """
    Validates the close position actions and retrieves the amounts from closing the position.

    Returns:
        bool: True if the close position actions were successful and the amounts were retrieved correctly.
    """
    actions = strategy.executioner_status.get("actions", None)

    if not actions:
        raise ValueError("Validation failed (Close): No actions found. Cannot skip a Close Position.")

    # Ensure the actions were successful
    if actions.status != ExecutionStatus.SUCCESS:
        raise ValueError(f"Validation failed (Close): Expected SUCCESS, Received: {actions.status}")

    # Ensure there is one action: close position
    if len(actions.actions) != 1:
        raise ValueError(f"Validation failed: Expected 1 action, Received: {len(actions.actions)}")
    if actions.actions[0].type != ActionType.CLOSE_LP_POSITION:
        raise ValueError(
            f"Validation failed: Expected action CLOSE_LP_POSITION, Received: {actions.actions[0].type}"
        )

    # Get the execution details of the close position action
    position_closed = actions.actions[0].get_execution_details()
    if not position_closed:
        raise ValueError("Validation failed: No receipt found for closing position")

    if position_closed.type != ActionType.CLOSE_LP_POSITION:
        raise ValueError(
            f"Validation failed: Expected receipt CLOSE_LP_POSITION, Received: {position_closed.type}"
        )

    # Update persistent state with amounts received from closing the position
    strategy.persistent_state.last_close_amounts_total = (
        position_closed.amount0,
        position_closed.amount1,
    )
    strategy.persistent_state.last_close_amounts_fees = (
        position_closed.fees0,
        position_closed.fees1,
    )
    strategy.persistent_state.last_close_amounts_liquidity = (
        position_closed.liquidity0,
        position_closed.liquidity1,
    )

    # Remove the position ID as it is now closed
    strategy.persistent_state.position_id = -1

    # Debug prints
    print("Position closed successfully:")
    print(position_closed)

    return True


def sadflow_close_position(strategy: "Strategy") -> ActionBundle | None:
    """
    Handles the sadflow (error handling) for the close position state.

    Returns:
        ActionBundle | None: A new action bundle to retry the close position.
    """
    actions = strategy.executioner_status.get("actions", None)
    if not actions:
        raise ValueError("Sadflow close position: No actions found.")

    match actions.status:
        case ExecutionStatus.FAILED | ExecutionStatus.CANCELLED | ExecutionStatus.NOT_INCLUDED:
            return sadflow_retry(strategy)
        case ExecutionStatus.PARTIAL_EXECUTION:
            return sadflow_partial_retry(strategy)
        case ExecutionStatus.SUCCESS:
            raise ValueError("Sadflow close position with SUCCESS status. Should not happen.")
        case _:
            raise ValueError(f"Invalid status for validate close position: {actions.status}")


def sadflow_retry(strategy: "Strategy") -> ActionBundle | None:
    """
    Handles the basic retry sadflow for close position.

    Returns:
        ActionBundle | None: A new action bundle to retry the close position.
    """
    print("Sadflow Retry: Retrying close position...")
    # TODO: Set your own retry logic here
    # Example:
    return prepare_close_position(strategy)  # Retrying the same state


def sadflow_partial_retry(strategy: "Strategy") -> ActionBundle | None:
    """
    Handles the partial retry sadflow for close position.

    Raises:
        ValueError: As partial retries are not applicable for close position with multicall.
    """
    # TODO: Set your own retry logic here
    # Example:
    # Close position with Multicall has no partial sadflow; it's all or nothing
    raise ValueError(
        "Partial Retry (Close): This should not happen with the Multicall Close Position Action."
    )
