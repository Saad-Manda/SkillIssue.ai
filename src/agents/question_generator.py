from typing import Any, Dict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .agent_utils.llm import llm
from .agent_utils.prompt import generate_interview_prompt
from .agent_utils.states import GlobalState


def question_generator_node(state: GlobalState) -> Dict[str, Any]:
    """
    Production node to generate the next interview question.
    """
    print(f"---GENERATING QUESTION [{state.get('interview_phase', 'unknown')}]---")

    # 1. Extract State
    jd = state.get("current_jd", {})
    user_summary = state.get("user_summary", "Candidate info not available.")
    phase = state.get("interview_phase", "introduction") ## ----> here the phase is default the introduction but we need to tweak here  according to response of the user
    chat_history = state.get("chat_history", [])
    recent_turns = state.get("recent_turns", [])
    turn_count = state.get("turn_count", 0)
    max_turns = state.get("max_turns", 1)

    # 2. Build Messages (Logic is now encapsulated here)
    messages = generate_interview_prompt(jd, user_summary, phase, chat_history)

    # 3. Invoke LLM
    try:
        response = llm.invoke(messages)
        generated_question = response.content.strip()
    except Exception as e:
        print(f"Error in LLM invocation: {e}")
        # Fallback question to prevent crash
        generated_question = "Could you tell me more about your background?"

    # 4. Update State
    new_ai_message = AIMessage(content=generated_question)
    updated_history = chat_history + [new_ai_message]
    updated_turns = recent_turns + [
        {"question": generated_question, "answer": "", "metrics": {}}
    ]
    updated_turn_count = turn_count + 1

    return {
        "next_question": generated_question,
        "chat_history": updated_history,
        "recent_turns": updated_turns,
        "turn_count": updated_turn_count,
        "max_turns": max_turns,
    }
