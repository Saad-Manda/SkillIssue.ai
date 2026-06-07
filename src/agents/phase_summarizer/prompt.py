import json
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage

from ...models.states.phase_summary import PhaseSummary
from ...models.states.turn import Turn


def phase_summary_prompt(
    phase_name: str,
    completed_phase_turns: List[Turn],
    prior_phase_summaries: List[PhaseSummary],
) -> list:
    """Build messages for summarizing a completed phase using all its turns and prior phase summaries."""
    completed_phase_turns_json = json.dumps([t.model_dump() for t in completed_phase_turns], indent=2, ensure_ascii=False)
    prior_summaries_json = json.dumps([s.model_dump() if hasattr(s, "model_dump") else s for s in prior_phase_summaries], indent=2, ensure_ascii=False)

    system_content = """You are an expert interview phase summarization assistant.

YOUR ROLE
Generate a comprehensive, high-quality evaluation summary of the interview phase that has just completed. This summary will be used by the question generator in subsequent phases to build upon context, and will also help inform the final readiness report.

WHAT TO CAPTURE:
- Skills, competencies, and depth of technical/conceptual knowledge demonstrated on topics covered in this phase.
- Design decisions, trade-offs, reasoning, or problem-solving approaches explained by the candidate.
- Concrete examples, metrics, achievements, or project details mentioned.
- Specific gaps, uncertainties, evasions, or flags that warrant attention.
- Tone, communication style, or behavioral patterns (especially if this was a behavioral or experience phase).

OUTPUT FORMAT:
Output only the raw summary text. Do NOT include markdown styling (like headings, bullet points), labels, JSON, or meta-commentary. Keep it clean, professional, and factual.
"""

    human_content = f"""Completed Phase Name: {phase_name}

Prior Phase Summaries (for context of the candidate's journey so far):
{prior_summaries_json}

All turns in the completed phase (newest last):
{completed_phase_turns_json}

Please generate the summary of the completed phase now. Return only the raw summary text.
"""

    return [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content),
    ]
