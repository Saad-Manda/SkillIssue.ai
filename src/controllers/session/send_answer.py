from fastapi import HTTPException

from ...models.states.redis_session import session_store
from ...models.states.states import SystemState
from .utils import _load_graph_state, _run_graph


def submit_answer(
    session_id: str, answer: str
) -> tuple[SystemState, list[dict], int, int]:
    state = _load_graph_state(session_id)
    print(
        f"[submit_answer] session_id param={session_id!r}, "
        f"checkpoint_found={state is not None}"
    )

    if not session_id or state is None:
        raise HTTPException(status_code=404, detail="Interview session not found")

    updated_state = state.model_copy(update={"current_response": answer})
    next_state = _run_graph(updated_state, resume=True)

    session_data = session_store.get(session_id)
    turns = session_data.get("chat_history") or []
    chat: list[dict] = []
    for turn in turns:
        chat.append({"role": "assistant", "content": turn["question"]})
        chat.append({"role": "user", "content": turn["response"]})

    if next_state.current_question:
        chat.append({"role": "assistant", "content": next_state.current_question})

    turn_count = len(turns)
    store_count = len(turns)

    return next_state, chat, turn_count, store_count