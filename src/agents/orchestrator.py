from langgraph.graph import StateGraph, START, END
from .agent_utils.llm import llm
from ..config import settings
from .summarizer import summarizer_node
from .question_generator import question_generator_node
from .agent_utils.states import GlobalState

from dotenv import load_dotenv
load_dotenv()

graph = StateGraph(GlobalState)

graph.add_node("user_summarizer", summarizer_node)
graph.add_node("question_generator", question_generator_node)

graph.add_edge(START, "user_summarizer")
graph.add_edge("user_summarizer", "question_generator")
graph.add_edge("question_generator", END)

app = graph.compile()


# app.invoke({"messages": [{"role": "user", "content": "hi!"}]})