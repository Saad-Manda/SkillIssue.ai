from langchain_core.messages import AIMessage

from src.models.states import phase_summary

from ..llm import llm
from .prompt import independent_question_prompt, dependent_question_prompt
from .get_topic import get_independent_topic
from ...models.states.states import SystemState
from ...models.states.redis_session import session_store

def question_generator_node(system_state: SystemState) -> SystemState:

    K = 5

    session_id = system_state.session_id
    session_state = session_store.get(session_id)

    user_summary = system_state.user_summary
    jd = system_state.jd
    plan = system_state.plan
    is_indep = system_state.is_curr_question_independent

    phase_summary = session_state.get("phase_summary", [])
    chat_history = session_state.get("chat_history", [])[:-K]

    if is_indep:
        prev_phase = chat_history[-1].phase
        prev_topic_id = chat_history[-1].topic

        new_phase_idx, new_topic_idx = get_independent_topic(
            plan, prev_phase, prev_topic_id
        )

        new_phase = plan.phase[new_phase_idx]
        new_topic = new_phase[new_topic_idx]


        messages = independent_question_prompt(
            previous_phase_summaries=phase_summary,
            user_summary=user_summary,
            jd=jd,
            phase=new_phase.name,
            topic=new_topic.topic
        )

        try:
            response: AIMessage = llm.invoke(messages)
            new_question = response.content
        except Exception as e:
            print(f"Error in LLM invocation: {e}")
            raise

        system_state.current_question = new_question
        system_state.current_phase_name = new_phase
        system_state.current_topic_id = new_topic.topic_id
        
        return system_state

    current_phase = chat_history[-1].phase
    current_phase_summary = phase_summary[-1]

    messages = dependent_question_prompt(
        current_phase_summary=current_phase_summary,
        previous_k_turns=chat_history,
        user_summary=user_summary,
        jd=jd
    )

    try:
        response: AIMessage = llm.invoke(messages)
        new_question = response.content
    except Exception as e:
        print(f"Error in LLM invocation: {e}")
        raise

    system_state.current_question = new_question

    return system_state