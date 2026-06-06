from langchain_core.messages import AIMessage

from ...models.states.redis_session import parse_chat_history, session_store
from ...models.states.states import SystemState
from ..llm import llm
from ..session_logging import log_agent_error, log_agent_event, log_agent_start
from .get_topic import get_current_phase, get_current_topic, get_next_topic
from .prompt import dependent_question_prompt, independent_question_prompt


def question_generator_node(system_state: SystemState) -> SystemState:
    session_id = system_state.session_id
    log_agent_start("question_generator", session_id, system_state)

    print(
        f"[question_generator] start session_id={session_id} "
        f"reason={system_state.current_turn_status} "
        f"is_indep={system_state.is_curr_question_independent} "
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
    is_indep = system_state.is_curr_question_independent
    reason = system_state.current_turn_status

    phase_summary = session_state.get("phase_summary", [])
    raw_history = session_state.get("chat_history") or []
    chat_history_full = parse_chat_history(raw_history)
    # Pre-topic background: turns *before* the current-topic block.
    # Used only as background context for the INDEPENDENT branch prompt,
    # so the LLM does not accidentally anchor its question to current-topic turns.
    chat_history_pre_topic = chat_history_full[:-k] if k > 0 else chat_history_full
    # last_turn: used as bridge context for TOPIC CHANGED transition.
    last_turn = chat_history_full[-1] if chat_history_full else None
    log_agent_event(
        session_id,
        "question_generator",
        "context_prepared",
        phase_summary=phase_summary,
        raw_history=raw_history,
        chat_history_full=chat_history_full,
        chat_history_pre_topic=chat_history_pre_topic,
        last_turn=last_turn.model_dump() if last_turn else None,
        k=k,
        reason=reason,
        is_independent=is_indep,
    )

    if reason == "TOPIC CHANGED":
        # Use the full (unsliced) history for topic lookup — we need the last
        # turn's phase/topic to know which topic we are transitioning *from*.
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

        # Pass only the last turn as bridge context (option a) so the LLM can
        # naturally acknowledge the candidate's final answer before pivoting.
        bridge_turns = [last_turn] if last_turn else []
        messages = independent_question_prompt(
            previous_phase_summaries=phase_summary,
            user_summary=user_summary,
            previous_k_turns=bridge_turns,
            jd=jd,
            phase=new_phase,
            topic=new_topic,
            router_reason=reason,
            is_topic_transition=True,
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
                f"[question_generator] invoking llm (independent) messages={len(messages)}"
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

        system_state.current_question = new_question
        system_state.current_phase_name = new_phase.name
        system_state.current_topic_id = new_topic.topic_id
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

    elif not is_indep:
        current_phase_name = chat_history_full[-1].phase_name
        current_phase = get_current_phase(plan, current_phase_name)
        if current_phase is None:
            raise ValueError(f"Could not find phase in plan: {current_phase_name}")
        current_phase_summary = phase_summary[-1]

        print(f"[question_generator] dependent follow-up phase={current_phase_name}")
        messages = dependent_question_prompt(
            current_phase_summary=current_phase_summary,
            previous_k_turns=chat_history_full[-k:],
            user_summary=user_summary,
            jd=jd,
            phase=current_phase,
            router_reason=reason,
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

    current_phase_name = chat_history_full[-1].phase_name
    current_topic_id = chat_history_full[-1].topic_id

    topic = get_current_topic(plan, current_phase_name, current_topic_id)
    if topic is None:
        raise ValueError(
            f"Could not find topic in plan: phase={current_phase_name} topic_id={current_topic_id}"
        )
    current_phase = get_current_phase(plan, current_phase_name)
    if current_phase is None:
        raise ValueError(f"Could not find phase in plan: {current_phase_name}")

    messages = independent_question_prompt(
        previous_phase_summaries=phase_summary,
        user_summary=user_summary,
        previous_k_turns=chat_history_pre_topic,
        jd=jd,
        phase=current_phase,
        topic=topic,
        router_reason=reason,
    )
    log_agent_event(
        session_id,
        "question_generator",
        "prompt_built",
        messages=messages,
        branch="INDEPENDENT",
    )

    try:
        print(
            f"[question_generator] invoking llm (independent) messages={len(messages)}"
        )
        response: AIMessage = llm.invoke(messages)
        new_question = response.content
        log_agent_event(
            session_id,
            "question_generator",
            "llm_response",
            response=response,
            branch="INDEPENDENT",
        )
    except Exception as e:
        print(f"[question_generator] Error in LLM invocation: {e}")
        log_agent_error(
            session_id,
            "question_generator",
            e,
            messages=messages,
            branch="INDEPENDENT",
        )
        raise

    system_state.current_question = new_question
    system_state.current_phase_name = current_phase_name
    system_state.current_topic_id = topic.topic_id
    system_state.current_topic_question_count += 1

    print(
        f"[question_generator] done question_len={len(new_question or '')} (independent)"
    )
    log_agent_event(
        session_id,
        "question_generator",
        "done",
        branch="INDEPENDENT",
        updated_state=system_state,
    )

    return system_state
