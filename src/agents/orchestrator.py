from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState

from ..utils.llm import llm
from ..config import settings
from .summarizer import summarizer_node

from dotenv import load_dotenv
load_dotenv()

graph = StateGraph[MessagesState, None, MessagesState, MessagesState](MessagesState)

graph.add_node(summarizer_node)

graph.add_edge(START, "summarizer_node")
graph.add_edge("summarizer_node", END)

graph = graph.compile()

graph.invoke({"messages": [{"role": "user", "content": "hi!"}]})