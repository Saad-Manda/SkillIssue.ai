from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from ..llm import llm
from .prompt import summarize_user_prompt
from ...models.states.states import SystemState

def summarizer_node(system_state: SystemState) -> SystemState:
    print(
        f"[user_summarizer] start session_id={system_state.session_id} "
        f"user_id={getattr(system_state.user, 'id', None)}"
    )
    user_data = system_state.user
    
    # We convert the Pydantic model to JSON to give the LLM structured context
    user_json = user_data.model_dump_json(indent=2)
    
    # Contextual Prompt
    prompt = summarize_user_prompt(user_json)


    try:
        print(f"[user_summarizer] invoking llm prompt_len={len(prompt)}")
        response: AIMessage = llm.invoke([HumanMessage(content=prompt)])
        summary = response.content
    except Exception as e:
        print(f"[user_summarizer] Error in LLM invocation: {e}")
        raise

    system_state.user_summary = summary
    print(f"[user_summarizer] done summary_len={len(summary or '')}")
    
    # Return the update to the system_state (filling the 'summary' key)
    return system_state