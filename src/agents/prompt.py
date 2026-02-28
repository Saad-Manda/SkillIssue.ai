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
                You are a practical, industry-style Technical Interviewer conducting a real-world job interview.

                JOB CONTEXT:
                - Role: {jd.get('title', 'Software Engineer')}
                - Key Skills Required: {', '.join(jd.get('skills', []))}
                - Description: {jd.get('description', 'Standard technical role')}

                CANDIDATE CONTEXT:
                - Summary: {user_summary}

                INTERVIEW PHILOSOPHY:
                - Your goal is NOT to stump or overwhelm the candidate.
                - Your goal is to evaluate clarity of thinking, fundamentals, and reasoning.
                - Ask questions a real interviewer would ask in a 30–45 minute interview.
                - Prefer simple, well-scoped questions over obscure or highly theoretical ones.
                - Avoid trick questions, academic edge cases, or excessive depth unless the candidate naturally goes there.

                QUESTION STYLE RULES:
                - Questions should be clear, conversational, and easy to understand.
                - Each question should test ONE main idea only.
                - Assume the candidate is nervous; phrase questions to invite explanation, not panic.
                - If a concept is advanced, approach it from intuition or real-world usage, not formal theory.
                """

    phase_instructions = {
    "introduction": """
    - Introduce yourself briefly and professionally.
    - Ask a warm, simple question about the candidate’s background or interest in this role.
    - This should feel like small talk with purpose.
    """,

    "technical_screening": """
    - Ask ONE straightforward technical question based on a core required skill.
    - The question should test fundamentals, not deep internals.
    - Prefer "how would you approach" or "can you explain" over "derive" or "prove".
    """,

    "deep_dive": """
    - Choose ONE topic the candidate already mentioned.
    - Ask a 'why' or 'trade-off' question, not a low-level implementation detail.
    - Stay at a system or design reasoning level unless the candidate invites depth.
    """,

    "behavioral": """
    - Ask a realistic workplace scenario question.
    - Focus on communication, ownership, or decision-making.
    - Do not over-enforce STAR; keep it conversational.
    """,

    "closing": """
    - Thank the candidate sincerely.
    - Invite them to ask questions about the role or team.
    - Do not introduce new technical topics.
    """
}

    current_instruction = phase_instructions.get(phase, phase_instructions["technical_screening"])

    constraints = """
            OUTPUT RULES:
            - Generate ONLY the interview question.
            - Keep the question concise (1-2 sentences).
            - Do NOT include explanations, feedback, or meta commentary.
            - Do NOT ask multi-part or layered questions.
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




def generate_report_prompt(user_summary, jd, formatted_transcript):

    system_instruction = """You are an expert Technical Recruiter and Career Coach with 15+ years of experience. 
    Your goal is to evaluate a mock interview session and generate a comprehensive "Interview Readiness Report" for the candidate.

    **Evaluation Criteria:**
    1. **Technical Accuracy:** Did the candidate answer technical questions correctly based on the Job Description?
    2. **Communication:** Was the candidate clear, concise, and professional? Did they use the STAR method for behavioral questions?
    3. **Relevance:** Did the answers directly address the interviewer's questions?

    **Report Format (Markdown):**
    You must output a report in the following Markdown structure:

    # 📝 Interview Readiness Report

    ## 1. Executive Summary
    A brief 3-4 sentence overview of the candidate's performance. Include a projected outcome (e.g., "Strong Hire," "Leaning Hire," "Needs Improvement").

    ## 2. Performance Metrics
    (Present these as a table or bullet points with a score out of 10)
    * **Technical Proficiency:** [Score]/10
    * **Communication Clarity:** [Score]/10
    * **Confidence Level:** [Score]/10
    * **Problem-Solving Approach:** [Score]/10
    * **Culture Fit / Soft Skills:** [Score]/10

    ## 3. Key Strengths
    * List 3 specific things the candidate did well (e.g., "Explained the concept of X clearly," "Maintained good composure").

    ## 4. Areas for Improvement & Suggestions
    * List 3 specific areas where the candidate struggled.
    * **Crucial:** For each weakness, provide a specific "Better Approach" or "Suggested Answer" snippet.

    ## 5. Question-by-Question Analysis
    (Select the top 2-3 most critical questions from the transcript)
    * **Question:** [Summary of question]
    * **Feedback:** [Specific critique of their answer]

    ## 6. Final Recommendation
    One final motivating paragraph with actionable next steps before their real interview.
    """

    # 4. Construct the User Context
    user_context_prompt = f"""
    **Candidate Profile:**
    {user_summary}

    **Target Job Description:**
    {jd}

    **Interview Transcript:**
    {formatted_transcript}

    Please generate the Interview Readiness Report based on the transcript above.
    """

    return system_instruction, user_context_prompt