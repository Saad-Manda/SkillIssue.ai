from langchain_core.messages import AIMessage

from ...models.states.redis_session import parse_chat_history, session_store
from ...models.states.states import SystemState
from ...models.states.phase_summary import PhaseSummary
from ..llm import get_llm
from ..session_logging import log_agent_error, log_agent_event, log_agent_start
from .get_topic import get_current_phase, get_current_topic, get_next_topic
from .prompt import dependent_question_prompt, topic_transition_prompt

llm = get_llm("question_generator")


def question_generator_node(system_state: SystemState) -> SystemState:
    session_id = system_state.session_id
    log_agent_start("question_generator", session_id, system_state)

    print(
        f"[question_generator] start session_id={session_id} "
        f"intent={system_state.router_intent} "
        f"k={system_state.current_topic_question_count} "
        f"phase={system_state.current_phase_name} "
        f"topic_id={system_state.current_topic_id}"
    )

    session_state = session_store.get(session_id) or {}
    log_agent_event(
        session_id,
        "question_generator",
        "session_store_loaded",
        session_state=session_state,
    )

    user_summary = system_state.user_summary
    jd = system_state.jd
    k = system_state.current_topic_question_count
    plan = system_state.plan
    router_intent = system_state.router_intent
    router_focus = system_state.router_focus

    phase_summary = session_state.get("phase_summary", [])
    raw_history = session_state.get("chat_history") or []
    chat_history_full = parse_chat_history(raw_history)
    last_turn = chat_history_full[-1] if chat_history_full else None
    
    log_agent_event(
        session_id,
        "question_generator",
        "context_prepared",
        phase_summary=phase_summary,
        raw_history=raw_history,
        chat_history_full=chat_history_full,
        last_turn=last_turn.model_dump() if last_turn else None,
        k=k,
        router_intent=router_intent,
        router_focus=router_focus,
    )

    # 1. TOPIC CHANGED / Transition Branch
    if router_intent == "advance_topic":
        if chat_history_full:
            prev_phase = chat_history_full[-1].phase_name
            prev_topic_id = chat_history_full[-1].topic_id

            print(
                f"[question_generator] TOPIC CHANGED from phase={prev_phase} topic_id={prev_topic_id}"
            )
            new_phase_idx, new_topic_idx = get_next_topic(
                plan, prev_phase, prev_topic_id
            )

            if new_phase_idx is None:
                print("[question_generator] no next topic found -> generating report")
                system_state.should_generate_report = True
                log_agent_event(
                    session_id,
                    "question_generator",
                    "done",
                    reason="interview_complete_sentinel",
                    updated_state=system_state,
                )
                return system_state

            new_phase = plan.phase[new_phase_idx]
            new_topic = new_phase.topics[new_topic_idx]

        else:
            print(f"[question_generator] TOPIC CHANGED (no prior history)")
            new_phase = plan.phase[0]
            new_topic = new_phase.topics[0]

        print(
            f"[question_generator] next phase={new_phase.name} topic_id={new_topic.topic_id}"
        )
        log_agent_event(
            session_id,
            "question_generator",
            "topic_selected",
            phase=new_phase,
            topic=new_topic,
            branch="TOPIC CHANGED",
        )

        bridge_turns = [last_turn] if last_turn else []
        messages = topic_transition_prompt(
            previous_phase_summaries=phase_summary,
            user_summary=user_summary,
            previous_k_turns=bridge_turns,
            jd=jd,
            phase=new_phase,
            topic=new_topic,
            router_intent=router_intent,
        )
        log_agent_event(
            session_id,
            "question_generator",
            "prompt_built",
            messages=messages,
            branch="TOPIC CHANGED",
        )

        try:
            print(
                f"[question_generator] invoking llm (transition) messages={len(messages)}"
            )
            response: AIMessage = llm.invoke(messages)
            new_question = response.content
            log_agent_event(
                session_id,
                "question_generator",
                "llm_response",
                response=response,
                branch="TOPIC CHANGED",
            )
        except Exception as e:
            print(f"[question_generator] Error in LLM invocation: {e}")
            log_agent_error(
                session_id,
                "question_generator",
                e,
                messages=messages,
                branch="TOPIC CHANGED",
            )
            raise

        if system_state.current_phase_name != new_phase.name:
            system_state.turns_in_current_phase = []
        system_state.current_question = new_question
        system_state.current_phase_name = new_phase.name
        system_state.current_topic_id = new_topic.topic_id
        system_state.current_topic_name = new_topic.topic
        system_state.current_topic_question_count = 1

        print(
            f"[question_generator] done question_len={len(new_question or '')} (topic changed)"
        )
        log_agent_event(
            session_id,
            "question_generator",
            "done",
            branch="TOPIC CHANGED",
            updated_state=system_state,
        )

        return system_state

    # 2. DEPENDENT (Follow-up / New Angle) Branch
    else:
        last_turn = system_state.turns_in_current_phase[-1]
        current_phase_name = last_turn.phase_name
        current_phase = get_current_phase(plan, current_phase_name)
        if current_phase is None:
            raise ValueError(f"Could not find phase in plan: {current_phase_name}")
        
        current_topic_id = last_turn.topic_id
        current_topic = get_current_topic(plan, current_phase_name, current_topic_id)
        if current_topic is None:
            raise ValueError(f"Could not find topic in plan: phase={current_phase_name} topic_id={current_topic_id}")

        # Use a placeholder PhaseSummary for the running phase since summaries are generated on transition
        current_phase_summary = PhaseSummary(
            phase_summary_id="current_running",
            phase_name=current_phase_name,
            summary="Active evaluation phase. No completed summary available yet."
        )

        # Get turns of current topic as context in O(1) from turns of the current phase
        current_topic_turns = [
            t for t in (system_state.turns_in_current_phase or []) if t.topic_id == current_topic_id
        ]

        router_focus = system_state.router_focus

        print(f"[question_generator] dependent flow intent={router_intent} phase={current_phase_name}")
        messages = dependent_question_prompt(
            current_phase_summary=current_phase_summary,
            previous_k_turns=current_topic_turns,
            user_summary=user_summary,
            jd=jd,
            phase=current_phase,
            topic=current_topic,
            router_intent=router_intent,
            router_focus=router_focus,
        )
        log_agent_event(
            session_id,
            "question_generator",
            "prompt_built",
            messages=messages,
            branch="DEPENDENT",
        )

        try:
            print(
                f"[question_generator] invoking llm (dependent) messages={len(messages)}"
            )
            response: AIMessage = llm.invoke(messages)
            new_question = response.content
            log_agent_event(
                session_id,
                "question_generator",
                "llm_response",
                response=response,
                branch="DEPENDENT",
            )
        except Exception as e:
            print(f"[question_generator] Error in LLM invocation: {e}")
            log_agent_error(
                session_id,
                "question_generator",
                e,
                messages=messages,
                branch="DEPENDENT",
            )
            raise

        system_state.current_question = new_question
        system_state.current_topic_question_count += 1

        print(
            f"[question_generator] done question_len={len(new_question or '')} (dependent)"
        )
        log_agent_event(
            session_id,
            "question_generator",
            "done",
            branch="DEPENDENT",
            updated_state=system_state,
        )

        return system_state
