from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from ..config import settings
from .agent_utils.llm import llm
from .agent_utils.states import GlobalState
from .question_generator import question_generator_node
from .summarizer import summarizer_node

load_dotenv()

graph = StateGraph(GlobalState)

graph.add_node("user_summarizer", summarizer_node)
graph.add_node("question_generator", question_generator_node)

graph.add_edge(START, "user_summarizer")
graph.add_edge("user_summarizer", "question_generator")


def should_continue(state: GlobalState):
    turn_count = state.get("turn_count", 0)
    max_turns = state.get("max_turns", 1)
    if turn_count >= max_turns:
        return END
    return "question_generator"


graph.add_conditional_edges(
    "question_generator",
    should_continue,
    {"question_generator": "question_generator", END: END},
)

app = graph.compile()


# app.invoke({"messages": [{"role": "user", "content": "hi!"}]})
