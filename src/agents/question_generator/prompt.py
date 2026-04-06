import json
from typing import Any, List

from langchain_core.messages import HumanMessage, SystemMessage

from ...models.jd_model import JobDescription
from ...models.plan_model import Phase, Topic
from ...models.states.phase_summary import PhaseSummary
from ...models.states.turn import Turn


def _to_pretty_json(value: Any) -> str:
    if hasattr(value, "model_dump_json"):
        return value.model_dump_json(indent=2)
    if hasattr(value, "model_dump"):
        return json.dumps(value.model_dump(), indent=2, ensure_ascii=False)
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, indent=2, ensure_ascii=False)
    except TypeError:
        return repr(value)


def independent_question_prompt(
    previous_phase_summaries: List[PhaseSummary],
    user_summary: str,
    previous_k_turns: List[Turn],
    jd: JobDescription,
    phase: Phase,
    topic: Topic,
) -> list:
    previous_phase_summaries_json = [
        s.model_dump() if hasattr(s, "model_dump") else s
        for s in previous_phase_summaries
    ]
    user_json = user_summary
    jd_json = _to_pretty_json(jd)
    phase_json = _to_pretty_json(phase)
    topic_json = _to_pretty_json(topic)
    previous_phase_summaries_json = _to_pretty_json(previous_phase_summaries_json)

    base_instruction = """
You are a practical, industry-style Technical Interviewer generating exactly one interview question.

INTERVIEW PHILOSOPHY:
- Evaluate clarity of thinking, fundamentals, and reasoning.
- Ask what a real interviewer would ask in a real interview.

QUESTION STYLE RULES:
- Keep the question clear, conversational, and easy to understand.
- Test one main idea only.
- Keep scope tight and relevant to the current phase/topic.
- Prefer practical reasoning over trivia.

CONTINUITY RULES:
- Use RECENT CHAT CONTEXT to maintain natural conversation progression.
- The question should feel like the next logical interview step, but still stand alone.
- Avoid repeating or paraphrasing already asked questions.
- If recent turns contain unresolved details, do not reference them with pronouns like “that/this/it/your approach above”.
"""

    mode_instruction = """
BRANCH MODE: INDEPENDENT (HARD CONSTRAINT)
- The new question must be topically independent from the candidate’s immediately previous answer.
- Do NOT ask a follow-up question.
- Do NOT require information from the previous answer to understand or answer this question.
- Keep continuity of interview flow using recent chat only for tone, difficulty calibration, and avoiding repetition.
"""

    context_block = f"""
JOB CONTEXT:
{jd_json}

CANDIDATE CONTEXT:
{user_json}

PHASE CONTEXT (Current Interview Phase):
{phase_json}

TOPIC CONTEXT (Current Topic):
{topic_json}

PREVIOUS PHASE SUMMARIES (before this new phase):
{previous_phase_summaries_json}

RECENT CHAT CONTEXT (previous k turns):
{previous_k_turns_json}
"""

    constraints = """
OUTPUT RULES:
- Generate ONLY one interview question.
- Keep it concise.
- Do NOT include explanation, labels, numbering, JSON, or meta commentary.
- Do NOT ask multi-part or layered questions.
"""

    system_content = base_instruction + "\n" + mode_instruction + "\n" + constraints
    human_content = context_block

    return [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content),
    ]


def dependent_question_prompt(
    current_phase_summary: PhaseSummary,
    previous_k_turns: List[Turn],
    user_summary: str,
    jd: JobDescription,
    phase: Phase,
) -> list:
    current_phase_summary_json = _to_pretty_json(current_phase_summary)
    previous_k_turns_json = [t.model_dump() for t in previous_k_turns]
    jd_json = _to_pretty_json(jd)
    phase_json = _to_pretty_json(phase)
    previous_k_turns_json = _to_pretty_json(previous_k_turns_json)

    base_instruction = """
You are a practical, industry-style Technical Interviewer generating exactly one interview question.

INTERVIEW PHILOSOPHY:
- Evaluate clarity of thinking, fundamentals, and reasoning.
- Ask what a real interviewer would ask in a real interview.

FOLLOW-UP QUALITY RULES:
- Use prior responses to probe depth, trade-offs, edge cases, or contradictions.
- If candidate gave a claim/design/decision earlier, ask them to justify, extend, or stress-test it.
- Avoid generic standalone questions that could be asked without prior context.
- Avoid repeating previously asked questions verbatim.

QUESTION STYLE RULES:
- Keep the question clear, conversational, and easy to understand.
- Test one main idea only.
- Keep scope tight and relevant.
"""

    mode_instruction = """
BRANCH MODE: DEPENDENT (HARD CONSTRAINT)
- The new question must be a follow-up question.
- It must explicitly depend on prior conversation context.
- The dependency may be on:
    1) the immediately previous answer, or
    2) multiple earlier turns/questions, if that produces a better probe.
- Stay within the same phase/topic flow; do NOT jump to a fresh independent topic.
"""

    context_block = f"""
JOB CONTEXT:
{jd_json}

CANDIDATE SUMMARY:
{user_summary}

PHASE CONTEXT (Current Phase):
{phase_json}

CURRENT PHASE SUMMARY:
{current_phase_summary_json}

RECENT CHAT CONTEXT (previous k turns):
{previous_k_turns_json}
"""

    constraints = """
OUTPUT RULES:
- Generate ONLY one interview question.
- Keep it concise.
- Do NOT include explanation, labels, numbering, JSON, or meta commentary.
- Do NOT ask multi-part or layered questions.
"""

    system_content = base_instruction + "\n" + mode_instruction + "\n" + constraints
    human_content = context_block

    return [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content),
    ]
