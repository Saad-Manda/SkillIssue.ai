from langchain_core.messages import AIMessage

from ...models.states.redis_session import parse_chat_history, session_store
from ...models.states.states import SystemState
from ..llm import llm
from .get_topic import get_current_phase, get_current_topic, get_next_topic
from .prompt import dependent_question_prompt, independent_question_prompt


def question_generator_node(system_state: SystemState) -> SystemState:

    print(
        f"[question_generator] start session_id={system_state.session_id} "
        f"reason={system_state.current_turn_status} "
        f"is_indep={system_state.is_curr_question_independent} "
        f"k={system_state.current_topic_question_count} "
        f"phase={system_state.current_phase_name} "
        f"topic_id={system_state.current_topic_id}"
    )

    session_id = system_state.session_id
    session_state = session_store.get(session_id)

    user_summary = system_state.user_summary
    jd = system_state.jd
    k = system_state.current_topic_question_count
    plan = system_state.plan
    is_indep = system_state.is_curr_question_independent
    reason = system_state.current_turn_status

    phase_summary = session_state.get("phase_summary", [])
    raw_history = session_state.get("chat_history") or []
    chat_histor_tot = parse_chat_history(raw_history)
    chat_history = chat_histor_tot[:-k] if k and k > 0 else chat_histor_tot

    if reason == "TOPIC CHANGED":
        if chat_history:
            prev_phase = chat_history[-1].phase_name
            prev_topic_id = chat_history[-1].topic_id

            print(
                f"[question_generator] TOPIC CHANGED from phase={prev_phase} topic_id={prev_topic_id}"
            )
            new_phase_idx, new_topic_idx = get_next_topic(
                plan, prev_phase, prev_topic_id
            )

            new_phase = plan.phase[new_phase_idx]
            new_topic = new_phase.topics[new_topic_idx]

        else:
            print(f"[question_generator] TOPIC CHANGED")
            new_phase = plan.phase[0]
            new_topic = new_phase.topics[0]

        print(
            f"[question_generator] next phase={new_phase.name} topic_id={new_topic.topic_id}"
        )

        messages = independent_question_prompt(
            previous_phase_summaries=phase_summary,
            user_summary=user_summary,
            jd=jd,
            phase=new_phase,
            topic=new_topic,
        )

        try:
            print(
                f"[question_generator] invoking llm (independent) messages={len(messages)}"
            )
            response: AIMessage = llm.invoke(messages)
            new_question = response.content
        except Exception as e:
            print(f"[question_generator] Error in LLM invocation: {e}")
            raise

        system_state.current_question = new_question
        system_state.current_phase_name = new_phase.name
        system_state.current_topic_id = new_topic.topic_id
        system_state.current_topic_question_count = 1

        print(
            f"[question_generator] done question_len={len(new_question or '')} (topic changed)"
        )

        return system_state

    elif not is_indep:
        current_phase_name = chat_history[-1].phase_name
        current_phase = get_current_phase(plan, current_phase_name)
        if current_phase is None:
            raise ValueError(f"Could not find phase in plan: {current_phase_name}")
        current_phase_summary = phase_summary[-1]

        print(f"[question_generator] dependent follow-up phase={current_phase_name}")
        messages = dependent_question_prompt(
            current_phase_summary=current_phase_summary,
            previous_k_turns=chat_history,
            user_summary=user_summary,
            jd=jd,
            phase=current_phase,
        )

        try:
            print(
                f"[question_generator] invoking llm (dependent) messages={len(messages)}"
            )
            response: AIMessage = llm.invoke(messages)
            new_question = response.content
        except Exception as e:
            print(f"[question_generator] Error in LLM invocation: {e}")
            raise

        system_state.current_question = new_question
        system_state.current_topic_question_count += 1

        print(
            f"[question_generator] done question_len={len(new_question or '')} (dependent)"
        )

        return system_state

    current_phase_name = chat_history[-1].phase_name
    current_topic_id = chat_history[-1].topic_id

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
        jd=jd,
        phase=current_phase,
        topic=topic,
    )

    try:
        print(
            f"[question_generator] invoking llm (independent) messages={len(messages)}"
        )
        response: AIMessage = llm.invoke(messages)
        new_question = response.content
    except Exception as e:
        print(f"[question_generator] Error in LLM invocation: {e}")
        raise

    system_state.current_question = new_question
    system_state.current_phase_name = current_phase_name
    system_state.current_topic_id = topic.topic_id
    system_state.current_topic_question_count = 1

    print(
        f"[question_generator] done question_len={len(new_question or '')} (independent)"
    )

    return system_state
