import json
import uuid
from ..models.user_model import User
from ..models.jd_model import JobDescription
from ..agents.summarizer import summarizer_node
from ..agents.question_generator import question_generator_node
from .util_controller import _normalize_jd, _hydrate_messages
from ..agents.agent_utils.redis_session import session_store
from ..agents.agent_utils.redis_utils import start_new_interview
from langchain_core.messages import messages_to_dict






def start_session(user_json: str, jd_json: str, max_turns: int):
    user_dict = json.loads(user_json)
    jd_dict = json.loads(jd_json)

    if isinstance(user_dict, dict) and "user_profile" in user_dict:
        user_dict = user_dict["user_profile"]
    if isinstance(jd_dict, dict) and "jd_profile" in jd_dict:
        jd_dict = jd_dict["jd_profile"]

    user = User(**user_dict)
    jd = JobDescription(**jd_dict)

    summary = summarizer_node({"current_user": user}).get("user_summary", "")

    session_id = str(uuid.uuid4())
    start_new_interview(
        session_id=session_id,
        user_data=user.model_dump(mode="json"),
        jd_data=_normalize_jd(jd),
        summary=summary,
        max_turns=max_turns,
    )

    state = session_store.get(session_id)
    state["chat_history"] = _hydrate_messages(state.get("chat_history"))
    state["current_jd"] = state.get("current_jd", {})
    state["turn_count"] = state.get("turn_count", 0)
    state["max_turns"] = state.get("max_turns", max_turns)

    result = question_generator_node(state)
    next_question = result.get("next_question", "")

    store_count = state.get("store_count", 0) + 1
    session_store.update(
        session_id,
        next_question=next_question,
        chat_history=messages_to_dict(
            result.get("chat_history", state["chat_history"])
        ),
        recent_turns=result.get("recent_turns", state.get("recent_turns", [])),
        turn_count=result.get("turn_count", state.get("turn_count", 0)),
        max_turns=result.get("max_turns", state.get("max_turns", max_turns)),
        interview_phase=state.get("interview_phase", "introduction"),
        store_count=store_count,
    )

    chat = [{"role": "assistant", "content": next_question}]
    latest_state = session_store.get(session_id)

    return (
        session_id,
        chat,
        latest_state.get("turn_count", 0),
        latest_state.get("store_count", 0),
    )






    