from uuid import uuid4

from langchain_core.messages import AIMessage

from ...models.states.redis_session import session_store
from ...models.states.states import SystemState
from ..llm import llm
from .prompt import phase_change_summary_prompt, same_phase_summary_prompt



def phase_summarizer_node(system_state: SystemState) -> SystemState:
    session_id = system_state.session_id
    session_data = session_store.get(session_id)
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

        try:
            print(
                f"[phase_summarizer] invoking llm (same phase) messages={len(messages)}"
            )
            response: AIMessage = llm.invoke(messages)
            new_summary = response.content
            last["summary"] = new_summary

        except Exception as e:
            print(f"[phase_summarizer] Error in LLM invocation: {e}")
            raise

        session_store.update(
            session_id, {"session_id": session_id, "phase_summary": phase_summary}
        )
        print(f"[phase_summarizer] done summary_len={len(new_summary or '')}")

        return system_state

    previous = last["summary"] if last else ""
    print("[phase_summarizer] creating new phase summary (phase changed)")
    messages = phase_change_summary_prompt(
        previous_phase_summary=previous,
        current_phase=system_state.current_phase_name,
        current_question=current_question,
        current_response=current_response,
    )

    try:
        print(
            f"[phase_summarizer] invoking llm (phase change) messages={len(messages)}"
        )
        response: AIMessage = llm.invoke(messages)
        new_summary = response.content
    except Exception as e:
        print(f"[phase_summarizer] Error in LLM invocation: {e}")
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
    print(f"[phase_summarizer] done summary_len={len(new_summary or '')}")

    return system_state
