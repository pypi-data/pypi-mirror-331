from datetime import datetime, timezone
from functools import partial
from typing import TYPE_CHECKING

from almanak.enterprise_library.constants import ETH_ADDRESS, get_address_by_chain_and_network
from almanak.enterprise_library.enums import ActionType, ExecutionStatus, SwapSide
from almanak.enterprise_library.models.action import Action
from almanak.enterprise_library.models.action_bundle import ActionBundle
from almanak.enterprise_library.models.params import (
    OpenPositionParams,
    SwapParams,
    WrapParams,
)
from almanak.strategy.utils.utils import (
    create_approve_1token_action,
    create_approve_2tokens_actions,
    to_readable,
)
from .open_position import calculate_position

if TYPE_CHECKING:
    from ..strategy import Strategy


def initialization(strategy: "Strategy") -> ActionBundle:
    """
    Initializes the strategy by preparing assets and opening positions.

    The initialization process may involve swapping assets, wrapping ETH, and opening liquidity positions.
    It operates in several substates to manage the sequence of actions.

    Returns:
        ActionBundle: An action bundle representing the actions required to initialize
        the strategy, or None if no actions are required.

    Notes:
        - This method should only be called at the start of the strategy lifecycle.
        - The process is divided into substates to handle complex initialization steps.
    """
    if strategy.persistent_state.current_substate is None:
        raise ValueError("Initialization SubState is None. This should not happen.")

    # Initialize substates if starting fresh
    if strategy.persistent_state.current_substate == strategy.SubState.NO_SUBSTATE:
        strategy.persistent_state.current_substate = strategy.SubState.INITIALIZATION_SWAP0

    # TODO: Add or remove any additional initialization logic

    # Handle each substate
    match strategy.persistent_state.current_substate:
        case strategy.SubState.INITIALIZATION_SWAP0:
            # Log a snapshot before starting the initialization
            strategy.log_snapshot(block_number=0)
            return strategy.handle_state_with_actions(
                prepare_fn=partial(prepare_swap, strategy, 0),
                validate_fn=partial(validate_swap, strategy, 0),
                sadflow_fn=partial(sadflow_swap, strategy, 0),
                next_state=None,
                next_substate=strategy.SubState.INITIALIZATION_SWAP1,
            )
        case strategy.SubState.INITIALIZATION_SWAP1:
            return strategy.handle_state_with_actions(
                prepare_fn=partial(prepare_swap, strategy, 1),
                validate_fn=partial(validate_swap, strategy, 1),
                sadflow_fn=partial(sadflow_swap, strategy, 1),
                next_state=None,
                next_substate=strategy.SubState.INITIALIZATION_OPEN,
            )
        case strategy.SubState.INITIALIZATION_OPEN:
            return strategy.handle_state_with_actions(
                prepare_fn=partial(prepare_open, strategy),
                validate_fn=partial(validate_open, strategy),
                sadflow_fn=partial(sadflow_open, strategy),
                next_state=strategy.State.CHECK_FOR_REBALANCE,
            )
        case _:
            raise ValueError(f"Invalid Initialization SubState: {strategy.persistent_state.current_substate}")


###################################################################################
#                           INITIALIZATION_SWAP0/1                                #
###################################################################################
def prepare_swap(strategy: "Strategy", token_index: int) -> ActionBundle:
    """
    Prepares the swap actions for the specified token index (0 or 1).

    Args:
        strategy (Strategy): The strategy instance.
        token_index (int): The index of the token to prepare the swap for (0 or 1).

    Returns:
        ActionBundle or None: An ActionBundle containing the actions required for the swap,
                              or None if no swap is needed.
    """
    if token_index not in [0, 1]:
        raise ValueError("token_index must be 0 or 1")

    value_USD = float(strategy.initialization.initial_position_value_USD / 2)
    print(
        f"Initializing strategy for Token{token_index} with {value_USD}/{strategy.initialization.initial_position_value_USD} USD."
    )

    funding_token = strategy.initialization.initial_funding_token
    wrap_needed = funding_token == ETH_ADDRESS

    token = strategy.token0 if token_index == 0 else strategy.token1
    init_amount = int(strategy.persistent_state.initialize_token_amounts[token_index])

    if init_amount < 0:
        raise ValueError(f"Initialization token{token_index} amount can't be negative.")
    elif init_amount > 0:
        print(f"Initialization token{token_index} amount is already prepared: {init_amount}")
        return None
    else:
        # Determine required amount
        funding_amount = (
            strategy.initialization.initial_funding_token0_amount
            if token_index == 0
            else strategy.initialization.initial_funding_token1_amount
        )
        required_amount = strategy.get_initialize_amount(token, funding_amount, value_USD)
        print(f"Token{token_index} Required Amount: {required_amount} {token.symbol}")

        # TODO: This example assumes WETH
        WETH_ADDRESS = get_address_by_chain_and_network(
            chain=strategy.chain, network=strategy.network, contract_name="WETH"
        )

        if required_amount <= 0:
            print(f"Token{token_index} required amount is <= 0. No need to swap.")
            _initialize_token_amounts = list(strategy.persistent_state.initialize_token_amounts)
            _initialize_token_amounts[token_index] = int(funding_amount)
            strategy.persistent_state.initialize_token_amounts = tuple(_initialize_token_amounts)
            return None
        elif token.address.lower() == funding_token.lower():
            print(f"Token{token_index} is the initial funding token. No need to swap.")
            _initialize_token_amounts = list(strategy.persistent_state.initialize_token_amounts)
            _initialize_token_amounts[token_index] = int(required_amount + funding_amount)
            strategy.persistent_state.initialize_token_amounts = tuple(_initialize_token_amounts)
            return None
        elif token.address.lower() == WETH_ADDRESS.lower() and wrap_needed:
            print(
                f"Token{token_index} is WETH and funding token is ETH. Wrapping required."
            )
            action_wrap = Action(
                type=ActionType.WRAP,
                params=WrapParams(
                    from_address=strategy.wallet_address,
                    amount=int(required_amount),
                ),
                protocol=strategy.protocol,
            )
            return ActionBundle(
                actions=[action_wrap],
                chain=strategy.chain,
                network=strategy.network,
                strategy_id=strategy.id,
                config=strategy.config,
                persistent_state=strategy.persistent_state,
            )
        else:
            # Swap is needed
            funding_pool_fee_tier = strategy.pooltoken.get_pool(
                strategy.initialization.initial_token0_pool
                if token_index == 0
                else strategy.initialization.initial_token1_pool
            ).fee

            # Get quote for swap
            amountIn = strategy.uniswap_v3.quoteExactOutputSingle(
                funding_token if not wrap_needed else WETH_ADDRESS,
                token.address,
                funding_pool_fee_tier,
                int(required_amount),
                0,
            )

            action_wrap = None
            if wrap_needed:
                action_wrap = Action(
                    type=ActionType.WRAP,
                    params=WrapParams(
                        from_address=strategy.wallet_address,
                        amount=int(amountIn),
                    ),
                    protocol=strategy.protocol,
                )

            # Approve before swapping
            action_approve = create_approve_1token_action(
                token_address=funding_token if not wrap_needed else WETH_ADDRESS,
                from_address=strategy.wallet_address,
                spender_address=strategy.uniswap_v3.UNISWAP_V3_ROUTER_ADDRESS,
                amount=amountIn,
                protocol=strategy.protocol,
            )

            # Create swap action
            action_swap = Action(
                type=ActionType.SWAP,
                params=SwapParams(
                    side=SwapSide.SELL,  # Adjust as needed
                    tokenIn=funding_token if not wrap_needed else WETH_ADDRESS,
                    tokenOut=token.address,
                    fee=funding_pool_fee_tier,
                    recipient=strategy.wallet_address,
                    amount=amountIn,
                    slippage=strategy.slippage.slippage_swap,
                ),
                protocol=strategy.protocol,
            )

            actions = (
                [action_wrap, action_approve, action_swap] if wrap_needed else [action_approve, action_swap]
            )

            return ActionBundle(
                actions=actions,
                chain=strategy.chain,
                network=strategy.network,
                strategy_id=strategy.id,
                config=strategy.config,
                persistent_state=strategy.persistent_state,
            )


def validate_swap(strategy: "Strategy", token_index: int) -> bool:
    """
    Validates the swap actions and updates the initialized token amounts.

    Args:
        strategy (Strategy): The strategy instance.
        token_index (int): The index of the token to validate the swap for (0 or 1).

    Returns:
        bool: True if validation is successful, False otherwise.
    """
    if token_index not in [0, 1]:
        raise ValueError("token_index must be 0 or 1")

    actions = strategy.executioner_status["actions"]

    # If no actions, swapping was not needed
    if not actions:
        print("Swap and Wrap were skipped, nothing to validate.")
        # Log swap metrics if needed
        # TODO: Implement logging if required
        return True

    if actions.status != ExecutionStatus.SUCCESS:
        raise ValueError(
            f"Validation failed (Initialization Swap{token_index}): Expected SUCCESS, Received: {actions.status}"
        )

    # Handle wrap and swap actions
    wrap_action = None
    wrap_executed = None
    wrap_actions = [action for action in actions.actions if action.type == ActionType.WRAP]
    if len(wrap_actions) > 1:
        raise ValueError(
            f"Validation failed (Init Swap{token_index}): Expected 0 or 1 wrap action, received: {len(wrap_actions)}"
        )
    if wrap_actions:
        wrap_action = wrap_actions[0]
        wrap_executed = wrap_action.get_execution_details()
        if not wrap_executed:
            raise ValueError("Validation failed: No execution details for wrap action.")

        _initialize_token_amounts = list(strategy.persistent_state.initialize_token_amounts)
        _initialize_token_amounts[token_index] = int(wrap_executed.amount)
        strategy.persistent_state.initialize_token_amounts = tuple(_initialize_token_amounts)

    swap_action = None
    swap_executed = None
    swap_actions = [action for action in actions.actions if action.type == ActionType.SWAP]
    if swap_actions:
        swap_action = swap_actions[0]
        swap_executed = swap_action.get_execution_details()
        if not swap_executed:
            raise ValueError("Validation failed: No execution details for swap action.")

        _initialize_token_amounts = list(strategy.persistent_state.initialize_token_amounts)
        _initialize_token_amounts[token_index] = int(swap_executed.amountOut)
        strategy.persistent_state.initialize_token_amounts = tuple(_initialize_token_amounts)

    # Log swap metrics if needed
    # TODO: Implement logging if required

    return True


def sadflow_swap(strategy: "Strategy", token_index: int) -> ActionBundle:
    """
    Handles sadflow for swap actions in case of failures.

    Args:
        strategy (Strategy): The strategy instance.
        token_index (int): The index of the token (0 or 1).

    Returns:
        ActionBundle: The actions to retry or adjust the swap.
    """
    actions = strategy.executioner_status["actions"]
    match actions.status:
        case ExecutionStatus.FAILED | ExecutionStatus.CANCELLED | ExecutionStatus.NOT_INCLUDED:
            return sadflow_swap_retry(strategy, token_index)
        case ExecutionStatus.PARTIAL_EXECUTION:
            return sadflow_swap_partial_retry(strategy, token_index)
        case ExecutionStatus.SUCCESS:
            raise ValueError("Sadflow swap called with SUCCESS status. Should not happen.")
        case _:
            raise ValueError(f"Invalid status for sadflow swap: {actions.status}")


def sadflow_swap_retry(strategy: "Strategy", token_index: int) -> ActionBundle:
    """
    Retries the swap action in case of failure.

    Args:
        strategy (Strategy): The strategy instance.
        token_index (int): The index of the token (0 or 1).

    Returns:
        ActionBundle: The actions to retry.
    """
    print(f"Retrying swap for Token{token_index}.")
    # TODO: Set your own retry logic here
    # Example:
    return prepare_swap(strategy, token_index)


def sadflow_swap_partial_retry(strategy: "Strategy", token_index: int) -> ActionBundle:
    """
    Handles partial retry for swap actions in case of partial execution.

    Args:
        strategy (Strategy): The strategy instance.
        token_index (int): The index of the token (0 or 1).

    Returns:
        ActionBundle: The adjusted actions to retry.
    """
    print(f"Handling partial retry for swap of Token{token_index}.")
    # TODO: Set your own retry logic here
    # Example:
    return prepare_swap(strategy, token_index)


###################################################################################
#                              INITIALIZATION_OPEN                                #
###################################################################################
def prepare_open(strategy: "Strategy") -> ActionBundle:
    """
    Prepares the open position actions.

    Args:
        strategy (Strategy): The strategy instance.

    Returns:
        ActionBundle: The actions required to open the position.
    """
    amount0 = strategy.persistent_state.initialize_token_amounts[0]
    amount1 = strategy.persistent_state.initialize_token_amounts[1]

    if amount0 <= 0 and amount1 <= 0:
        raise ValueError(
            f"Invalid state for opening a new position during initialization. Amount0: {amount0}, Amount1: {amount1}"
        )

    # Calculate the new position amounts and price bounds
    position = calculate_position(
        strategy,
        amount0=amount0,
        amount1=amount1,
        use_specified_amounts=True,
    )
    amount0, amount1 = position["amounts"]
    price_lower, price_upper = position["range"]
    open_slippage = max(strategy.slippage.slippage_open, position.get("open_slippage", 0))

    print(
        f"New Position (expected): {to_readable(amount0, strategy.token0.decimals):.6f} {strategy.token0.symbol} | {to_readable(amount1, strategy.token1.decimals):.6f} {strategy.token1.symbol} [{price_lower}, {price_upper}]"
    )

    # Approve tokens before opening position
    action_approve0, action_approve1 = create_approve_2tokens_actions(
        token0_address=strategy.token0.address,
        token1_address=strategy.token1.address,
        from_address=strategy.wallet_address,
        spender_address=strategy.uniswap_v3.UNISWAP_V3_POSITION_MANAGER_ADDRESS,
        amount0=int(amount0),
        amount1=int(amount1),
        protocol=strategy.protocol,
    )

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

    return ActionBundle(
        actions=[action_approve0, action_approve1, action_open],
        chain=strategy.chain,
        network=strategy.network,
        strategy_id=strategy.id,
        config=strategy.config,
        persistent_state=strategy.persistent_state,
    )


def validate_open(strategy: "Strategy") -> bool:
    """
    Validates the open position actions and updates the strategy's state.

    Args:
        strategy (Strategy): The strategy instance.

    Returns:
        bool: True if validation is successful, False otherwise.
    """
    actions = strategy.executioner_status["actions"]

    if not actions:
        raise ValueError("Validation failed (Init Open): No actions found.")

    if actions.status != ExecutionStatus.SUCCESS:
        raise ValueError(f"Validation failed (Init Open): Expected SUCCESS, Received: {actions.status}")

    if len(actions.actions) != 3:
        raise ValueError(
            f"Validation failed (Init Open): Expected 3 actions, Received: {len(actions.actions)}"
        )
    if actions.actions[2].type != ActionType.OPEN_LP_POSITION:
        raise ValueError(
            f"Validation failed: Expected action[2] OPEN_LP_POSITION, Received: {actions.actions[2].type}"
        )

    position_opened = actions.actions[2].get_execution_details()
    if not position_opened:
        raise ValueError("Validation failed (Init Open): No execution details for open position")

    strategy.persistent_state.position_id = position_opened.position_id

    if not actions.executed_at:
        raise ValueError("Validation failed (Init Open): No executed_at timestamp found.")

    strategy.persistent_state.last_rebalance_time = datetime.fromtimestamp(actions.executed_at, timezone.utc)
    strategy.persistent_state.last_check_for_rebalance_time = strategy.persistent_state.last_rebalance_time

    # Calculate unallocated amounts
    amount0 = strategy.persistent_state.initialize_token_amounts[0]
    amount1 = strategy.persistent_state.initialize_token_amounts[1]
    unallocated_amount0 = amount0 - position_opened.amount0
    unallocated_amount1 = amount1 - position_opened.amount1
    strategy.persistent_state.last_open_unallocated_amounts = (unallocated_amount0, unallocated_amount1)

    if any(x < 0 for x in strategy.persistent_state.last_open_unallocated_amounts):
        raise ValueError("Negative unallocated assets after opening a position.")

    print("Position opened successfully.")

    # Log open metrics if needed
    # TODO: Implement logging if required

    # Update initialization status
    strategy.persistent_state.initialized = True

    return True


def sadflow_open(strategy: "Strategy") -> ActionBundle:
    """
    Handles sadflow for opening positions in case of failures.

    Args:
        strategy (Strategy): The strategy instance.

    Returns:
        ActionBundle: The actions to retry or adjust the open position.
    """
    actions = strategy.executioner_status["actions"]
    match actions.status:
        case ExecutionStatus.FAILED | ExecutionStatus.CANCELLED | ExecutionStatus.NOT_INCLUDED:
            return sadflow_open_retry(strategy)
        case ExecutionStatus.PARTIAL_EXECUTION:
            return sadflow_open_partial_retry(strategy)
        case ExecutionStatus.SUCCESS:
            raise ValueError("Sadflow open called with SUCCESS status. Should not happen.")
        case _:
            raise ValueError(f"Invalid status for sadflow open: {actions.status}")


def sadflow_open_retry(strategy: "Strategy") -> ActionBundle:
    """
    Retries the open position action in case of failure.

    Args:
        strategy (Strategy): The strategy instance.

    Returns:
        ActionBundle: The actions to retry.
    """
    print("Retrying open position.")
    # TODO: Set your own retry logic here
    # Example:
    return prepare_open(strategy)


def sadflow_open_partial_retry(strategy: "Strategy") -> ActionBundle:
    """
    Handles partial retry for opening positions in case of partial execution.

    Args:
        strategy (Strategy): The strategy instance.

    Returns:
        ActionBundle: The adjusted actions to retry.
    """
    print("Handling partial retry for open position.")
    # TODO: Set your own retry logic here
    # Example:
    return prepare_open(strategy)
