import json
import logging
import uuid

from ...agents.app import app
from ...models.jd_model import JobDescription
from ...models.plan_model import Plan
from ...models.states.states import SystemState
from ...models.user_model import User

logger = logging.getLogger(__name__)


def _parse_json(text: str) -> dict:
    logger.debug("_parse_json called with text_present=%s", bool(text))
    if not text:
        return {}
    return json.loads(text)


def _build_initial_state(
    session_id: str,
    user: User,
    jd: JobDescription,
    interview_length: str,
) -> SystemState:
    logger.info(
        "_build_initial_state called for session_id=%s interview_length=%s",
        session_id,
        interview_length,
    )
    length_to_topics = {
        "short": (5, 10),
        "medium": (10, 15),
        "deep_dive": (15, 20),
    }
    min_topics, max_topics = length_to_topics.get(interview_length, (10, 15))

    return SystemState(
        session_id=session_id,
        user=user,
        user_summary="",
        jd=jd,
        current_question="",
        is_curr_question_independent=True,
        current_response="",
        plan=Plan.model_construct(),
        current_topic_id="",
        current_topic_question_count=0,
        current_phase_name="introduction",
        current_turn_status="START",
        min_topics=min_topics,
        max_topics=max_topics,
        final_report="",
    )


def _run_graph(state: SystemState, *, resume: bool = False) -> SystemState:
    """
    Run or resume the LangGraph interview flow.

    - When resume=False (initial call), we start the graph from the entry node.
    - When resume=True, we continue from the last interrupted node for this
      session_id, merging in the updated fields from `state`.
    """

    logger.info("_run_graph called resume=%s thread_id=%s", resume, state.session_id)
    # Base config for this session
    config = {
        "configurable": {"thread_id": state.session_id},
        "recursion_limit": 50,
    }

    if resume:
        app.update_state(config, {"current_response": state.current_response})
        input_payload = None

    else:
        input_payload = state

    result = app.invoke(input_payload, config=config)
    logger.info("_run_graph completed resume=%s thread_id=%s", resume, state.session_id)
    return SystemState.model_validate(result)


def _load_graph_state(session_id: str) -> SystemState | None:
    """
    Load the latest checkpointed SystemState for a session.

    The POST answer route should use this instead of expecting the client
    to send back the full in-memory state object.
    """
    logger.info("_load_graph_state called for session_id=%s", session_id)
    config = {
        "configurable": {"thread_id": session_id},
        "recursion_limit": 50,
    }
    snapshot = app.get_state(config)
    if snapshot is None or snapshot.values is None:
        logger.warning("_load_graph_state found no state for session_id=%s", session_id)
        return None
    logger.info("_load_graph_state succeeded for session_id=%s", session_id)
    return SystemState.model_validate(snapshot.values)
