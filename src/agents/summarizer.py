import operator
from typing import TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from ..utils.llm import llm
from ..models.user_model import User
from .prompts.summarizer_prompt import summarize_user_prompt

class AgentState(TypedDict):
    user: User
    summary: str

def summarizer_node(state: AgentState):
    """
    Node that takes a User object from the state, contextualizes their profile,
    and generates a concise summary without ambiguity.
    """
    user_data = state["user"]
    
    # We convert the Pydantic model to JSON to give the LLM structured context
    user_json = user_data.model_dump_json(indent=2)
    
    # Contextual Prompt
    prompt = summarize_user_prompt(user_json)
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # Return the update to the state (filling the 'summary' key)
    return {"summary": response.content}