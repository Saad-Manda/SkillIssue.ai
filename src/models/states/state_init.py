from .redis_session import session_store
from .states import SessionState, SystemState

from .turn import Turn
from .phase_summary import PhaseSummary
from ...models.user_model import User
from ...models.jd_model import JobDescription
from ...models.plan_model import Plan

def session_state_initialize(session_id: str):
    """
    Initializes a new interview session in Redis.
    Must be called BEFORE invoking the graph for the first time.
    """
    print(f"---INITIALIZING SESSION: {session_id}---")

    session_state = SessionState()

    session_state.session_id = session_id
    session_state.chat_history = []
    session_state.phasewise_summary = []

    session_store.set(session_id, session_state)

    print(f"Session {session_id} created in Redis.")


def system_state_initialize(
    session_id: str,
    user: User,
    jd: JobDescription
):
    system_state = SystemState()

    system_state.session_id = session_id
    system_state.user = user
    system_state.user_summary = None
    system_state.jd = jd
    system_state.current_question = None
    system_state.is_curr_question_independent = True
    system_state.current_response = None
    system_state.current_phase_name = None
    system_state.plan = None
    system_state.current_topic_question_count = 0
    system_state.current_topic_id = None
    system_state.final_report = None

    return system_state