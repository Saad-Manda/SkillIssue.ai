from ..agents.agent_utils.redis_session import session_store
from .util_controller import _hydrate_messages
from langchain_core.messages import HumanMessage, messages_to_dict
from ..agents.question_generator import question_generator_node




def submit_answer(session_id: str, answer: str, chat):
    if not session_id:
        return chat, 0, 0

    state = session_store.get(session_id)
    if not state:
        return chat, 0, 0

    chat = chat or []
    chat.append({"role": "user", "content": answer})

    recent_turns = state.get("recent_turns", [])
    if recent_turns and recent_turns[-1].get("answer", "") == "":
        recent_turns[-1]["answer"] = answer
    else:
        recent_turns.append({"question": "", "answer": answer, "metrics": {}})

    history_messages = _hydrate_messages(state.get("chat_history"))
    history_messages.append(HumanMessage(content=answer))

    store_count = state.get("store_count", 0) + 1
    session_store.update(
        session_id,
        recent_turns=recent_turns,
        chat_history=messages_to_dict(history_messages),
        store_count=store_count,
    )

    turn_count = state.get("turn_count", 0)
    max_turns = state.get("max_turns", 1)
    if turn_count >= max_turns:
        chat.append({"role": "assistant", "content": "Interview complete."})
        latest_state = session_store.get(session_id)
        return (
            chat,
            latest_state.get("turn_count", 0),
            latest_state.get("store_count", 0),
        )

    state = session_store.get(session_id)
    state["chat_history"] = _hydrate_messages(state.get("chat_history"))
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
        max_turns=result.get("max_turns", state.get("max_turns", 1)),
        interview_phase=state.get("interview_phase", "introduction"),
        store_count=store_count,
    )

    chat.append({"role": "assistant", "content": next_question})
    latest_state = session_store.get(session_id)

    return chat, latest_state.get("turn_count", 0), latest_state.get("store_count", 0)