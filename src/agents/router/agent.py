import json
import re
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import JsonOutputParser

from ..llm import get_llm
from ..session_logging import log_agent_error, log_agent_event, log_agent_start
from .prompt import router_prompt
from ...models.states.states import SystemState
from ...models.states.redis_session import parse_chat_history, session_store
from ..question_generator.get_topic import get_next_topic

llm = get_llm("router")


def router_node(system_state: SystemState) -> SystemState:
    session_id = system_state.session_id
    log_agent_start("router", session_id, system_state)
    print(
        f"[router] start session_id={session_id} "
        f"topic_id={system_state.current_topic_id} "
        f"topic_name={system_state.current_topic_name} "
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
    current_topic_name = system_state.current_topic_name or (current_topic.topic if current_topic else "")
    if current_topic is None:
        print("[router] current_topic not found -> independent, TOPIC CHANGED")
        system_state.is_curr_question_independent = True
        system_state.router_intent = "advance_topic"
        system_state.phase_transition_occurred = False
        system_state.completed_phase_name = None
        log_agent_event(
            session_id, "router", "done", reason="current_topic_not_found", updated_state=system_state
        )
        return system_state

    max_question_count = current_topic.max_question_count
    print(f"[router] max_question_count={max_question_count}")

    # Load session state
    session_state = session_store.get(session_id) or {}
    log_agent_event(
        session_id,
        "router",
        "session_store_loaded",
        session_state=session_state,
    )

    # Retrieve turns of the current phase in O(1) from system_state
    turns_in_current_phase = system_state.turns_in_current_phase or []

    # If within the first 1-2 turns of a fresh phase, get previous phase summary
    previous_phase_summary = ""
    if len(turns_in_current_phase) <= 2:
        phase_summaries = session_state.get("phase_summary", [])
        if phase_summaries:
            last_summary = phase_summaries[-1]
            if isinstance(last_summary, dict):
                previous_phase_summary = last_summary.get("summary", "")
            else:
                previous_phase_summary = getattr(last_summary, "summary", "")

    # Build prompt messages
    messages = router_prompt(
        chat_history=turns_in_current_phase,
        current_topic_id=current_topic_id,
        current_topic_name=current_topic_name,
        current_phase_name=system_state.current_phase_name,
        k=k,
        max_question_count=max_question_count,
        previous_phase_summary=previous_phase_summary,
    )
    log_agent_event(session_id, "router", "prompt_built", messages=messages)

    parser = JsonOutputParser()

    try:
        print(f"[router] invoking llm messages={len(messages)} chat_history_used={len(turns_in_current_phase)}")
        response: AIMessage = llm.invoke(messages)
        preview = (response.content or "")[:120].replace("\n", "\\n")
        print(f"[router] llm_response_preview={preview}")
        log_agent_event(session_id, "router", "llm_response", response=response)
        
        result = parser.parse(response.content)
    except Exception as e:
        print(f"[router] Error in LLM invocation or parsing: {e}")
        log_agent_error(session_id, "router", e, messages=messages)
        raise

    intent = result.get("intent", "advance_topic")
    focus = result.get("focus", "")

    system_state.router_intent = intent
    system_state.router_focus = focus
    system_state.is_curr_question_independent = (intent == "advance_topic")

    # If intent is to advance, determine if we transition phase
    if intent == "advance_topic":
        new_phase_idx, new_topic_idx = get_next_topic(
            system_state.plan, system_state.current_phase_name, current_topic_id
        )
        if new_phase_idx is None:
            print("[router] last topic reached -> should generate report")
            system_state.should_generate_report = True
        else:
            new_phase = system_state.plan.phase[new_phase_idx]
            if new_phase.name != system_state.current_phase_name:
                print(f"[router] phase transition detected: {system_state.current_phase_name} -> {new_phase.name}")
                system_state.phase_transition_occurred = True
                system_state.completed_phase_name = system_state.current_phase_name

    print(
        f"[router] done intent={system_state.router_intent} "
        f"focus={system_state.router_focus} "
        f"phase_transition={system_state.phase_transition_occurred}"
    )
    log_agent_event(
        session_id,
        "router",
        "done",
        parsed_result=result,
        updated_state=system_state,
    )

    return system_state
