from typing import List
import json
from langchain_core.messages import HumanMessage, SystemMessage

from ...models.states.turn import Turn


def router_prompt(
    chat_history: List[Turn],
    current_topic_id: str,
    current_topic_name: str,
    current_phase_name: str,
    k: int,
    max_question_count: int,
    previous_phase_summary: str = "",
) -> list:
    """
    Build messages for the router agent that decides the routing intent
    (advance_topic, dependent_followup, dependent_new_angle) for the current topic,
    using current phase turns, the topic question counter, and optional previous phase summary.
    """
    chat_history_json = json.dumps([t.model_dump() for t in chat_history], indent=2, ensure_ascii=False)

    system_content = """You are an expert routing assistant for an adaptive interview question generator.

YOUR GOAL
Given candidate context and chat history of the current phase, select the next routing action (intent) and focus area. You will be provided with the "Current Topic Name" representing the active topic under evaluation.

METRICS INTERPRETATION GUIDE
Each turn in the chat history contains a "metrics" field with the following numerical scores (ranging from 0.0 to 1.0) and flags:
- QAR (Question-Answer Relevance): Relevance and alignment of the candidate's answer to the question. Low scores (< 0.6) indicate evasion or off-topic rambling.
- TDS (Topical Depth Score): Quality of depth, causal reasoning (e.g., use of 'because', 'therefore'), and concrete examples/numbers. Low scores (< 0.6) indicate shallow or superficial answers.
- ACS (Answer Completeness Score): Sentence relevance and length adequacy (~80+ words). Low scores indicate very short or incomplete answers.
- SS (Specificity Score): Mention of named technologies, tools, and quantified metrics/outcomes. Low scores indicate vague, generic claims.
- CCS (Confidence & Clarity Score): Ownership-oriented language (e.g., 'I built', 'I led') vs. passive voice ('was built') or hedging ('maybe', 'I think'). Low scores indicate a lack of confidence or clear ownership.
- FARQ (Factual Accuracy & Reasoning Quality): Coherence of reasoning and technical accuracy of claims.
- RFD (Red Flag Detector): Score indicating potential red flags like blame-shifting, avoidance, contradictions, or exaggeration. Ideal is 1.0 (no flags); lower scores indicate warning signs.
- RFD_flags: List of specific warning/red flags detected in the turn.

How to use metrics for Routing Decisions:
- Probe Gaps (dependent_followup): If the last turn's metrics (especially QAR, TDS, SS, CCS, or RFD) are low, it indicates significant gaps, hedging, or red flags on the current topic (indicated by "Current Topic Name"). Select "dependent_followup" to probe these specific areas (the "focus" field should specify the gap).
- Explore Depth (dependent_new_angle): If the metrics are high (e.g., >= 0.7 or 0.8 across the board) indicating a solid, specific, and confident answer, but we want to test a different sub-topic or tradeoff on the same topic (indicated by "Current Topic Name"), select "dependent_new_angle" (the "focus" field should specify the new angle).
- Move On (advance_topic): If metrics are consistently high, or the candidate has struggled and the question counter is reaching the limit, select "advance_topic".

INTENTS
1. "advance_topic"
   - Use this when:
     - The candidate has sufficiently demonstrated their skills on the current topic (Current Topic Name).
     - OR the question counter indicates we should move on to maintain interview pace.
     - CRITICAL: Always keep the question counter in mind. If the candidate is stuck, or has already had multiple questions on this topic, do NOT get stuck in a loop; select "advance_topic" to advance the interview.
2. "dependent_followup"
   - Use this when the candidate's last answer shows gaps, shallow reasoning, or potential red flags on this topic (Current Topic Name) that need to be probed directly.
   - The "focus" should specify what exact claim or gap to probe.
3. "dependent_new_angle"
   - Use this when the candidate answered the last question well, but we want to explore a different facet, scenario, or practical tradeoff of the same topic (Current Topic Name) before moving on.
   - The "focus" should specify what angle to explore.

DECISION GUIDELINES
- Do NOT use hard comparisons or formulas. Evaluate qualitatively.
- Be mindful of the question counter: if the counter is close to or has reached the soft limit, lean heavily towards "advance_topic" unless there is an extremely critical gap to follow up on.

OUTPUT FORMAT
You MUST return ONLY a single JSON object. Do NOT wrap it in code fences (e.g. ```json ... ```) or include any conversational filler.
{
  "intent": "advance_topic | dependent_followup | dependent_new_angle",
  "focus": "Short phrase describing the probe/angle to focus on (can be empty if intent is advance_topic)"
}
"""

    context_lines = [
        f"Current Phase: {current_phase_name}",
        f"Current Topic ID: {current_topic_id}",
        f"Current Topic Name: {current_topic_name}",
        f"Questions asked on this topic so far: {k} (Guideline soft limit: {max_question_count})",
    ]

    if previous_phase_summary:
        context_lines.append(f"\nSummary of the Previous Completed Phase (for context):\n{previous_phase_summary}")

    context_lines.append(f"\nChat History for Current Phase (newest last):\n{chat_history_json}")

    human_content = "\n".join(context_lines) + "\n\nSelect the next intent and focus. Return ONLY the raw JSON object."

    return [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content),
    ]