from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from strategy import Strategy

def complete(strat: "Strategy", snapshot=False) -> None:
        # TODO: Add or remove any additional completion logic
        strat.persistent_state.current_state = strat.State.COMPLETED
        strat.persistent_state.current_flowstatus = strat.InternalFlowStatus.PREPARING_ACTION
        strat.persistent_state.completed = True
        if snapshot:
            strat.log_snapshot()

        strat.show_balances()