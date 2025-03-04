from functools import partial
from typing import TYPE_CHECKING

from almanak.enterprise_library.constants import ETH_ADDRESS, get_address_by_chain_and_network
from almanak.enterprise_library.enums import ActionType, ExecutionStatus, SwapSide, TransactionType
from almanak.enterprise_library.models.action import Action
from almanak.enterprise_library.models.action_bundle import ActionBundle
from almanak.enterprise_library.models.params import ClosePositionParams, SwapParams, UnwrapParams
from almanak.strategy.utils.utils import create_approve_1token_action, to_readable

if TYPE_CHECKING:
    from ..strategy import Strategy


def teardown(strategy: "Strategy") -> ActionBundle | None:
    """
    Concludes the strategy by closing any active positions and preparing the system for a reset or shutdown.
    Leaves the system in a state where it can be cleanly initialized again.

    Returns:
        ActionBundle | None: An action bundle with the teardown actions.
    """
    # Initialize the teardown substate if necessary
    if strategy.persistent_state.current_substate == strategy.SubState.NO_SUBSTATE:
        strategy.persistent_state.current_substate = strategy.SubState.TEARDOWN_CLOSE

    # TODO: Add or remove any additional teardwon logic
    
    # Handle the teardown substates
    match strategy.persistent_state.current_substate:
        case strategy.SubState.TEARDOWN_CLOSE:
            return strategy.handle_state_with_actions(
                prepare_fn=partial(prepare_close, strategy),
                validate_fn=partial(validate_close, strategy),
                sadflow_fn=partial(sadflow_close, strategy),
                next_substate=strategy.SubState.TEARDOWN_SWAP0,
            )
        case strategy.SubState.TEARDOWN_SWAP0:
            return strategy.handle_state_with_actions(
                prepare_fn=partial(prepare_swap, strategy, 0),
                validate_fn=partial(validate_swap, strategy, 0),
                sadflow_fn=partial(sadflow_swap, strategy, 0),
                next_substate=strategy.SubState.TEARDOWN_SWAP1,
            )
        case strategy.SubState.TEARDOWN_SWAP1:
            return strategy.handle_state_with_actions(
                prepare_fn=partial(prepare_swap, strategy, 1),
                validate_fn=partial(validate_swap, strategy, 1),
                sadflow_fn=partial(sadflow_swap, strategy, 1),
                next_substate=strategy.SubState.TEARDOWN_UNWRAP,
            )
        case strategy.SubState.TEARDOWN_UNWRAP:
            return strategy.handle_state_with_actions(
                prepare_fn=partial(prepare_unwrap, strategy),
                validate_fn=partial(validate_unwrap, strategy),
                sadflow_fn=partial(sadflow_unwrap, strategy),
                next_state=strategy.State.TERMINATED,
            )
        case _:
            raise ValueError(f"Invalid Teardown SubState: {strategy.persistent_state.current_substate}")


###################################################################################
#                                TEARDOWN_CLOSE                                   #
###################################################################################
def prepare_close(strategy: "Strategy") -> ActionBundle | None:
    """
    Prepares the close position action as part of the teardown.

    Returns:
        ActionBundle | None: An action bundle with the close position action.
    """
    position_id = strategy.persistent_state.position_id

    print(f"Closing position ({position_id}) as part of Teardown...")

    if position_id is None or position_id == -1:
        print("[WARNING] No valid position ID found. Skipping Close Position.")
        return None

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

    return ActionBundle(
        actions=[action_close],
        chain=strategy.chain,
        network=strategy.network,
        strategy_id=strategy.id,
        config=strategy.config,
        persistent_state=strategy.persistent_state,
    )


def validate_close(strategy: "Strategy") -> bool:
    """
    Validates the close position action and updates the persistent state.

    Returns:
        bool: True if validation is successful.
    """
    actions = strategy.executioner_status.get("actions", None)

    if not actions:
        print("[WARNING] Teardown Close was skipped, nothing to validate.")
        strategy.persistent_state.teardown_close_amounts_total = (0, 0)
        return True

    if actions.status != ExecutionStatus.SUCCESS:
        raise ValueError(f"Validation failed (Teardown Close): Expected SUCCESS, Received: {actions.status}")

    if len(actions.actions) != 1:
        raise ValueError(f"Validation failed: Expected 1 action, Received: {len(actions.actions)}")

    if actions.actions[0].type != ActionType.CLOSE_LP_POSITION:
        raise ValueError(
            f"Validation failed: Expected CLOSE_LP_POSITION, Received: {actions.actions[0].type}"
        )

    position_closed = actions.actions[0].get_execution_details()
    if not position_closed:
        raise ValueError("Validation failed: No execution details found for close position.")

    strategy.persistent_state.teardown_close_amounts_total = (
        position_closed.amount0,
        position_closed.amount1,
    )

    # Remove the position ID as it is now closed
    strategy.persistent_state.position_id = -1

    print("Position closed successfully:")
    print(position_closed)

    return True


def sadflow_close(strategy: "Strategy") -> ActionBundle | None:
    """
    Handles the sadflow for the teardown close substate.

    Returns:
        ActionBundle | None: A new action bundle to retry the close position.
    """
    actions = strategy.executioner_status.get("actions", None)
    if not actions:
        raise ValueError("Sadflow teardown close position: No actions found.")

    match actions.status:
        case ExecutionStatus.FAILED | ExecutionStatus.CANCELLED | ExecutionStatus.NOT_INCLUDED:
            return sadflow_close_retry(strategy)
        case ExecutionStatus.PARTIAL_EXECUTION:
            return sadflow_close_partial_retry(strategy)
        case ExecutionStatus.SUCCESS:
            raise ValueError("Sadflow teardown close with SUCCESS status. Should not happen.")
        case _:
            raise ValueError(f"Invalid status for validate teardown close: {actions.status}")


def sadflow_close_retry(strategy: "Strategy") -> ActionBundle | None:
    """
    Handles the basic retry sadflow for close position.

    Returns:
        ActionBundle | None: A new action bundle to retry the close position.
    """
    print("Sadflow Retry: Retrying close position during teardown...")
    # TODO: Set your own retry logic here
    # Example:
    return prepare_close(strategy)


def sadflow_close_partial_retry(strategy: "Strategy") -> None:
    """
    Handles the partial retry sadflow for close position.

    Raises:
        ValueError: As partial retries are not applicable for close position with multicall.
    """
    # TODO: Set your own retry logic here
    # Example:
    raise ValueError(
        "Partial Retry (Teardown Close): This should not happen with the Multicall Close Position Action."
    )


###################################################################################
#                                TEARDOWN_SWAP                                    #
###################################################################################
def prepare_swap(strategy: "Strategy", token_index: int) -> ActionBundle | None:
    """
    Prepares the swap actions during teardown for the specified token index.

    Args:
        strategy (Strategy): The strategy instance.
        token_index (int): Index of the token to swap (0 or 1).

    Returns:
        ActionBundle | None: An action bundle with the swap actions.
    """
    if token_index not in [0, 1]:
        raise ValueError("token_index must be 0 or 1")

    token = strategy.token0 if token_index == 0 else strategy.token1
    funding_token = strategy.initialization.initial_funding_token

    # Calculate the total amount of the token to swap
    token_amount = (
        strategy.persistent_state.teardown_close_amounts_total[token_index]
        + strategy.persistent_state.unallocated_amounts[token_index]
    )

    if token_amount == 0:
        print(f"[WARNING] Token{token_index} has no amount to swap. Skipping swap.")
        return None

    if token.address.lower() == funding_token.lower():
        print(f"Token{token_index} is the initial funding token. No need to swap.")
        return None
    # TODO: This example assumes WETH is the only token that needs to be unwrapped
    # Remove or modify this logic if you have other tokens that need to be unwrapped
    WETH_ADDRESS = get_address_by_chain_and_network(
        chain=strategy.chain, network=strategy.network, contract_name="WETH"
    )

    if token.address.lower() == WETH_ADDRESS.lower() and funding_token == ETH_ADDRESS:
        print(f"Token{token_index} is WETH and funding token is ETH. Will unwrap later.")
        strategy.persistent_state.teardown_unwrap_target_amount += token_amount
        return None

    funding_pool_fee_tier = strategy.pooltoken.get_pool(
        strategy.initialization.initial_token0_pool
        if token_index == 0
        else strategy.initialization.initial_token1_pool
    ).fee

    print(f"Swapping back {to_readable(token_amount, token.decimals):.6f} of {token.symbol}")

    # Create approval action
    action_approve = create_approve_1token_action(
        token_address=token.address,
        from_address=strategy.wallet_address,
        spender_address=strategy.uniswap_v3.UNISWAP_V3_ROUTER_ADDRESS,
        amount=token_amount,
        protocol=strategy.protocol,
    )

    # Create swap action
    action_swap = Action(
        type=ActionType.SWAP,
        params=SwapParams(
            side=SwapSide.SELL,
            tokenIn=token.address,
            tokenOut=funding_token if funding_token != ETH_ADDRESS else WETH_ADDRESS,
            fee=funding_pool_fee_tier,
            recipient=strategy.wallet_address,
            amount=token_amount,
            slippage=strategy.slippage.slippage_swap,
        ),
        protocol=strategy.protocol,
    )

    return ActionBundle(
        actions=[action_approve, action_swap],
        chain=strategy.chain,
        network=strategy.network,
        strategy_id=strategy.id,
        config=strategy.config,
        persistent_state=strategy.persistent_state,
    )


def validate_swap(strategy: "Strategy", token_index: int) -> bool:
    """
    Validates the swap actions during teardown for the specified token index.

    Args:
        strategy (Strategy): The strategy instance.
        token_index (int): Index of the token swapped (0 or 1).

    Returns:
        bool: True if validation is successful.
    """
    actions = strategy.executioner_status.get("actions", None)

    if not actions:
        print("[WARNING] Swap was skipped, nothing to validate.")
        return True

    if actions.status != ExecutionStatus.SUCCESS:
        raise ValueError(f"Validation failed (Teardown Swap): Expected SUCCESS, Received: {actions.status}")

    # Find the swap action
    swap_actions = [action for action in actions.actions if action.type == ActionType.SWAP]
    if len(swap_actions) != 1:
        raise ValueError(f"Validation failed: Expected 1 swap action, received: {len(swap_actions)}")

    swap_executed = swap_actions[0].get_execution_details()
    if not swap_executed:
        raise ValueError("Validation failed: No execution details found for swap action.")

    if swap_executed.amountOut <= 0:
        raise ValueError("Swap amountOut is <= 0")

    # Update the persistent state with the amount received from the swap
    teardown_swap_amounts = list(strategy.persistent_state.teardown_swap_amounts)
    teardown_swap_amounts[token_index] = swap_executed.amountOut
    strategy.persistent_state.teardown_swap_amounts = tuple(teardown_swap_amounts)

    # TODO: This example assumes WETH is the only token that needs to be unwrapped
    # Remove or modify this logic if you have other tokens that need to be unwrapped

    # Check if we need to unwrap WETH to ETH
    if (
        swap_executed.tokenOut_symbol.upper() == "WETH"
        and strategy.initialization.initial_funding_token.lower() == ETH_ADDRESS.lower()
    ):
        strategy.persistent_state.teardown_unwrap_target_amount += swap_executed.amountOut

    print(f"Swap executed successfully for Token{token_index}:")
    print(swap_executed)

    return True


def sadflow_swap(strategy: "Strategy", token_index: int) -> ActionBundle | None:
    """
    Handles the sadflow for the teardown swap substate.

    Args:
        strategy (Strategy): The strategy instance.
        token_index (int): Index of the token swapped (0 or 1).

    Returns:
        ActionBundle | None: A new action bundle to retry the swap.
    """
    actions = strategy.executioner_status.get("actions", None)
    if not actions:
        raise ValueError("Sadflow teardown swap: No actions found.")

    match actions.status:
        case ExecutionStatus.FAILED | ExecutionStatus.CANCELLED | ExecutionStatus.NOT_INCLUDED:
            return sadflow_swap_retry(strategy, token_index)
        case ExecutionStatus.PARTIAL_EXECUTION:
            return sadflow_swap_partial_retry(strategy, token_index)
        case ExecutionStatus.SUCCESS:
            raise ValueError("Sadflow teardown swap with SUCCESS status. Should not happen.")
        case _:
            raise ValueError(f"Invalid status for validate teardown swap: {actions.status}")


def sadflow_swap_retry(strategy: "Strategy", token_index: int) -> ActionBundle | None:
    """
    Handles the basic retry sadflow for swap action.

    Args:
        strategy (Strategy): The strategy instance.
        token_index (int): Index of the token swapped (0 or 1).

    Returns:
        ActionBundle | None: A new action bundle to retry the swap.
    """
    print(f"Sadflow Retry: Retrying swap for Token{token_index} during teardown...")
    # TODO: Set your own retry logic here
    # Example:
    return prepare_swap(strategy, token_index)


def sadflow_swap_partial_retry(strategy: "Strategy", token_index: int) -> ActionBundle | None:
    """
    Handles the partial retry sadflow for swap action.

    Args:
        strategy (Strategy): The strategy instance.
        token_index (int): Index of the token swapped (0 or 1).

    Raises:
        ValueError: If partial retry is not applicable.
    """
    # TODO: Set your own retry logic here
    # Example:
    # Only support 1 retry attempt to avoid infinite loops
    if strategy.persistent_state.sadflow_actions and len(strategy.persistent_state.sadflow_actions) > 0:
        raise ValueError(
            "Partial Retry (Teardown Swap): Sadflow Partial Retry already attempted. Halting strategy for human intervention."
        )

    actions = strategy.executioner_status["actions"]
    if actions.status != ExecutionStatus.PARTIAL_EXECUTION:
        raise ValueError("Partial Retry (Teardown Swap): Expected PARTIAL_EXECUTION status.")

    print("Entering Partial Retry (Teardown Swap) - last attempted actions:", actions)

    # Find the approve transactions
    approve_txs = [tx for tx in actions.transactions if tx.type == TransactionType.APPROVE]
    if approve_txs and any(tx.tx_status != ExecutionStatus.SUCCESS for tx in approve_txs):
        print("Partial Retry: Approve failed, restarting the state.")
        strategy.persistent_state.current_flowstatus = strategy.InternalFlowStatus.PREPARING_ACTION
        return prepare_swap(strategy, token_index)

    # Find the swap transaction
    swap_txs = [tx for tx in actions.transactions if tx.type == TransactionType.SWAP]
    if not swap_txs or any(tx.tx_status != ExecutionStatus.SUCCESS for tx in swap_txs):
        print("Partial Retry: Swap failed, restarting the state.")
        strategy.persistent_state.current_flowstatus = strategy.InternalFlowStatus.PREPARING_ACTION
        return prepare_swap(strategy, token_index)

    # If we reach here, there is an unknown partial execution issue
    raise ValueError("Partial Retry (Teardown Swap): Unknown partial flow status.")


###################################################################################
#                               TEARDOWN_UNWRAP                                   #
###################################################################################
def prepare_unwrap(strategy: "Strategy") -> ActionBundle | None:
    """
    Prepares the unwrap action during teardown to convert WETH to ETH.

    Returns:
        ActionBundle | None: An action bundle with the unwrap action.
    """
    unwrap_target_amount = strategy.persistent_state.teardown_unwrap_target_amount

    if unwrap_target_amount <= 0:
        print("No WETH to unwrap.")
        return None

    # TODO: This example assumes WETH is the only token that needs to be unwrapped
    # Remove or modify this logic if you have other tokens that need to be unwrapped

    WETH_ADDRESS = get_address_by_chain_and_network(
        chain=strategy.chain, network=strategy.network, contract_name="WETH"
    )

    print(f"Unwrapping {to_readable(unwrap_target_amount, strategy.token1.decimals):.6f} WETH to ETH.")

    action_unwrap = Action(
        type=ActionType.UNWRAP,
        params=UnwrapParams(
            from_address=strategy.wallet_address,
            token_address=WETH_ADDRESS,
            amount=int(unwrap_target_amount),
        ),
        protocol=strategy.protocol,
    )

    return ActionBundle(
        actions=[action_unwrap],
        chain=strategy.chain,
        network=strategy.network,
        strategy_id=strategy.id,
        config=strategy.config,
        persistent_state=strategy.persistent_state,
    )


def validate_unwrap(strategy: "Strategy") -> bool:
    """
    Validates the unwrap action during teardown.

    Returns:
        bool: True if validation is successful.
    """
    actions = strategy.executioner_status.get("actions", None)

    if not actions:
        print("Unwrap was skipped, nothing to validate.")
        return True

    if actions.status != ExecutionStatus.SUCCESS:
        raise ValueError(f"Validation failed (Teardown Unwrap): Expected SUCCESS, Received: {actions.status}")

    # Find the unwrap action
    unwrap_actions = [action for action in actions.actions if action.type == ActionType.UNWRAP]
    if len(unwrap_actions) != 1:
        raise ValueError(f"Validation failed: Expected 1 unwrap action, received: {len(unwrap_actions)}")

    unwrap_executed = unwrap_actions[0].get_execution_details()
    if not unwrap_executed:
        raise ValueError("Validation failed: No execution details found for unwrap action.")

    if unwrap_executed.amount <= 0:
        raise ValueError("Unwrap amount is <= 0")

    # Update the persistent state with the amount unwrapped
    strategy.persistent_state.teardown_unwrap_amount = unwrap_executed.amount

    print("Unwrap executed successfully:")
    print(unwrap_executed)

    return True


def sadflow_unwrap(strategy: "Strategy") -> ActionBundle | None:
    """
    Handles the sadflow for the teardown unwrap substate.

    Returns:
        ActionBundle | None: A new action bundle to retry the unwrap.
    """
    actions = strategy.executioner_status.get("actions", None)
    if not actions:
        raise ValueError("Sadflow teardown unwrap: No actions found.")

    match actions.status:
        case ExecutionStatus.FAILED | ExecutionStatus.CANCELLED | ExecutionStatus.NOT_INCLUDED:
            return sadflow_unwrap_retry(strategy)
        case ExecutionStatus.PARTIAL_EXECUTION:
            return sadflow_unwrap_partial_retry(strategy)
        case ExecutionStatus.SUCCESS:
            raise ValueError("Sadflow teardown unwrap with SUCCESS status. Should not happen.")
        case _:
            raise ValueError(f"Invalid status for validate teardown unwrap: {actions.status}")


def sadflow_unwrap_retry(strategy: "Strategy") -> ActionBundle | None:
    """
    Handles the basic retry sadflow for unwrap action.

    Returns:
        ActionBundle | None: A new action bundle to retry the unwrap.
    """
    print("Sadflow Retry: Retrying unwrap during teardown...")
    # TODO: Set your own retry logic here
    # Example:
    return prepare_unwrap(strategy)


def sadflow_unwrap_partial_retry(strategy: "Strategy") -> None:
    """
    Handles the partial retry sadflow for unwrap action.

    Raises:
        ValueError: As partial retries are not applicable for unwrap action.
    """
    # TODO: Set your own retry logic here
    # Example:
    raise ValueError("Partial Retry (Teardown Unwrap): This should not happen with only 1 transaction.")
