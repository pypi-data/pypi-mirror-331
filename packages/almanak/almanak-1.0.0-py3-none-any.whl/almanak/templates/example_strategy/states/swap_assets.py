from functools import partial
from typing import TYPE_CHECKING

from almanak.enterprise_library.constants import ETH_ADDRESS
from almanak.enterprise_library.enums import ActionType, ExecutionStatus, SwapSide, TransactionType
from almanak.enterprise_library.models.action import Action
from almanak.enterprise_library.models.action_bundle import ActionBundle
from almanak.enterprise_library.models.params import SwapParams
from almanak.strategy.utils.utils import create_approve_1token_action
from .open_position import calculate_position

if TYPE_CHECKING:
    from ..strategy import Strategy


def swap_assets(strategy: "Strategy") -> ActionBundle | None:
    """
    Executes the necessary asset swaps to maintain the desired token ratio for opening a new position.

    Args:
        strategy (Strategy): The strategy instance.

    Returns:
        ActionBundle or None: An ActionBundle containing the approve and swap actions if a swap is needed,
                              or None if no swap is required.
    """

    # TODO: Add or remove any additional open position logic

    return strategy.handle_state_with_actions(
        prepare_fn=partial(prepare_swap_assets, strategy),
        validate_fn=partial(validate_swap_assets, strategy),
        sadflow_fn=partial(sadflow_swap_assets, strategy),
        next_state=strategy.State.OPEN_POSITION,
    )


def prepare_swap_assets(strategy: "Strategy") -> ActionBundle | None:
    """
    Prepares the swap actions based on the desired token ratio.

    Args:
        strategy (Strategy): The strategy instance.

    Returns:
        ActionBundle or None: An ActionBundle containing the approve and swap actions if a swap is needed,
                              or None if no swap is required.
    """
    print(f"Preparing to swap assets to achieve a {strategy.lp_bounds_ratio:.2f} token ratio.")

    if strategy.token0.address == ETH_ADDRESS or strategy.token1.address == ETH_ADDRESS:
        raise NotImplementedError("Native ETH is not supported directly; use WETH instead.")

    # Ensure we have amounts from the last closed position
    if (
        strategy.persistent_state.last_close_amounts_total is None
        or sum(strategy.persistent_state.last_close_amounts_total) == 0
    ):
        raise ValueError("No amounts from the last closed position. Cannot proceed with swapping.")

    # Get the current spot price from the pool
    spot_price = strategy.uniswap_v3.get_pool_spot_rate(strategy.pool_address)
    if not spot_price or spot_price <= 0:
        raise ValueError(f"Invalid spot price: {spot_price}")

    # Step 1: Calculate available capital (including unallocated amounts)
    amount0, amount1 = strategy.get_available_capital(include_last_swap_amounts=False)

    # Step 2: Calculate desired amounts to achieve the target ratio
    amount0_desired, amount1_desired = strategy.calculate_desired_amounts(
        amount0_initial=amount0,
        amount1_initial=amount1,
        ratio=strategy.lp_bounds_ratio,
        spot_price=spot_price,
        token0_decimals=strategy.token0.decimals,
        token1_decimals=strategy.token1.decimals,
    )
    print(
        f"Desired amounts for ratio {strategy.lp_bounds_ratio}: Token0 = {amount0_desired}, Token1 = {amount1_desired}"
    )

    # Step 3: Calculate position parameters
    position = calculate_position(
        strategy,
        include_last_swap_amounts=False,
        use_specified_amounts=True,
        amount0=amount0_desired,
        amount1=amount1_desired,
    )
    amount0_calculated, amount1_calculated = position["amounts"]

    # Step 4: Determine swap amounts
    swap_t0_for_t1, swap_amount_in, swap_amount_out = strategy.calculate_reswap_amounts(
        amount0_initial=amount0,
        amount1_initial=amount1,
        ratio=strategy.lp_bounds_ratio,
        spot_price=spot_price,
        token0_decimals=strategy.token0.decimals,
        token1_decimals=strategy.token1.decimals,
        amount0_desired=amount0_calculated,
        amount1_desired=amount1_calculated,
    )

    # Edge case handling: Check if swap amounts are too small
    min_swap_amount = 1  # Minimum acceptable swap amount in smallest units
    if (swap_amount_in * strategy.slippage.slippage_swap) < min_swap_amount:
        print("Swap amount is too small after considering slippage. Skipping swap.")
        return None
    if (swap_amount_out * strategy.slippage.slippage_swap) < min_swap_amount:
        print("Swap amount is too small after considering slippage. Skipping swap.")
        return None

    # Prepare the swap actions
    action_approve = None
    action_swap = None
    if swap_t0_for_t1 and swap_amount_in > 0:
        # Swap Token0 for Token1
        print(f"Swapping {swap_amount_in} of Token0 for {swap_amount_out} of Token1.")
        action_approve = create_approve_1token_action(
            token_address=strategy.token0.address,
            from_address=strategy.wallet_address,
            spender_address=strategy.uniswap_v3.UNISWAP_V3_ROUTER_ADDRESS,
            amount=int(swap_amount_in),
            protocol=strategy.protocol,
        )
        action_swap = Action(
            type=ActionType.SWAP,
            params=SwapParams(
                side=SwapSide.SELL,
                tokenIn=strategy.token0.address,
                tokenOut=strategy.token1.address,
                fee=strategy.fee,
                recipient=strategy.wallet_address,
                amount=int(swap_amount_in),
                slippage=strategy.slippage.slippage_swap,
            ),
            protocol=strategy.protocol,
        )
    elif not swap_t0_for_t1 and swap_amount_in > 0:
        # Swap Token1 for Token0
        print(f"Swapping {swap_amount_in} of Token1 for {swap_amount_out} of Token0.")
        action_approve = create_approve_1token_action(
            token_address=strategy.token1.address,
            from_address=strategy.wallet_address,
            spender_address=strategy.uniswap_v3.UNISWAP_V3_ROUTER_ADDRESS,
            amount=int(swap_amount_in),
            protocol=strategy.protocol,
        )
        action_swap = Action(
            type=ActionType.SWAP,
            params=SwapParams(
                side=SwapSide.SELL,
                tokenIn=strategy.token1.address,
                tokenOut=strategy.token0.address,
                fee=strategy.fee,
                recipient=strategy.wallet_address,
                amount=int(swap_amount_in),
                slippage=strategy.slippage.slippage_swap,
            ),
            protocol=strategy.protocol,
        )
    elif swap_t0_for_t1 is None and swap_amount_in == 0 and swap_amount_out == 0:
        # No swap needed
        print("No swap needed; desired token ratio already achieved.")
        return None
    else:
        raise ValueError("Invalid swap amounts calculated.")

    # Return the action bundle
    if action_approve and action_swap:
        return ActionBundle(
            actions=[action_approve, action_swap],
            chain=strategy.chain,
            network=strategy.network,
            strategy_id=strategy.id,
            config=strategy.config,
            persistent_state=strategy.persistent_state,
        )


def validate_swap_assets(strategy: "Strategy") -> bool:
    """
    Validates the swap actions and updates the strategy's state with the executed amounts.

    Args:
        strategy (Strategy): The strategy instance.

    Returns:
        bool: True if validation is successful, False otherwise.
    """
    actions = strategy.executioner_status["actions"]

    # If no actions, swapping was not needed
    if not actions:
        strategy.persistent_state.last_swap_amounts = (0, 0)
        print("No swap actions to validate.")
        return True

    if actions.status != ExecutionStatus.SUCCESS:
        raise ValueError(f"Validation failed (Swap): Expected SUCCESS, Received: {actions.status}")

    # Find the swap action
    swap_actions = [action for action in actions.actions if action.type == ActionType.SWAP]
    if len(swap_actions) != 1:
        raise ValueError(f"Validation failed (Swap): Expected 1 swap action, received: {len(swap_actions)}")
    swap_action = swap_actions[0]

    swap_executed = swap_action.get_execution_details()
    if not swap_executed:
        raise ValueError("Validation failed: No execution details found for swap action.")
    if swap_executed.type != ActionType.SWAP:
        raise ValueError(f"Validation failed: Expected SWAP action type, received: {swap_executed.type}")

    # Verify that the tokens match the strategy tokens
    tokens_in_swap = {swap_executed.tokenIn_symbol.lower(), swap_executed.tokenOut_symbol.lower()}
    tokens_in_strategy = {strategy.token0.symbol.lower(), strategy.token1.symbol.lower()}
    if tokens_in_swap != tokens_in_strategy:
        raise ValueError("Validation failed: Tokens in swap action do not match strategy tokens.")

    # Update last swap amounts based on executed swap
    if swap_executed.tokenIn_symbol.lower() == strategy.token0.symbol.lower():
        amount0 = -swap_executed.amountIn
        amount1 = swap_executed.amountOut
    else:
        amount0 = swap_executed.amountOut
        amount1 = -swap_executed.amountIn

    strategy.persistent_state.last_swap_amounts = (int(amount0), int(amount1))
    print(f"Swap executed successfully: {swap_executed}")
    return True


def sadflow_swap_assets(strategy: "Strategy") -> ActionBundle:
    """
    Handles failures during the swap assets process and decides whether to retry or adjust actions.

    Args:
        strategy (Strategy): The strategy instance.

    Returns:
        ActionBundle: The actions to retry or adjust for recovery.
    """
    actions = strategy.executioner_status["actions"]
    match actions.status:
        case ExecutionStatus.FAILED | ExecutionStatus.CANCELLED | ExecutionStatus.NOT_INCLUDED:
            return sadflow_retry(strategy)
        case ExecutionStatus.PARTIAL_EXECUTION:
            return sadflow_partial_retry(strategy)
        case ExecutionStatus.SUCCESS:
            raise ValueError("Sadflow called with SUCCESS status. Should not happen.")
        case _:
            raise ValueError(f"Invalid status for sadflow swap assets: {actions.status}")


def sadflow_retry(strategy: "Strategy") -> ActionBundle:
    """
    Retries the swap actions in case of failure.

    Args:
        strategy (Strategy): The strategy instance.

    Returns:
        ActionBundle: The actions to retry.
    """
    print("Retrying swap assets due to failure.")
    # TODO: Set your own retry logic here
    # Example:
    return prepare_swap_assets(strategy)


def sadflow_partial_retry(strategy: "Strategy") -> ActionBundle:
    """
    Handles partial execution failures and decides on recovery actions.

    Args:
        strategy (Strategy): The strategy instance.

    Returns:
        ActionBundle: The actions to retry or adjust.
    """
    # TODO: Set your own retry logic here
    # Example:

    # Only allow one retry attempt to prevent infinite loops
    if strategy.persistent_state.sadflow_actions and len(strategy.persistent_state.sadflow_actions) > 0:
        raise ValueError(
            "Partial retry already attempted. Manual intervention required."
        )

    actions = strategy.executioner_status["actions"]
    if actions.status != ExecutionStatus.PARTIAL_EXECUTION:
        raise ValueError("Expected PARTIAL_EXECUTION status for partial retry.")

    print("Handling partial execution failure for swap assets.")

    # Check if approval failed
    approve_txs = [tx for tx in actions.transactions if tx.type == TransactionType.APPROVE]
    if len(approve_txs) != 1:
        raise ValueError(f"Expected 1 approve transaction, found: {len(approve_txs)}")
    approve_tx = approve_txs[0]

    if approve_tx.tx_status != ExecutionStatus.SUCCESS:
        print("Approval transaction failed. Retrying swap assets.")
        strategy.persistent_state.current_flowstatus = strategy.InternalFlowStatus.PREPARING_ACTION
        return prepare_swap_assets(strategy)

    # Check if swap failed
    swap_txs = [tx for tx in actions.transactions if tx.type == TransactionType.SWAP]
    if len(swap_txs) != 1:
        raise ValueError(f"Expected 1 swap transaction, found: {len(swap_txs)}")
    swap_tx = swap_txs[0]

    if swap_tx.tx_status != ExecutionStatus.SUCCESS:
        # Attempt to get the revert reason
        try:
            revert_reason = strategy.execution_manager.get_revert_reason(strategy.web3, swap_tx.tx_hash)
        except Exception as e:
            print(f"Failed to retrieve revert reason: {e}")
            revert_reason = "Unknown"

        print(f"Swap transaction failed with revert reason: {revert_reason}")
        print("Retrying swap assets.")
        strategy.persistent_state.current_flowstatus = strategy.InternalFlowStatus.PREPARING_ACTION
        return prepare_swap_assets(strategy)

    # Should not reach here
    raise ValueError("Unknown failure during partial retry of swap assets.")
