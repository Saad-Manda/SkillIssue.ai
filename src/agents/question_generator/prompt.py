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
- Keep scope tight and relevant to the target topic.
"""

    mode_instruction = """
BRANCH MODE: INDEPENDENT
- Do NOT create a follow-up that depends on the candidate's immediate prior answer.
- Align strictly to the provided current phase and current topic.
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

QUESTION STYLE RULES:
- Keep the question clear, conversational, and easy to understand.
- Test one main idea only.
- Prefer depth, trade-offs, and reasoning over trivia.
"""

    mode_instruction = """
BRANCH MODE: DEPENDENT
- Generate a follow-up question within the same phase/topic flow.
- Ground the follow-up in previous turns and current phase summary.
- Do NOT jump to a new independent topic.
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
- Do NOT repeat a previously asked question.
"""

    system_content = base_instruction + "\n" + mode_instruction + "\n" + constraints
    human_content = context_block

    return [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content),
    ]
