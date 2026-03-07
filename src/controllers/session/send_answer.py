from ...models.states.states import SystemState
from .utils import _run_graph

def submit_answer(session_id: str, state: SystemState | None, answer: str, chat):
    print(f"[submit_answer] session_id param={session_id!r}, state.session_id={state.session_id if state else 'STATE IS NONE'!r}") 

    if not session_id or state is None:
        return state, (chat or []), 0, 0

    chat = chat or []
    if answer:
        chat.append({"role": "user", "content": answer})

    updated_state = state.model_copy(update={"current_response": answer})
    # Resume the graph from the last interruption (just after question generation),
    # starting at the `phase_summarizer` node for this session.
    next_state = _run_graph(updated_state, resume=True)

    if next_state.current_question:
        chat.append({"role": "assistant", "content": next_state.current_question})

    turn_count = sum(
        1 for msg in chat if isinstance(msg, dict) and msg.get("role") == "assistant"
    )
    store_count = turn_count

    return next_state, chat, turn_count, store_count