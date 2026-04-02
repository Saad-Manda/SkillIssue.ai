from uuid import uuid4

from langchain_core.messages import AIMessage

from ...models.states.redis_session import session_store
from ...models.states.states import SystemState
from ..llm import llm
from ..session_logging import log_agent_error, log_agent_event, log_agent_start
from .prompt import phase_change_summary_prompt, same_phase_summary_prompt



def phase_summarizer_node(system_state: SystemState) -> SystemState:
    session_id = system_state.session_id
    session_data = session_store.get(session_id)
    log_agent_start("phase_summarizer", session_id, system_state)
    log_agent_event(
        session_id, "phase_summarizer", "session_store_loaded", session_data=session_data
    )
    print(
        f"[phase_summarizer] start session_id={session_id} "
        f"phase={system_state.current_phase_name} "
        f"topic_id={system_state.current_topic_id}"
    )

    current_question = system_state.current_question
    current_response = system_state.current_response

    phase_summary = session_data.get("phase_summary", [])
    last = phase_summary[-1] if phase_summary else None

    if last and last["phase_name"] == system_state.current_phase_name:
        print("[phase_summarizer] updating existing phase summary")

        messages = same_phase_summary_prompt(
            current_phase_summary=last["summary"],
            current_question=current_question,
            current_response=current_response,
        )
        log_agent_event(
            session_id,
            "phase_summarizer",
            "prompt_built",
            branch="same_phase",
            messages=messages,
        )

        try:
            print(
                f"[phase_summarizer] invoking llm (same phase) messages={len(messages)}"
            )
            response: AIMessage = llm.invoke(messages)
            new_summary = response.content
            last["summary"] = new_summary
            log_agent_event(
                session_id,
                "phase_summarizer",
                "llm_response",
                branch="same_phase",
                response=response,
            )

        except Exception as e:
            print(f"[phase_summarizer] Error in LLM invocation: {e}")
            log_agent_error(
                session_id,
                "phase_summarizer",
                e,
                branch="same_phase",
                messages=messages,
            )
            raise

        session_store.update(
            session_id, {"session_id": session_id, "phase_summary": phase_summary}
        )
        log_agent_event(
            session_id,
            "phase_summarizer",
            "session_store_updated",
            phase_summary=phase_summary,
            branch="same_phase",
        )
        print(f"[phase_summarizer] done summary_len={len(new_summary or '')}")
        log_agent_event(
            session_id, "phase_summarizer", "done", branch="same_phase", updated_state=system_state
        )

        return system_state

    previous = last["summary"] if last else ""
    print("[phase_summarizer] creating new phase summary (phase changed)")
    messages = phase_change_summary_prompt(
        previous_phase_summary=previous,
        current_phase=system_state.current_phase_name,
        current_question=current_question,
        current_response=current_response,
    )
    log_agent_event(
        session_id,
        "phase_summarizer",
        "prompt_built",
        branch="phase_changed",
        messages=messages,
    )

    try:
        print(
            f"[phase_summarizer] invoking llm (phase change) messages={len(messages)}"
        )
        response: AIMessage = llm.invoke(messages)
        new_summary = response.content
        log_agent_event(
            session_id,
            "phase_summarizer",
            "llm_response",
            branch="phase_changed",
            response=response,
        )
    except Exception as e:
        print(f"[phase_summarizer] Error in LLM invocation: {e}")
        log_agent_error(
            session_id,
            "phase_summarizer",
            e,
            branch="phase_changed",
            messages=messages,
        )
        raise

    new_phase_summary = {
        "phase_summary_id": str(uuid4()),
        "phase_name": system_state.current_phase_name,
        "summary": new_summary,
    }

    phase_summary.append(new_phase_summary)

    session_store.update(
        session_id, {"session_id": session_id, "phase_summary": phase_summary}
    )
    log_agent_event(
        session_id,
        "phase_summarizer",
        "session_store_updated",
        phase_summary=phase_summary,
        branch="phase_changed",
    )
    print(f"[phase_summarizer] done summary_len={len(new_summary or '')}")
    log_agent_event(
        session_id, "phase_summarizer", "done", branch="phase_changed", updated_state=system_state
    )

    return system_state
