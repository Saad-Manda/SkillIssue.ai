import logging

from ...agents.app import app
from ...models.states.states import SystemState
from .utils import _load_graph_state, _run_graph

logger = logging.getLogger(__name__)


def get_report(session_id: str):
    logger.info("get_report controller called for session_id=%s", session_id)
    state = _load_graph_state(session_id)
    if state is None:
        logger.warning(
            "get_report controller no state found for session_id=%s", session_id
        )
        return "No report available yet.", None

    app.update_state(
        {"configurable": {"thread_id": session_id}}, {"should_generate_report": True}
    )
    updated_state = state.model_copy(update={"should_generate_report": True})
    final_state = _run_graph(updated_state, resume=True)
    logger.info("get_report controller succeeded for session_id=%s", session_id)
    return final_state.final_report, final_state
