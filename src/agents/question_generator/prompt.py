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


def topic_transition_prompt(
    previous_phase_summaries: List[PhaseSummary],
    user_summary: str,
    previous_k_turns: List[Turn],
    jd: JobDescription,
    phase: Phase,
    topic: Topic,
    router_intent: str = "",
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

    mode_instruction = f"""
BRANCH MODE: TOPIC TRANSITION
- You are transitioning to a new topic: **{topic.topic}** (within phase: {phase.name}).
- The RECENT CHAT CONTEXT below contains the candidate's last answer from the previous topic — use it as your bridge source.
- Do NOT evaluate or praise hollowly ("Great answer!", "Interesting!").
- The question that follows must be squarely focused on the new topic: **{topic.topic}**.
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

ROUTER DIRECTIVE (why this question is being generated):
{router_intent if router_intent else "Transitioning to a new topic."}
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
    topic: Topic,
    router_intent: str,
    router_focus: str = "",
) -> list:
    current_phase_summary_json = _to_pretty_json(current_phase_summary)
    previous_k_turns_json = [t.model_dump() for t in previous_k_turns]
    jd_json = _to_pretty_json(jd)
    phase_json = _to_pretty_json(phase)
    topic_json = _to_pretty_json(topic)
    previous_k_turns_json = _to_pretty_json(previous_k_turns_json)

    base_instruction = """
You are a practical, industry-style Technical Interviewer generating exactly one interview question.

INTERVIEW PHILOSOPHY:
- Evaluate clarity of thinking, fundamentals, and reasoning.
- Ask what a real interviewer would ask in a real interview.

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

    if router_intent == "dependent_followup":
        mode_instruction = f"""
BRANCH MODE: DEPENDENT FOLLOW-UP (HARD CONSTRAINT)
- The new question must be a direct follow-up question probing details, gaps, or assumptions.
- It must explicitly build on specific parts of the candidate's prior responses.
- TARGET FOCUS SIGNAL: Probes/focuses on: {router_focus}
"""
    else:
        # dependent_new_angle
        mode_instruction = f"""
BRANCH MODE: DEPENDENT NEW ANGLE (STRICT)
- The candidate answered the last question well. Do NOT probe specific gaps or details of their last answer.
- Instead, explore a different angle, tradeoff, scenario, or edge case under the SAME topic: **{topic.topic}**.
- TARGET FOCUS SIGNAL: Explore this angle: {router_focus}
"""

    context_block = f"""
JOB CONTEXT:
{jd_json}

CANDIDATE SUMMARY:
{user_summary}

PHASE CONTEXT (Current Phase):
{phase_json}

TOPIC CONTEXT (Current Topic):
{topic_json}

CURRENT PHASE SUMMARY:
{current_phase_summary_json}

RECENT CHAT CONTEXT (turns in this topic):
{previous_k_turns_json}
"""

    constraints = """
OUTPUT RULES:
Your response MUST have exactly two parts, in this order:

1. BRIDGE (1–2 sentences): Acknowledge something specific from the candidate's prior answer — a claim, a design decision, a technology choice, or a gap you observed. Be natural and conversational. Do NOT use hollow filler ("Great!", "Interesting!"). Make it feel like a real interviewer heard them.
2. QUESTION (1 sentence): The question. It must build on the prior conversation but align with the branch mode instruction.

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
