from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from ..llm import llm
from ..session_logging import log_agent_error, log_agent_event, log_agent_start
from .prompt import summarize_user_prompt
from ...models.states.states import SystemState

def summarizer_node(system_state: SystemState) -> SystemState:
    session_id = system_state.session_id
    print(
        f"[user_summarizer] start session_id={session_id} "
        f"user_id={getattr(system_state.user, 'id', None)}"
    )
    log_agent_start("user_summarizer", session_id, system_state)
    user_data = system_state.user
    
    # We convert the Pydantic model to JSON to give the LLM structured context
    user_json = user_data.model_dump_json(indent=2)
    
    # Contextual Prompt
    prompt = summarize_user_prompt(user_json)
    log_agent_event(
        session_id,
        "user_summarizer",
        "prompt_built",
        user_json=user_json,
        prompt=prompt,
    )


    try:
        print(f"[user_summarizer] invoking llm prompt_len={len(prompt)}")
        response: AIMessage = llm.invoke([HumanMessage(content=prompt)])
        summary = response.content
        log_agent_event(
            session_id,
            "user_summarizer",
            "llm_response",
            response=response,
        )
    except Exception as e:
        print(f"[user_summarizer] Error in LLM invocation: {e}")
        log_agent_error(
            session_id,
            "user_summarizer",
            e,
            prompt=prompt,
            user_json=user_json,
        )
        raise

    system_state.user_summary = summary
    print(f"[user_summarizer] done summary_len={len(summary or '')}")
    log_agent_event(session_id, "user_summarizer", "done", updated_state=system_state)
    
    # Return the update to the system_state (filling the 'summary' key)
    return system_state
