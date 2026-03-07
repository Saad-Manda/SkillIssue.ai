from .utils import _run_graph
from ...agents.app import app
from ...models.states.states import SystemState


def get_report(state: SystemState | None, session_id: str):
    if state is None:
        return "No report available yet.", None
    
    app.update_state(
        {"configurable": {"thread_id": session_id}},
        {"should_generate_report": True}
    )
    updated_state = state.model_copy(update={"should_generate_report": True})
    final_state = _run_graph(updated_state, resume=True)
    return final_state.final_report, final_state