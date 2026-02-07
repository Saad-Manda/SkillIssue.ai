from typing import TypedDict, Literal, List, Any, Dict
from .states import GlobalState
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

def summarize_user_prompt(user_json: TypedDict):
    prompt = f"""
    You are an expert HR profiler generating concise candidate summaries for recruiters.

    Task:
    Generate ONE SHORT professional summary based ONLY on the provided user data.

    Hard Rules (must follow strictly):
    1. Use ONLY fields explicitly present in the User Data.
    2. Do NOT infer, assume, embellish, or generalize beyond the data.
    3. If a field is missing, null, or empty, ignore it completely.
    4. Do NOT mention missing information.
    5. Do NOT add opinions, soft traits, or future potential.
    6. Do NOT use bullet points, headings, or labels.
    7. Output must be a SINGLE paragraph, maximum 5-10 sentences.
    8. Return ONLY the summary text — no preamble, no explanations.

    Content Rules:
    - Start with the candidate's name and primary professional identity (if inferable from experience or projects ONLY).
    - Include education (degree / institution if present).
    - Mention most recent or current experience if available.
    - List key skills concisely (comma-separated, no exaggeration).
    - Mention notable projects or leadership ONLY if explicitly provided.

    User Data:
     {user_json}
    """

    return prompt


def generate_interview_prompt(
    jd: Dict[str, Any], 
    user_summary: str, 
    phase: str, 
    chat_history: List[BaseMessage]
) -> List[BaseMessage]:
    """
    Constructs the full message list for the LLM, including System Prompt, 
    Context (History), and the Trigger Prompt.
    """
    
    # --- 1. System Prompt Construction ---
    base_instruction = f"""
    You are an expert Technical Interviewer conducting a professional job interview.
    
    JOB CONTEXT:
    - Role: {jd.get('title', 'Software Engineer')}
    - Key Skills Required: {', '.join(jd.get('skills', []))}
    - Description: {jd.get('description', 'Standard technical role')}

    CANDIDATE CONTEXT:
    - Summary: {user_summary}

    YOUR GOAL:
    Assess the candidate's fit for this role through a natural conversation.
    """

    phase_instructions = {
        "introduction": """
            - Start by briefly introducing yourself as the AI interviewer.
            - Ask a welcoming but relevant opening question about their background or interest in this specific role.
        """,
        "technical_screening": """
            - Ask a specific technical question that tests a core skill listed in the Job Description.
            - Focus on problem-solving ability.
        """,
        "deep_dive": """
            - Pick a complex topic from the candidate's summary or previous answers.
            - Ask a 'How' or 'Why' question (e.g., system design, architectural choices).
        """,
        "behavioral": """
            - Ask a behavioral question using the STAR method context.
            - Focus on soft skills: teamwork, conflict resolution, or leadership.
        """,
        "closing": """
            - Briefly thank the candidate for their time.
            - Ask if they have any final questions.
            - Do not ask any more technical questions.
        """
    }

    current_instruction = phase_instructions.get(phase, phase_instructions["technical_screening"])

    constraints = """
    OUTPUT RULES:
    - Generate ONLY the question text. 
    - Do NOT include prefixes like "Here is the next question:".
    - Do NOT provide feedback on the previous answer in this turn.
    """

    full_system_text = (
        base_instruction + 
        "\n\nCURRENT PHASE: " + phase + "\n" + 
        current_instruction + "\n" + 
        constraints
    )

    # --- 2. Assemble Message List ---
    messages = [SystemMessage(content=full_system_text)]

    # Append last 10 messages for context (Sliding Window)
    # We filter to ensure we are only passing valid BaseMessage objects if necessary
    messages.extend(chat_history[-10:])

    # Append the trigger to force generation
    messages.append(
        HumanMessage(content="Based on the context and previous answers, generate the next interview question now.")
    )

    return messages