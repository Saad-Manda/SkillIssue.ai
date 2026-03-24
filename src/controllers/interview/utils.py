from datetime import datetime
from uuid import uuid4
from ...models.states.redis_session import session_store
from ...models.states.states import SystemState


def _build_interview_payload(system_state: SystemState) -> dict:
    
    session_id = system_state.session_id
    user = system_state.user
    jd = system_state.jd
    report = system_state.final_report

    session_state = session_store.get(session_id)
    chat_history = session_state.get("chat_history", [])

    payload = {
        "session_id": session_id,
        "user_id": user.user_id,
        "jd_id": jd.jd_id,
        "report": report,
        "chat_history": chat_history,
        "conducted_on": datetime.now(),
    }
    return payload
