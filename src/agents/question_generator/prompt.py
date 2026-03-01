from typing import List

from langchain_core.messages import HumanMessage, SystemMessage

from ...models.jd_model import JobDescription
from ...models.plan_model import Phase, Topic
from ...models.states.phase_summary import PhaseSummary
from ...models.states.turn import Turn


def independent_question_prompt(
    previous_phase_summaries: List[PhaseSummary],
    user_summary: str,
    jd: JobDescription,
    phase: Phase,
    topic: Topic,
) -> list:
    previous_phase_summaries_json = [s.model_dump() for s in previous_phase_summaries]
    user_json = user_summary.model_dump_json(indent=2)
    jd_json = jd.model_dump_json(indent=2)
    phase_json = phase.model_dump_json(indent=2)
    topic_json = topic.model_dump_json(indent=2)

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
- Generate a fresh question for a topic transition.
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

    system_content = (
        base_instruction
        + "\n"
        + mode_instruction
        + "\n"
        + constraints
    )
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
    current_phase_summary_json = current_phase_summary.model_dump_json(indent=2)
    previous_k_turns_json = [t.model_dump() for t in previous_k_turns]
    jd_json = jd.model_dump_json(indent=2)
    phase_json = phase.model_dump_json(indent=2)

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

    system_content = (
        base_instruction
        + "\n"
        + mode_instruction
        + "\n"
        + constraints
    )
    human_content = context_block

    return [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content),
    ]
