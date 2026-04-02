import json
import re
from langchain_core.messages import AIMessage

from ..llm import llm
from ..session_logging import log_agent_error, log_agent_event, log_agent_start
from .prompt import router_prompt
from ...models.states.states import SystemState
from ...models.states.redis_session import parse_chat_history, session_store


def router_node(system_state: SystemState) -> SystemState:
    session_id = system_state.session_id
    log_agent_start("router", session_id, system_state)
    print(
        f"[router] start session_id={session_id} "
        f"topic_id={system_state.current_topic_id} "
        f"k={system_state.current_topic_question_count}"
    )
    
    k = system_state.current_topic_question_count
    current_topic_id = system_state.current_topic_id
    matching_topics = [
        topic 
        for phase in system_state.plan.phase 
        for topic in phase.topics 
        if topic.topic_id == current_topic_id
    ]
    log_agent_event(
        session_id,
        "router",
        "topic_lookup",
        current_topic_id=current_topic_id,
        matching_topics=matching_topics,
    )
    current_topic = matching_topics[0] if matching_topics else None
    if current_topic is None:
        print("[router] current_topic not found -> independent, TOPIC CHANGED")
        system_state.is_curr_question_independent = True
        system_state.current_turn_status = "TOPIC CHANGED"
        log_agent_event(
            session_id, "router", "done", reason="current_topic_not_found", updated_state=system_state
        )
        return system_state

    max_question_count = current_topic.max_question_count
    print(f"[router] max_question_count={max_question_count}")
    
    
    ## Independent + topic Change
    if k >= max_question_count:
        print("[router] k>=max_question_count -> independent, TOPIC CHANGED")
        system_state.is_curr_question_independent = True
        system_state.current_turn_status = "TOPIC CHANGED"
        log_agent_event(
            session_id,
            "router",
            "done",
            reason="max_question_count_reached",
            updated_state=system_state,
        )
    
        return system_state


    ## Same Topic
    session_state = session_store.get(session_id)
    chat_history = session_state.get("chat_history", [])[:-k]
    chat_history = parse_chat_history(chat_history)
    log_agent_event(
        session_id,
        "router",
        "session_store_loaded",
        session_state=session_state,
        chat_history=chat_history,
    )
    
    messages = router_prompt(chat_history=chat_history)
    log_agent_event(session_id, "router", "prompt_built", messages=messages)

    try:
        print(f"[router] invoking llm messages={len(messages)} chat_history_used={len(chat_history)}")
        response: AIMessage = llm.invoke(messages)
        preview = (response.content or "")[:120].replace("\n", "\\n")
        print(f"[router] llm_response_preview={preview}")
        log_agent_event(session_id, "router", "llm_response", response=response)
        
        raw = response.content.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw.strip())
        result = json.loads(raw)
        
    except Exception as e:
        print(f"[router] Error in LLM invocation: {e}")
        log_agent_error(session_id, "router", e, messages=messages)
        raise


    system_state.is_curr_question_independent = not bool(result["is_dependent"])
    system_state.current_turn_status = str(result["reason"])
    print(
        f"[router] done is_independent={system_state.is_curr_question_independent} "
        f"reason={system_state.current_turn_status}"
    )
    log_agent_event(
        session_id,
        "router",
        "done",
        parsed_result=result,
        updated_state=system_state,
    )

    return system_state
