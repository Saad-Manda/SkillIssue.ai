import re
from uuid import uuid4
from ...models.states.states import SystemState
from ...models.states.redis_session import session_store
from .metrics import calculate_turn_metrics

def metrics_node(system_state: SystemState) -> SystemState:
    session_id = system_state.session_id
    session_state = session_store.get(session_id)

    chat_history = session_state.get("chat_history")
    current_question = system_state.current_question
    current_response = system_state.current_response
    current_phase = system_state.current_phase_name
    current_topic_id = system_state.current_topic_id


    results = calculate_turn_metrics(
        question=current_question,
        answer=current_response,
        chat_history=chat_history,
        behavioral_phase=(True if re.findall('behavior', current_phase.lower()) else False),
    )

    current_turn = {
        "chat_id": uuid4(),
        "question": current_question,
        "response": current_response,
        "metrics": results,
        "phase_name": current_phase,
        "topic_id": current_topic_id
    }

    chat_history.append(current_turn)

    session_store.update(session_id, {
            "session_id": session_id,
            "chat_history": chat_history
        })

    return system_state