from langchain_core.messages import HumanMessage, SystemMessage
from ..llm import llm
from .prompt import summarize_user_prompt
from ...models.states.states import SystemState

def summarizer_node(system_state: SystemState) -> SystemState:
    user_data = system_state["current_user"]
    
    # We convert the Pydantic model to JSON to give the LLM structured context
    user_json = user_data.model_dump_json(indent=2)
    
    # Contextual Prompt
    prompt = summarize_user_prompt(user_json)
    
    response = llm.invoke([HumanMessage(content=prompt)])

    system_state["user_summary"] = response.content
    
    # Return the update to the system_state (filling the 'summary' key)
    return system_state