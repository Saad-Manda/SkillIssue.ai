import json
import uuid

from ...agents.app import app
from ...models.jd_model import JobDescription
from ...models.plan_model import Plan
from ...models.states.states import SystemState
from ...models.user_model import User


def _parse_json(text: str) -> dict:
    if not text:
        return {}
    return json.loads(text)


def _build_initial_state(
    session_id: str,
    user: User,
    jd: JobDescription,
    interview_length: str,
) -> SystemState:
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

    print(f"[_run_graph] resume={resume}, thread_id={state.session_id!r}")
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
    return SystemState.model_validate(result)


def _load_graph_state(session_id: str) -> SystemState | None:
    """
    Load the latest checkpointed SystemState for a session.

    The POST answer route should use this instead of expecting the client
    to send back the full in-memory state object.
    """
    config = {
        "configurable": {"thread_id": session_id},
        "recursion_limit": 50,
    }
    snapshot = app.get_state(config)
    if snapshot is None or snapshot.values is None:
        return None
    return SystemState.model_validate(snapshot.values)
