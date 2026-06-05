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
from .session_logging import log_agent_event

load_dotenv()

checkpointer = MemorySaver()
def _build_graph():
    print("[orchestrator] building interview graph")
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
    
    def _route_after_metrics(state: SystemState) -> str:
        log_agent_event(
            state.session_id,
            "orchestrator",
            "route_after_metrics",
            should_generate_report=state.should_generate_report,
            current_turn_status=state.current_turn_status,
            current_topic_id=state.current_topic_id,
            current_phase_name=state.current_phase_name,
        )
        if state.should_generate_report:
            return "report_generator"
        return "router"

    graph.add_conditional_edges(
        "metric_calculator",
        _route_after_metrics,
        {"router": "router", "report_generator": "report_generator"}
    )


    app = graph.compile(
        checkpointer=checkpointer,
        # Interrupt the graph after generating a question, i.e. before
        # the `phase_summarizer` node, so that the UI can display the
        # question, collect the user's response, and then resume.
        interrupt_before=["phase_summarizer"],
    )
    print("[orchestrator] graph compiled")
    return app
