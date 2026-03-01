from langchain_core.messages import AIMessage
from uuid import uuid4

from ..llm import llm
from .prompt import same_phase_summary_prompt, phase_change_summary_prompt
from ...models.states.states import SystemState
from ...models.states.redis_session import session_store

def phase_summarizer_node(system_state: SystemState) -> SystemState: 
    session_id = system_state.session_id
    session_state = session_store.get(session_id)

    current_question = system_state.current_question
    current_response = system_state.current_response

    
    phase_summary = session_state.get("phase_summary", [])
    current_phase_summary = phase_summary[-1].summary

    if phase_summary.phase_name == system_state.current_phase_name:
        
        messages = same_phase_summary_prompt(
            current_phase_summary=current_phase_summary,
            current_question=current_question,
            current_response=current_response
        )

        try:
            response: AIMessage = llm.invoke(messages)
            new_summary = response.content
        except Exception as e:
            print(f"Error in LLM invocation: {e}")
            raise

        phase_summary[-1].summary = new_summary


        session_store.update(session_id, {
            "session_id": session_id,
            "phase_summary": phase_summary
        })

        return system_state

    
    messages = phase_change_summary_prompt(
        previous_phase_summary=current_phase_summary,
        current_phase=system_state.current_phase_name,
        current_question=current_question,
        current_response=current_response
    )

    try:
        response: AIMessage = llm.invoke(messages)
        new_summary = response.content
    except Exception as e:
        print(f"Error in LLM invocation: {e}")
        raise

    phase_summary_id = uuid4()
    new_phase_summary = {
        "phase_summary_id": phase_summary_id,
        "phase_name": system_state.current_phase_name,
        "summary": new_summary
    }

    phase_summary.append(new_phase_summary)

    session_store.update(session_id, {
        "session_id": session_id,
        "phase_summary": phase_summary
    })

    return system_state