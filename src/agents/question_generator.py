from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from .agent_utils.llm import llm
from .agent_utils.prompt import generate_interview_prompt
from .agent_utils.states import GlobalState
from .agent_utils.short_term_memory import session_store


def question_generator_node(state: GlobalState) -> Dict[str, Any]:
    """
    Production node to generate the next interview question.
    """
    print(f"---GENERATING QUESTION [{state.get('interview_phase', 'unknown')}]---")
    
    # 1. Extract State
    jd = state.get("current_jd", {})
    user_summary = state.get("user_summary", "Candidate info not available.")
    phase = state.get("interview_phase", "introduction")
    chat_history = state.get("chat_history", [])

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



    return {
        "next_question": generated_question,
        "chat_history": updated_history
    }