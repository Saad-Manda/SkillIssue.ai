import logging

from fastapi import HTTPException

from ...models.states.redis_session import session_store
from ...models.states.states import SystemState
from .utils import _load_graph_state, _run_graph

logger = logging.getLogger(__name__)


def submit_answer(
    session_id: str, answer: str
) -> tuple[SystemState, list[dict], int, int]:
    logger.info("submit_answer controller called for session_id=%s", session_id)
    state = _load_graph_state(session_id)
    logger.info(
        "submit_answer controller checkpoint lookup for session_id=%s found=%s",
        session_id,
        state is not None,
    )

    if not session_id or state is None:
        logger.warning(
            "submit_answer controller missing session for session_id=%s", session_id
        )
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

    logger.info(
        "submit_answer controller succeeded for session_id=%s turn_count=%s",
        session_id,
        turn_count,
    )
    return next_state, chat, turn_count, store_count
