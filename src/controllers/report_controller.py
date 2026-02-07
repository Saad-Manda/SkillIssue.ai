from ..agents.agent_utils.redis_session import session_store
from .util_controller import _hydrate_messages
from langchain_core.messages import HumanMessage, messages_to_dict
from ..agents.report_generator import generate_report





def print_report(session_id: str):

    state = session_store.get(session_id)
    report = generate_report(state)
    
    session_store.update(session_id, {
        "final_report": report
    })

    return report