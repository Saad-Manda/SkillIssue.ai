from uuid import uuid4

from langchain_core.messages import AIMessage

from ...models.states.redis_session import session_store, parse_chat_history
from ...models.states.states import SystemState
from ..llm import get_llm
from ..session_logging import log_agent_error, log_agent_event, log_agent_start
from .prompt import phase_summary_prompt

llm = get_llm("phase_summarizer")


def phase_summarizer_node(system_state: SystemState) -> SystemState:
    session_id = system_state.session_id
    
    # O(1) Fast Bypass if no phase transition occurred
    if not system_state.phase_transition_occurred:
        print(f"[phase_summarizer] bypass - no phase transition occurred")
        return system_state

    log_agent_start("phase_summarizer", session_id, system_state)
    session_data = session_store.get(session_id) or {}
    log_agent_event(
        session_id, "phase_summarizer", "session_store_loaded", session_data=session_data
    )
    print(
        f"[phase_summarizer] start session_id={session_id} "
        f"completed_phase={system_state.completed_phase_name} "
        f"current_phase={system_state.current_phase_name}"
    )

    # Get turns of completed phase from chat history
    chat_history = parse_chat_history(session_data.get("chat_history", []))
    completed_phase_turns = [
        t for t in chat_history if t.phase_name == system_state.completed_phase_name
    ]

    if not completed_phase_turns:
        print(f"[phase_summarizer] WARNING: no turns found for completed phase {system_state.completed_phase_name}. Bypassing.")
        system_state.phase_transition_occurred = False
        system_state.completed_phase_name = None
        log_agent_event(
            session_id, "phase_summarizer", "done", reason="no_turns_found", updated_state=system_state
        )
        return system_state

    phase_summaries = session_data.get("phase_summary", [])
    
    # Build prompt messages
    messages = phase_summary_prompt(
        phase_name=system_state.completed_phase_name,
        completed_phase_turns=completed_phase_turns,
        prior_phase_summaries=phase_summaries,
    )
    log_agent_event(
        session_id,
        "phase_summarizer",
        "prompt_built",
        messages=messages,
    )

    try:
        print(f"[phase_summarizer] invoking llm (completed phase) messages={len(messages)}")
        response: AIMessage = llm.invoke(messages)
        new_summary = response.content
        log_agent_event(
            session_id,
            "phase_summarizer",
            "llm_response",
            response=response,
        )
    except Exception as e:
        print(f"[phase_summarizer] Error in LLM invocation: {e}")
        log_agent_error(
            session_id,
            "phase_summarizer",
            e,
            messages=messages,
        )
        raise

    new_phase_summary = {
        "phase_summary_id": str(uuid4()),
        "phase_name": system_state.completed_phase_name,
        "summary": new_summary,
    }

    # Ensure phase_summaries is a list
    if not isinstance(phase_summaries, list):
        phase_summaries = []

    phase_summaries.append(new_phase_summary)

    session_store.update(
        session_id, {"session_id": session_id, "phase_summary": phase_summaries}
    )
    log_agent_event(
        session_id,
        "phase_summarizer",
        "session_store_updated",
        phase_summary=phase_summaries,
    )

    # Reset flags after successful transition summary
    system_state.phase_transition_occurred = False
    system_state.completed_phase_name = None

    print(f"[phase_summarizer] done summary_len={len(new_summary or '')}")
    log_agent_event(
        session_id, "phase_summarizer", "done", updated_state=system_state
    )

    return system_state
