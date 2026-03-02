from langchain_core.messages import HumanMessage, SystemMessage

from ..llm import llm
from .prompt import generate_report_prompt
from ...models.states.states import SystemState
from ...models.states.redis_session import session_store

def report_node(system_state: SystemState) -> SystemState:

    session_id = system_state.session_id
    session_state = session_store.get(session_id)

    user_summary = system_state.user_summary
    jd = system_state.jd
    raw_history = session_state.get("chat_history", [])
    if not isinstance(raw_history, list):
        raw_history = []

    # 2. Format Chat History for the LLM
    # Converts list of messages (dicts or objects) into a readable script format
    formatted_transcript = ""
    for msg in raw_history:
        # Handle if msg is a dict (common in session system_state) or an object
        if isinstance(msg, dict):
            if "role" in msg or "content" in msg:
                role = msg.get("role", "unknown").upper()
                content = msg.get("content", "")
            elif "type" in msg and "data" in msg and isinstance(msg.get("data"), dict):
                role = str(msg.get("type", "unknown")).upper()
                content = msg["data"].get("content", "")
            else:
                role = "UNKNOWN"
                content = ""
        else:
            # Fallback if it's a LangChain message object
            role = getattr(msg, "type", "unknown").upper()
            content = getattr(msg, "content", "")

        formatted_transcript += f"[{role}]: {content}\n\n"

    # 3. Construct the Prompt
    # We use a comprehensive system instruction to define the persona and output format
    system_instruction, user_context_prompt = generate_report_prompt(
        user_summary, jd, formatted_transcript
    )

    # 5. Invoke LLM
    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_context_prompt)
    ]
    report = "## Error\nAn error occurred while generating the report."
    try:
        response = llm.invoke(messages)
        report = response.content
    except Exception as e:
        # Log error here if you have a logger
        print(f"## Generation Error\nAn error occurred while generating the report: {str(e)}")

    
    system_state.final_report = report

    return system_state