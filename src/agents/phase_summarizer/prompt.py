from langchain_core.messages import HumanMessage, SystemMessage

from ...models.states.phase_summary import PhaseSummary


def same_phase_summary_prompt(
    current_phase_summary: PhaseSummary,
    current_question: str,
    current_response: str,
) -> list:
    """Build messages for incremental update of an existing phase summary."""
    current_phase_summary_json = current_phase_summary.model_dump_json(indent=2)

    system_content = """
You are a precise interview phase summarization assistant.

ROLE:
Your job is to update an existing phase summary by incorporating the latest question-response turn.
The summary will be used to:
- Generate follow-up questions in the same phase
- Inform the final interview report
- Track what the candidate has demonstrated so far

WHAT TO CAPTURE IN SUMMARIES:
- Skills, competencies, or knowledge demonstrated
- Decisions, trade-offs, reasoning, or problem-solving approach
- Concrete examples, metrics, or outcomes mentioned
- Gaps, uncertainties, or areas needing follow-up
- Behavioral or leadership signals (if relevant)

UPDATE RULES:
- Preserve all important points already in the current phase summary.
- Add only new, relevant information from the latest turn.
- Merge overlapping points; avoid redundancy.
- Keep it concise, factual, and interview-focused.
- Do not invent details.
- Do not include labels, bullets, JSON, or meta commentary.
- Output only the updated phase summary text.
"""

    human_content = f"""
CURRENT PHASE SUMMARY (to update):
{current_phase_summary_json}

LATEST QUESTION:
{current_question}

LATEST RESPONSE:
{current_response}

TASK: Create an updated phase summary that merges the current summary with the new information from the latest turn.
Return only the updated summary text.
"""

    return [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content),
    ]


def phase_change_summary_prompt(
    previous_phase_summary: PhaseSummary,
    current_phase: str,
    current_question: str,
    current_response: str,
) -> list:
    """Build messages for generating the first summary when transitioning to a new phase."""
    previous_phase_summary_json = previous_phase_summary.model_dump_json(indent=2)

    system_content = """
You are a precise interview phase summarization assistant.

ROLE:
Your job is to generate the first summary for a new interview phase when the phase has changed.
The previous phase is complete; this summary starts fresh for the current phase.
The summary will be used to:
- Generate follow-up questions in the new phase
- Inform the final interview report
- Track what the candidate has demonstrated in this phase

WHAT TO CAPTURE IN SUMMARIES:
- Skills, competencies, or knowledge demonstrated
- Decisions, trade-offs, reasoning, or problem-solving approach
- Concrete examples, metrics, or outcomes mentioned
- Gaps, uncertainties, or areas needing follow-up
- Behavioral or leadership signals (if relevant)

PHASE TRANSITION RULES:
- Focus only on the current phase turn content.
- Do NOT carry detailed content from the previous phase summary into this summary.
- You may reference the previous phase briefly for context (e.g., "Following introduction...") but do not duplicate its details.
- This is the first summary for the new phase; keep it focused on the current question-response.
- Keep it concise, factual, and interview-focused.
- Do not invent details.
- Do not include labels, bullets, JSON, or meta commentary.
- Output only the new phase summary text.
"""

    human_content = f"""
PREVIOUS PHASE SUMMARY (for context only; do not copy its content):
{previous_phase_summary_json}

CURRENT PHASE:
{current_phase}

LATEST QUESTION:
{current_question}

LATEST RESPONSE:
{current_response}

TASK: Create a new summary for the current phase based on the latest question and response.
Return only the new phase summary text.
"""

    return [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content),
    ]
