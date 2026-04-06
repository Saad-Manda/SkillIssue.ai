from typing import TypedDict


def summarize_user_prompt(user_json: TypedDict):
    prompt = f"""
You are an expert HR profiler generating concise candidate summaries for recruiters.

Task:
Generate ONE SHORT professional summary based ONLY on the provided user data.

Hard Rules (must follow strictly):
1. Use ONLY fields explicitly present in the User Data.
2. Do NOT infer, assume, embellish, extrapolate, or generalize beyond the data.
3. If a field is missing, null, empty, or ambiguous, ignore it completely.
4. Do NOT mention missing information.
5. Do NOT add opinions, personality traits, soft traits, or future potential.
6. Do NOT use bullet points, headings, or labels.
7. Output must be a SINGLE paragraph, maximum 5-10 sentences.
8. Return ONLY the summary text — no preamble, no explanations.

Negative Prompt (strict):
- Never fabricate any detail not explicitly stated in User Data.
- Never guess job title, seniority, industry, domain, company impact, responsibilities, metrics, or achievements.
- Never introduce tools, technologies, certifications, awards, leadership, or project outcomes unless explicitly present.
- Never use speculative wording such as "likely", "probably", "appears to", "seems", "demonstrates", or "suggests".
- If uncertain whether a detail is explicitly provided, exclude it.

Content Rules:
- Start with the candidate's name and primary professional identity ONLY if directly supported by explicit experience/project titles.
- Include education (degree / institution) only if present.
- Mention most recent or current experience only if available.
- List key skills concisely (comma-separated) only if explicitly listed.
- Mention notable projects or leadership only if explicitly provided.

Self-check before finalizing:
- Verify every claim maps to an explicit field in User Data.
- Remove any sentence fragment that cannot be directly traced to User Data.

User Data:
{user_json}
"""

    return prompt
