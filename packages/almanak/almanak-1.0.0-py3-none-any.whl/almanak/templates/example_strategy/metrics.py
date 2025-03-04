import time
from datetime import datetime, timezone
from pprint import pprint
from typing import TYPE_CHECKING, Optional

from almanak.enterprise_library.enums import ActionType
from almanak.enterprise_library.metrics.metrics_agg import MetricAggType, MetricsAggTable
from almanak.enterprise_library.models.receipt import Receipt
from almanak.strategy.utils.price_volatility import get_current_price

if TYPE_CHECKING:
    from ..strategy import Strategy

def log_strategy_balance_metrics(strategy: "Strategy", action_bundle_id: str):
    """
    Logs the strategy's balance metrics after executing actions.

    Args:
        strategy (Strategy): The strategy instance.
        action_bundle_id (str): The ID of the action bundle that was executed.

    Notes:
        - Fetches executed actions and computes the changes in token balances.
        - Retrieves current prices for tokens to include in the metrics.
        - Logs the metrics using the strategy's metrics aggregator.
    """
    try:
        details = {}
        executioner_state = strategy.load_executioner_state(action_bundle_id)
        if executioner_state and executioner_state["actions"]:

            # Only consider successful actions with execution details
            actions = [action for action in executioner_state["actions"].actions if action.execution_details]
            for action in actions:
                eth_delta, weth_delta, token0_delta, token1_delta = 0, 0, 0, 0
                token0_unallocated, token1_unallocated = 0, 0

                match action.type:
                    case ActionType.SWAP:
                        swap_executed = action.execution_details
                        # TODO: Adjust token delta calculations based on your token symbols
                        # Example:
                        # if swap_executed.tokenIn_symbol.lower() == strategy.token0.symbol.lower():
                        #     token0_delta = int(swap_executed.amountIn * -1)
                        # ...
                    case ActionType.CLOSE_LP_POSITION:
                        position_closed = action.execution_details
                        # TODO: Update token deltas and unallocated amounts
                    case ActionType.OPEN_LP_POSITION:
                        position_opened = action.execution_details
                        # TODO: Update token deltas and unallocated amounts
                    case ActionType.WRAP:
                        # TODO: Handle wrap action deltas
                        pass
                    case ActionType.UNWRAP:
                        # TODO: Handle unwrap action deltas
                        pass
                    case _:
                        # Actions that don't affect balances (e.g., Complete)
                        continue

                # TODO: Add 
                positions_balance = {}
                # Example: Update positions_balance with current positions and amounts
                # position_ids = [strategy.persistent_state.position_id]
                # for pos_id in position_ids:
                #     if pos_id is None or pos_id == -1:
                #         continue
                #     pos_info = strategy.uniswap_v3.get_position_info(pos_id)
                #     amount0, amount1 = strategy.uniswap_v3.get_lp_token_amounts(strategy.pool_address, pos_id)
                #     unclaimed0, unclaimed1 = strategy.uniswap_v3.get_unclaimed_fees(strategy.pool_address, pos_id)
                #     positions_balance[pos_id] = {
                #         "token0": {...},
                #         "token1": {...},
                #         "info": pos_info,
                #     }

                details = {
                    "action": {
                        "type": action.type.value,
                        "id": str(action.id),
                    },
                    "native": {
                        "ETH_delta": eth_delta,
                        "WETH_delta": weth_delta,
                    },
                    "tokens": {
                        strategy.token0.symbol: {
                            "address": strategy.token0.address,
                            "decimals": strategy.token0.decimals,
                            "unallocated": token0_unallocated,
                            "delta": token0_delta,
                            "price_in_USD": None,
                            "price_in_ETH": None,
                        },
                        strategy.token1.symbol: {
                            "address": strategy.token1.address,
                            "decimals": strategy.token1.decimals,
                            "unallocated": token1_unallocated,
                            "delta": token1_delta,
                            "price_in_USD": None,
                            "price_in_ETH": None,
                        },
                    },
                    "positions": positions_balance,
                }

                # Fetch current prices for tokens
                tokens = [strategy.token0, strategy.token1]
                for token in tokens:
                    for quote_currency in ["USD", "ETH"]:
                        try:
                            price = get_current_price(
                                data_source=strategy.price_model.data_source,
                                pool=strategy.pool,
                                base_symbol=token.symbol,
                                quote_symbol=quote_currency,
                                chain=strategy.chain,
                            )
                            if quote_currency == "USD":
                                details["tokens"][token.symbol]["price_in_USD"] = price
                            elif quote_currency == "ETH":
                                details["tokens"][token.symbol]["price_in_ETH"] = price
                        except Exception as e:
                            print(f"[WARNING] Failed to fetch price for {token.symbol} in {quote_currency}: {e}")

                # Debug print
                print("============ [DEBUG] Updated Strategy Balance Metrics ============")
                pprint(details)
                print("===================================================================")

                # Add the metrics to the aggregator table
                strategy.metrics_agg_handler.add_metric(
                    MetricsAggTable(
                        metric_type=MetricAggType.STRATEGY_BALANCE.value,
                        strategy_id=strategy.id,
                        wallet_address=strategy.wallet_address,
                        details=details,
                        action_id=str(action.id),
                        bundle_id=str(action.bundle_id),
                        block_number=action.execution_details.block_number,
                    )
                )
        else:
            print(f"No executioner state for ActionBundle ID: {action_bundle_id}.")
    except Exception as e:
        print(f"Error loading executioner state in log_strategy_balance_metrics: {e}")

def log_swap_metrics(
    strategy: "Strategy",
    token_index: int,
    swap_executed: Optional[Receipt],
    swap_action_id: Optional[str],
    wrap_executed: Optional[Receipt],
    wrap_action_id: Optional[str],
    bundle_id: str,
    context: str,
):
    """
    Logs metrics for swap actions during initialization or teardown.

    Args:
        strategy (Strategy): The strategy instance.
        token_index (int): Index of the token (0 or 1).
        swap_executed (Optional[Receipt]): The executed swap receipt.
        swap_action_id (Optional[str]): The action ID for the swap.
        wrap_executed (Optional[Receipt]): The executed wrap receipt.
        wrap_action_id (Optional[str]): The action ID for the wrap.
        bundle_id (str): The bundle ID.
        context (str): Context of the swap ("initialization" or "teardown").
    """
    try:
        token_in = strategy.get_token(swap_executed.tokenIn_symbol).to_dict() if swap_executed else None
        token_out = strategy.get_token(swap_executed.tokenOut_symbol).to_dict() if swap_executed else None
        funding_token = strategy.get_funding_token().to_dict()
    except Exception as e:
        print(f"[WARNING] Failed to get token details while logging {context} swap metrics: {e}")
        token_in = None
        token_out = None
        funding_token = None

    details = {
        f"swap_for_token{token_index}": {
            "wrap": wrap_executed.amount if wrap_executed else None,
            "side": str(swap_executed.side.value) if swap_executed else None,
            "tokenIn": token_in,
            "tokenOut": token_out,
            "amountOut": swap_executed.amountOut if swap_executed else None,
            "amountIn": swap_executed.amountIn if swap_executed else None,
            "target_amount_in_USD": strategy.initialization.initial_position_value_USD / 2,
            "funding_token": funding_token,
            "swap_action_id": str(swap_action_id) if swap_action_id else None,
            "wrap_action_id": str(wrap_action_id) if wrap_action_id else None,
        }
    }

    block_number = (
        swap_executed.block_number if swap_executed else wrap_executed.block_number if wrap_executed else None
    )

    if context.lower() == "initialization":
        log_initialization_metrics(
            strategy=strategy,
            init_details=details,
            substate=True,
            action_id=swap_action_id or wrap_action_id,
            bundle_id=bundle_id,
            block_number=block_number,
        )
    elif context.lower() == "teardown":
        log_teardown_metrics(
            strategy=strategy,
            teardown_details=details,
            substate=True,
            action_id=swap_action_id or wrap_action_id,
            bundle_id=bundle_id,
            block_number=block_number,
        )
    else:
        raise ValueError(f"Unknown context for logging swap metrics: {context}")


def log_open_metrics(
    strategy: "Strategy",
    position_opened: Receipt,
    action_id: str,
    bundle_id: str,
    context: str,
):
    """
    Logs metrics for open position actions.

    Args:
        strategy (Strategy): The strategy instance.
        position_opened (Receipt): The executed open position receipt.
        action_id (str): The action ID for the open position.
        bundle_id (str): The bundle ID.
        context (str): Context of the open position ("initialization").
    """
    try:
        token0 = strategy.get_token(position_opened.token0_symbol).to_dict() if position_opened else None
        token1 = strategy.get_token(position_opened.token1_symbol).to_dict() if position_opened else None
    except Exception as e:
        print(f"[WARNING] Failed to get token details while logging {context} open metrics: {e}")
        token0 = None
        token1 = None

    details = {
        "open": {
            "token0": token0,
            "token1": token1,
            "amount0": position_opened.amount0,
            "amount1": position_opened.amount1,
            "bound_tick_lower": position_opened.bound_tick_lower,
            "bound_tick_upper": position_opened.bound_tick_upper,
            "bound_price_lower": position_opened.bound_price_lower,
            "bound_price_upper": position_opened.bound_price_upper,
            "position_id": position_opened.position_id,
            "pool_tick": position_opened.pool_tick,
            "pool_spot_rate": position_opened.pool_spot_rate,
            "open_action_id": str(action_id),
        }
    }

    if context.lower() == "initialization":
        log_initialization_metrics(
            strategy=strategy,
            init_details=details,
            substate=True,
            action_id=action_id,
            bundle_id=bundle_id,
            block_number=position_opened.block_number,
        )
    else:
        raise ValueError(f"Unknown context for logging open metrics: {context}")


def log_close_metrics(
    strategy: "Strategy",
    position_closed: Receipt,
    action_id: str,
    bundle_id: str,
    context: str,
):
    """
    Logs metrics for close position actions.

    Args:
        strategy (Strategy): The strategy instance.
        position_closed (Receipt): The executed close position receipt.
        action_id (str): The action ID for the close position.
        bundle_id (str): The bundle ID.
        context (str): Context of the close position ("teardown").
    """
    try:
        token0 = strategy.get_token(position_closed.token0_symbol).to_dict() if position_closed else None
        token1 = strategy.get_token(position_closed.token1_symbol).to_dict() if position_closed else None
    except Exception as e:
        print(f"[WARNING] Failed to get token details while logging {context} close metrics: {e}")
        token0 = None
        token1 = None

    details = {
        "close": {
            "token0": token0,
            "token1": token1,
            "amount0": position_closed.amount0,
            "amount1": position_closed.amount1,
            "liquidity0": position_closed.liquidity0,
            "liquidity1": position_closed.liquidity1,
            "fees0": position_closed.fees0,
            "fees1": position_closed.fees1,
            "position_id": position_closed.position_id,
            "pool_tick": position_closed.pool_tick,
            "pool_spot_rate": position_closed.pool_spot_rate,
            "close_action_id": str(action_id),
        }
    }

    if context.lower() == "teardown":
        log_teardown_metrics(
            strategy=strategy,
            teardown_details=details,
            substate=True,
            action_id=action_id,
            bundle_id=bundle_id,
            block_number=position_closed.block_number,
        )
    else:
        raise ValueError(f"Unknown context for logging close metrics: {context}")


def log_unwrap_metrics(
    strategy: "Strategy",
    unwrap: Receipt,
    action_id: str,
    bundle_id: str,
    context: str,
):
    """
    Logs metrics for unwrap actions during teardown.

    Args:
        strategy (Strategy): The strategy instance.
        unwrap (Receipt): The executed unwrap receipt.
        action_id (str): The action ID for the unwrap.
        bundle_id (str): The bundle ID.
        context (str): Context of the unwrap ("teardown").
    """
    token = strategy.get_token("WETH").to_dict() if unwrap else None
    details = {
        "unwrap": {
            "token": token,
            "amount": unwrap.amount,
            "unwrap_action_id": str(action_id),
        }
    }

    if context.lower() == "teardown":
        log_teardown_metrics(
            strategy=strategy,
            teardown_details=details,
            substate=True,
            action_id=action_id,
            bundle_id=bundle_id,
            block_number=unwrap.block_number,
        )
    else:
        raise ValueError(f"Unknown context for logging unwrap metrics: {context}")


def log_initialization_metrics(
    strategy: "Strategy",
    init_details: dict,
    substate: bool,
    action_id: Optional[str] = None,
    bundle_id: Optional[str] = None,
    block_number: Optional[int] = None,
):
    """
    Aggregates and logs initialization metrics.

    Args:
        strategy (Strategy): The strategy instance.
        init_details (dict): Details of the initialization substate.
        substate (bool): Whether this is a substate or final aggregation.
        action_id (Optional[str]): Action ID.
        bundle_id (Optional[str]): Bundle ID.
        block_number (Optional[int]): Block number of the action.
    """
    if substate:
        # Log substate metrics
        strategy.metrics_agg_handler.add_metric(
            MetricsAggTable(
                metric_type=MetricAggType.INITIALIZATION.value,
                strategy_id=strategy.id,
                wallet_address=strategy.wallet_address,
                details={"substate": init_details},
                action_id=str(action_id) if action_id else datetime.now(timezone.utc).isoformat(),
                bundle_id=str(bundle_id) if bundle_id else datetime.now(timezone.utc).isoformat(),
                block_number=block_number,
            )
        )
    else:
        # Aggregate substate metrics
        init_substates = strategy.metrics_agg_handler.get_metrics_agg(
            strategy_id=strategy.id,
            metric_type=MetricAggType.INITIALIZATION,
            wallet_address=strategy.wallet_address,
        )

        initialization_agg = {}
        substate_keys = {"swap_for_token0", "swap_for_token1", "open"}

        # TODO: Aggregate the substate metrics into initialization_agg
        # Example:
        # for entry in init_substates:
        #     substate = entry.details.get("substate", {})
        #     for key in substate_keys:
        #         if key in substate:
        #             initialization_agg[key] = substate[key]
        #     ...

        # Log the aggregated initialization metrics
        strategy.metrics_agg_handler.add_metric(
            MetricsAggTable(
                metric_type=MetricAggType.INITIALIZATION.value,
                strategy_id=strategy.id,
                wallet_address=strategy.wallet_address,
                details={"aggregated": initialization_agg},
                action_id=datetime.now(timezone.utc).isoformat(),
                bundle_id=datetime.now(timezone.utc).isoformat(),
                block_number=None,
            )
        )


def log_teardown_metrics(
    strategy: "Strategy",
    teardown_details: dict,
    substate: bool,
    action_id: Optional[str] = None,
    bundle_id: Optional[str] = None,
    block_number: Optional[int] = None,
):
    """
    Aggregates and logs teardown metrics.

    Args:
        strategy (Strategy): The strategy instance.
        teardown_details (dict): Details of the teardown substate.
        substate (bool): Whether this is a substate or final aggregation.
        action_id (Optional[str]): Action ID.
        bundle_id (Optional[str]): Bundle ID.
        block_number (Optional[int]): Block number of the action.
    """
    if substate:
        # Log substate metrics
        strategy.metrics_agg_handler.add_metric(
            MetricsAggTable(
                metric_type=MetricAggType.TEARDOWN.value,
                strategy_id=strategy.id,
                wallet_address=strategy.wallet_address,
                details={"substate": teardown_details},
                action_id=str(action_id) if action_id else datetime.now(timezone.utc).isoformat(),
                bundle_id=str(bundle_id) if bundle_id else datetime.now(timezone.utc).isoformat(),
                block_number=block_number,
            )
        )
    else:
        # Aggregate substate metrics
        teardown_substates = strategy.metrics_agg_handler.get_metrics_agg(
            strategy_id=strategy.id,
            metric_type=MetricAggType.TEARDOWN,
            wallet_address=strategy.wallet_address,
        )

        teardown_agg = {}
        substate_keys = {"swap_for_token0", "swap_for_token1", "close", "unwrap"}

        # TODO: Aggregate the substate metrics into teardown_agg
        # Example:
        # for entry in teardown_substates:
        #     substate = entry.details.get("substate", {})
        #     for key in substate_keys:
        #         if key in substate:
        #             teardown_agg[key] = substate[key]
        #     ...

        # Log the aggregated teardown metrics
        strategy.metrics_agg_handler.add_metric(
            MetricsAggTable(
                metric_type=MetricAggType.TEARDOWN.value,
                strategy_id=strategy.id,
                wallet_address=strategy.wallet_address,
                details={"aggregated": teardown_agg},
                action_id=datetime.now(timezone.utc).isoformat(),
                bundle_id=datetime.now(timezone.utc).isoformat(),
                block_number=None,
            )
        )


def log_rebalance_trigger_metrics(strategy: "Strategy", details: dict):
    """
    Logs metrics when a rebalance is triggered.

    Args:
        strategy (Strategy): The strategy instance.
        details (dict): Details of the rebalance trigger.
    """
    strategy.metrics_agg_handler.add_metric(
        MetricsAggTable(
            metric_type=MetricAggType.REBALANCE_TRIGGER.value,
            strategy_id=strategy.id,
            wallet_address=strategy.wallet_address,
            details=details,
            block_number=None,
            action_id=datetime.now(timezone.utc).isoformat(),
            bundle_id=datetime.now(timezone.utc).isoformat(),
        )
    )
