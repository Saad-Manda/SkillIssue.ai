from langchain_core.messages import HumanMessage, SystemMessage
from .agent_utils.llm import llm
from .agent_utils.prompt import summarize_user_prompt
from .agent_utils.states import GlobalState

def summarizer_node(state: GlobalState) -> GlobalState:
    user_data = state["current_user"]
    
    # We convert the Pydantic model to JSON to give the LLM structured context
    user_json = user_data.model_dump_json(indent=2)
    
    # Contextual Prompt
    prompt = summarize_user_prompt(user_json)
    
    response = llm.invoke([HumanMessage(content=prompt)])

    state["user_summary"] = response.content
    
    # Return the update to the state (filling the 'summary' key)
    return state