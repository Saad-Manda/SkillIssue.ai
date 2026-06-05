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
    router_reason: str = "",
    is_topic_transition: bool = False,
) -> list:
    previous_phase_summaries_json = [
        s.model_dump() if hasattr(s, "model_dump") else s
        for s in previous_phase_summaries
    ]
    user_json = user_summary
    previous_k_turns_json = [t.model_dump() for t in previous_k_turns]
    jd_json = _to_pretty_json(jd)
    phase_json = _to_pretty_json(phase)
    topic_json = _to_pretty_json(topic)
    previous_phase_summaries_json = _to_pretty_json(previous_phase_summaries_json)
    previous_k_turns_json = _to_pretty_json(previous_k_turns_json)

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

CONVERSATION FLOW (MANDATORY)
- Use RECENT CHAT CONTEXT to maintain continuity of tone, seniority level, and progression.
- The question must include a short conversational bridge that links to the ongoing interview flow.
- The bridge can reference high-level direction (e.g., interests, role focus, phase shift), but not depend on details of the last answer.
- Avoid abrupt topic jumps; move from broad → role-aligned → technical depth naturally.
"""

    if is_topic_transition:
        mode_instruction = f"""
BRANCH MODE: TOPIC TRANSITION
- You are transitioning to a new topic: **{topic.topic}** (within phase: {phase.name}).
- The RECENT CHAT CONTEXT below contains the candidate's last answer from the previous topic — use it as your bridge source.
- Do NOT evaluate or praise hollowly ("Great answer!", "Interesting!").
- The question that follows must be squarely focused on the new topic: **{topic.topic}**.
"""
    else:
        mode_instruction = """
BRANCH MODE: INDEPENDENT (STRICT)
- The question itself must NOT require the candidate's last answer to be understandable or answerable.
- The question itself must NOT probe, challenge, or drill into a specific claim from the last answer.
- You MAY (and should) open with a brief 1-2 sentence acknowledgment that references the overall conversation direction — but the question that follows must stand alone.
- The question must be aligned to current phase/topic.
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

ROUTER DIRECTIVE (why this question is being generated — HIGHEST PRIORITY):
{router_reason if router_reason else "No specific directive. Use your best judgment based on context above."}
Formulate your question to directly address this directive.
"""

    constraints = """
OUTPUT RULES:
Your response MUST have exactly two parts, in this order:

1. BRIDGE (1–2 sentences): Naturally acknowledge the conversation so far — the candidate's general approach, a topic they covered, or the direction of the interview. Do NOT evaluate or praise with hollow phrases ("Great answer!", "Interesting!"). Be natural and human.
2. QUESTION (1 sentence): The next interview question. It must be self-contained — no dependency on the last answer's specifics.

Do NOT include labels, numbering, JSON, or meta commentary.
Do NOT ask multi-part or layered questions.
Keep the total response concise (3–5 sentences combined).
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
    router_reason: str = "",
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
- Explicitly anchor to prior context (a claim, design choice, trade-off, assumption, or gap).
- Use prior responses to probe depth, trade-offs, edge cases, or contradictions.
- If candidate gave a claim/design/decision earlier, ask them to justify, extend, or stress-test it.
- Avoid generic standalone questions that could be asked without prior context.
- Avoid repeating previously asked questions verbatim.

QUESTION STYLE RULES:
- Keep the question clear, conversational, and easy to understand.
- Test one main idea only.
- Keep scope tight and relevant.

CONVERSATION FLOW (MANDATORY):
- Before asking your question, open with 1–2 sentences that acknowledge something specific from the candidate's most recent answer (a claim they made, a technology they mentioned, a trade-off they described, or an approach they took).
- The acknowledgment does NOT need to be evaluative — simply referencing what they said is enough.
- Do NOT use hollow filler phrases ("Great answer!", "That's very interesting!").
- The acknowledgment should flow naturally into the follow-up question.
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

ROUTER DIRECTIVE (why this follow-up is being generated — HIGHEST PRIORITY):
{router_reason if router_reason else "No specific directive. Use your best judgment based on context above."}
Formulate your follow-up question to directly address this directive.
"""

    constraints = """
OUTPUT RULES:
Your response MUST have exactly two parts, in this order:

1. BRIDGE (1–2 sentences): Acknowledge something specific from the candidate's prior answer — a claim, a design decision, a technology choice, or a gap you observed. Be natural and conversational. Do NOT use hollow filler ("Great!", "Interesting!"). Make it feel like a real interviewer heard them.
2. QUESTION (1 sentence): The follow-up question. It must directly build on the prior conversation.

Do NOT include labels, numbering, JSON, or meta commentary.
Do NOT ask multi-part or layered questions.
Keep the total response concise (3–5 sentences combined).
"""

    system_content = base_instruction + "\n" + mode_instruction + "\n" + constraints
    human_content = context_block

    return [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content),
    ]
