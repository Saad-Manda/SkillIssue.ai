import operator
from typing import TypedDict
from langchain_core.messages import HumanMessage, SystemMessage
from ..models.user_model import User
from .agent_utils.llm import llm
from .agent_utils.summarizer_prompt import summarize_user_prompt

class SummarizerAgentState(TypedDict):
    user: User
    summary: str

def summarizer_node(state: SummarizerAgentState):
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