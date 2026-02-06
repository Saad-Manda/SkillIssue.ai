from typing import TypedDict


def summarize_user_prompt(user_json: TypedDict):
    prompt = f"""
    You are an expert HR profiler. 
    Analyze the following user data strictly and generate a short, professional summary.
    
    Rules:
    1. Be direct and unambiguous.
    2. Highlight key skills, education, and latest experience.
    3. Do not infer information not present in the data.
    4. Return ONLY the summary string.

    User Data:
    {user_json}
    """

    return prompt