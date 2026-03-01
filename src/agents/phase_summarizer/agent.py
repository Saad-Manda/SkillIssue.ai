from langchain_core.messages import AIMessage

from ..llm import llm
from .prompt import same_phase_summary_prompt, phase_change_summary_prompt
from ...models.states.states import SystemState
from ...models.states.redis_session import session_store

def phase_summarizer_node(system_state: SystemState) -> SystemState: 
    session_id = system_state.session_id
    session_state = session_store.get(session_id)

    current_question = system_state.current_question
    current_response = system_state.current_response

    
    phase_summary = session_state.get("phase_summary", [])[:-1]

    if phase_summary.phase_name == system_state.current_phase_name