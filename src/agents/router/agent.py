from langchain_core.messages import AIMessage

from ..llm import llm
from .prompt import router_prompt
from ...models.states.states import SystemState
from ...models.states.redis_session import session_store


def router_node(system_state: SystemState) -> SystemState:
    session_id = system_state.session_id
    
    k = system_state.current_topic_question_count
    current_topic_id = system_state.current_topic_id
    matching_topics = [
        topic 
        for phase in system_state.plan.phase 
        for topic in phase.topics 
        if topic.topic_id == current_topic_id
    ]
    current_topic = matching_topics[0] if matching_topics else None
    max_question_count = current_topic.max_question_count
    
    
    ## Independent + topic Change
    if k >= max_question_count:
        system_state.is_curr_question_independent = True
        system_state.current_turn_status = "TOPIC CHANGED"
    
        return system_state


    ## Same Topic
    session_state = session_store.get(session_id)
    chat_history = session_state.get("chat_history", [])[:-k]
    
    messages = router_prompt(chat_history=chat_history)

    try:
        response: AIMessage = llm.invoke(messages)
        result = response.content
    except Exception as e:
        print(f"Error in LLM invocation: {e}")
        raise


    system_state.is_curr_question_independent = not result.is_dependent
    system_state.current_turn_status = result.reason

    return system_state