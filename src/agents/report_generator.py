from langchain_core.messages import SystemMessage, HumanMessage
from .agent_utils.llm import llm
from .agent_utils.redis_session import session_store
from .agent_utils.prompt import generate_report_prompt

def generate_report(state) -> str:
    
    if not state:
        return "## Error\nSession data could not be retrieved. Please try again."

    user_summary = state.get("user_summary", "N/A")
    jd = state.get("current_jd", "N/A")
    raw_history = state.get("chat_history", [])

    # 2. Format Chat History for the LLM
    # Converts list of messages (dicts or objects) into a readable script format
    formatted_transcript = ""
    for msg in raw_history:
        # Handle if msg is a dict (common in session state) or an object
        if isinstance(msg, dict):
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
        else:
            # Fallback if it's a LangChain message object
            role = getattr(msg, "type", "unknown").upper()
            content = getattr(msg, "content", "")
        
        formatted_transcript += f"[{role}]: {content}\n\n"

    # 3. Construct the Prompt
    # We use a comprehensive system instruction to define the persona and output format
    system_instruction, user_context_prompt = generate_report_prompt(user_summary, jd, formatted_transcript)

    # 5. Invoke LLM
    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_context_prompt)
    ]

    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        # Log error here if you have a logger
        return f"## Generation Error\nAn error occurred while generating the report: {str(e)}"