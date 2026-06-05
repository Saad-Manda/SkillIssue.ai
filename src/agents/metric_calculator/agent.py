import re
from uuid import uuid4
from ...models.states.states import SystemState
from ...models.states.redis_session import session_store
from ..session_logging import log_agent_event, log_agent_start
from .metrics import calculate_turn_metrics
from ...models.states.turn import Turn
from ...models.states.metrics import Metrics

def metrics_node(system_state: SystemState) -> SystemState:
    session_id = system_state.session_id
    session_state = session_store.get(session_id)
    log_agent_start("metric_calculator", session_id, system_state)
    log_agent_event(
        session_id, "metric_calculator", "session_store_loaded", session_state=session_state
    )
    print(
        f"[metric_calculator] start session_id={session_id} "
        f"phase={system_state.current_phase_name} "
        f"topic_id={system_state.current_topic_id}"
    )

    chat_history_raw = session_state.get("chat_history") or []
    chat_history_for_metrics = []
    for t in chat_history_raw:
        chat_history_for_metrics.append({"role": "user", "content": t["question"]})
        chat_history_for_metrics.append({"role": "assistant", "content": t["response"]})
    
    current_question = system_state.current_question
    current_response = system_state.current_response
    current_phase = system_state.current_phase_name
    current_topic_id = system_state.current_topic_id


    results = calculate_turn_metrics(
        question=current_question,
        answer=current_response,
        chat_history=chat_history_for_metrics,
        behavioral_phase=(True if re.findall('behavior', current_phase.lower()) else False),
    )
    log_agent_event(
        session_id,
        "metric_calculator",
        "metrics_calculated",
        input_payload={
            "current_question": current_question,
            "current_response": current_response,
            "current_phase": current_phase,
            "current_topic_id": current_topic_id,
            "chat_history_for_metrics": chat_history_for_metrics,
        },
        results=results,
    )
    print(
        f"[metric_calculator] metrics_done keys={len(results)} "
        f"QAR={results.get('QAR')} TDS={results.get('TDS')} ACS={results.get('ACS')}"
    )

    current_turn = Turn(
        chat_id=str(uuid4()),
        question=current_question,
        response=current_response,
        metrics=Metrics(**results),
        phase_name=current_phase,
        topic_id=current_topic_id,
    )

    chat_history_raw.append(current_turn.model_dump())

    session_store.update(session_id, {
            "session_id": session_id,
            "chat_history": chat_history_raw
        })
    log_agent_event(
        session_id,
        "metric_calculator",
        "session_store_updated",
        chat_history=chat_history_raw,
    )

    print(f"[metric_calculator] done turns={len(chat_history_raw)}")
    updated = system_state.model_copy(
        update={
            "should_generate_report": system_state.should_generate_report
        })
    log_agent_event(session_id, "metric_calculator", "done", updated_state=updated)
    return updated
