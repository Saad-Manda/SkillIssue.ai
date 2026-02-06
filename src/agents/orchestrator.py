from langgraph.graph import StateGraph, START, END
from .agent_utils.llm import llm
from ..config import settings
from .summarizer import summarizer_node
from .agent_utils.states import GlobalState

from dotenv import load_dotenv
load_dotenv()

graph = StateGraph(GlobalState)

graph.add_node("summarizer_node", summarizer_node)

graph.add_edge(START, "summarizer_node")
graph.add_edge("summarizer_node", END)

app = graph.compile()


# app.invoke({"messages": [{"role": "user", "content": "hi!"}]})