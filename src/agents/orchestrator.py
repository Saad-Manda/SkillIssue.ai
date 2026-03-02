from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from ..config import settings
from .llm import llm
from ..models.states.states import SystemState

from .planner.agent import planner_node
from .question_generator.agent import question_generator_node
from .user_summarizer.agent import summarizer_node
from .phase_summarizer.agent import phase_summarizer_node
from .router.agent import router_node
from .metric_calculator.agent import metrics_node
from .report_generator.agent import report_node

load_dotenv()

checkpointer = MemorySaver()
def _build_graph():
    graph = StateGraph(SystemState)

    # Nodes
    graph.add_node("planner", planner_node)
    graph.add_node("user_summarizer", summarizer_node)
    graph.add_node("phase_summarizer", phase_summarizer_node)
    graph.add_node("router", router_node)
    graph.add_node("question_generator", question_generator_node)
    graph.add_node("metric_calculator", metrics_node)
    graph.add_node("report_generator", report_node)


    ## Edges

    graph.set_entry_point("user_summarizer")
    graph.add_edge("user_summarizer", "planner")
    graph.add_edge("planner", "router")
    graph.add_edge("router", "question_generator")
    graph.add_edge("question_generator", "phase_summarizer")
    graph.add_edge("phase_summarizer", "metric_calculator")
    graph.add_edge("metric_calculator", "router")
    graph.add_edge("metric_calculator", "report_generator")


    app = graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["router", "question_generator", "report_generator"],
        recursion_limit=50,
    )
    return app