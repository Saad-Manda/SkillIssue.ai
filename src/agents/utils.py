from .session_logging import log_agent_event
from ..models.states.states import SystemState

def _route_after_router(state: SystemState) -> str:
    log_agent_event(
        state.session_id,
        "orchestrator",
        "route_after_router",
        should_generate_report=state.should_generate_report,
        router_intent=state.router_intent,
        current_topic_id=state.current_topic_id,
        current_phase_name=state.current_phase_name,
    )
    if state.should_generate_report:
        return "report_generator"
    return "question_generator"

def _route_after_metrics(state: SystemState) -> str:
    log_agent_event(
        state.session_id,
        "orchestrator",
        "route_after_metrics",
        should_generate_report=state.should_generate_report,
        router_intent=state.router_intent,
        current_topic_id=state.current_topic_id,
        current_phase_name=state.current_phase_name,
    )
    if state.should_generate_report:
        return "report_generator"
    return "router"


def _route_after_question_generator(state: SystemState) -> str:
    log_agent_event(
        state.session_id,
        "orchestrator",
        "route_after_question_generator",
        phase_transition_occurred=state.phase_transition_occurred,
        completed_phase_name=state.completed_phase_name,
        current_phase_name=state.current_phase_name,
    )
    if state.phase_transition_occurred:
        return "phase_summarizer"
    return "metric_calculator"