import re
import json
from typing import List, Optional, Any, Dict
from .utils import embed, cosine, _prior_answers, _prior_questions, _history_text, _llm_critique, _parse_llm_json
from .utils import _CAUSAL_RE, _ACTION_RE, _EXAMPLE_RE, _HEDGE_RE,  _PASSIVE_RE, _QUANTITY_RE, _SHALLOW_RE, _STAR_RE, _TECH_RE
from .utils import Turn, Metrics

def question_answer_relevance(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
) -> float:
    """
    Semantic similarity between question and answer via embeddings.
    With history: blends in how well the answer bridges the ongoing thread.
    Score: 0.0 – 1.0
    """
    q_emb = embed(question)
    a_emb = embed(answer)
    direct = cosine(q_emb, a_emb)

    if chat_history:
        ctx      = _prior_answers(chat_history) + " " + _prior_questions(chat_history)
        ctx_emb  = embed(ctx)
        bridge   = cosine(a_emb, ctx_emb)
        score    = 0.75 * direct + 0.25 * bridge
    else:
        score = direct

    return round(min(max(score, 0.0), 1.0), 4)


def topical_depth_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
) -> float:
    """
    Rewards causal reasoning, concrete examples, and quantified claims.
    Penalises shallow filler phrases.
    With history: adds an embedding-novelty bonus for genuinely new content.
    Score: 0.0 – 1.0
    """
    total = max(len(re.findall(r'\b\w+\b', answer)), 1)

    causal_density   = len(_CAUSAL_RE.findall(answer))   / total
    example_density  = len(_EXAMPLE_RE.findall(answer))  / total
    quantity_density = len(_QUANTITY_RE.findall(answer))  / total
    shallow_hits     = len(_SHALLOW_RE.findall(answer))

    base = (0.35 * min(causal_density   * 25, 1.0) +
            0.35 * min(example_density  * 25, 1.0) +
            0.30 * min(quantity_density * 15, 1.0))
    base = max(base - shallow_hits * 0.12, 0.0)

    if chat_history:
        prior = _prior_answers(chat_history)
        if prior.strip():
            novelty = 1.0 - cosine(embed(answer), embed(prior))
            base = 0.80 * base + 0.20 * novelty

    return round(min(base, 1.0), 4)


def answer_completeness_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
) -> float:
    """
    Fraction of answer sentences that are semantically on-topic + length adequacy.
    With history: penalises answers that are mostly redundant with prior turns.
    Score: 0.0 – 1.0
    """
    q_emb     = embed(question)
    sentences = [s.strip() for s in re.split(r'[.!?]+', answer) if s.strip()]
    if not sentences:
        return 0.0

    sims     = [cosine(embed(s), q_emb) for s in sentences]
    on_topic = sum(1 for s in sims if s > 0.10) / len(sims)

    word_count   = len(re.findall(r'\b\w+\b', answer))
    length_score = min(word_count / 80, 1.0)

    score = 0.60 * on_topic + 0.40 * length_score

    if chat_history:
        prior = _prior_answers(chat_history)
        if prior.strip():
            redundancy = cosine(embed(answer), embed(prior))
            score *= (1.0 - 0.25 * redundancy)

    return round(min(max(score, 0.0), 1.0), 4)


def specificity_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
) -> float:
    """
    Rewards named technologies + quantified claims.
    Diminishing returns for tools already mentioned in prior turns.
    Score: 0.0 – 1.0
    """
    total   = max(len(re.findall(r'\b\w+\b', answer)), 1)
    numbers = re.findall(r"\b\d+(?:\.\d+)?(?:%|x|ms|gb|mb|k|m)?\b", answer.lower())
    tools   = [t.lower() for t in _TECH_RE.findall(answer)]

    if chat_history:
        prior_tools = {t.lower() for t in _TECH_RE.findall(_prior_answers(chat_history))}
        new_tools   = [t for t in tools if t not in prior_tools]
        tool_count  = len(new_tools) + 0.3 * (len(tools) - len(new_tools))
    else:
        tool_count = len(tools)

    tool_score   = min(tool_count   / max(total * 0.08, 1), 1.0)
    number_score = min(len(numbers) / max(total * 0.05, 1), 1.0)

    return round(0.55 * tool_score + 0.45 * number_score, 4)


def confidence_clarity_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
) -> float:
    """
    Rewards assertive first-person ownership; penalises hedging and passive voice.
    With history: compounds penalty for a sustained pattern of uncertainty.
    Score: 0.0 – 1.0
    """
    sentences = [s.strip() for s in re.split(r'[.!?]+', answer) if s.strip()]
    total_s   = max(len(sentences), 1)

    hedge_rate   = len(_HEDGE_RE.findall(answer))   / total_s
    passive_rate = len(_PASSIVE_RE.findall(answer)) / total_s
    action_rate  = len(_ACTION_RE.findall(answer))  / total_s

    score = max(1.0 - hedge_rate * 0.25 - passive_rate * 0.15, 0.0)
    score = min(score + min(action_rate * 0.20, 0.30), 1.0)

    if chat_history:
        prior  = _prior_answers(chat_history)
        prior_s = max(len(re.split(r'[.!?]+', prior)), 1)
        prior_hedge_rate = len(_HEDGE_RE.findall(prior)) / prior_s
        score *= (1.0 - 0.15 * prior_hedge_rate)

    return round(min(max(score, 0.0), 1.0), 4)


def star_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
) -> Dict[str, Any]:
    """
    Checks Situation-Task-Action-Result structure in the current answer and
    cumulatively across the full conversation (STAR may span multiple turns).
    Score: 0.0 – 1.0 (proportion of 4 components present).
    """
    def _check(text: str) -> Dict[str, bool]:
        return {k: bool(p.search(text)) for k, p in _STAR_RE.items()}

    turn_components = _check(answer)
    turn_score      = round(sum(turn_components.values()) / 4, 4)

    if chat_history:
        all_text = _prior_answers(chat_history) + " " + answer
        cum_comp = _check(all_text)
    else:
        cum_comp = turn_components.copy()

    return {
        "STAR_turn":       turn_score,
        "STAR_cumulative": round(sum(cum_comp.values()) / 4, 4),
        "components_turn": turn_components,
    }



def factual_accuracy_reasoning_quality(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
) -> float:
    """
    LLM judge: are technical claims correct and is the reasoning logically sound?
    Returns -1.0 if GOOGLE_API_KEY is not set.
    Score: 0.0 – 1.0
    """
    history_block = (f"\n\nConversation so far:\n{_history_text(chat_history, last_n=4)}"
                     if chat_history else "")
    system = "You are an expert technical interviewer. Evaluate the factual accuracy and logical correctness of the answer. Are technical claims correct? Is the reasoning coherent and free of contradictions? Does the candidate show an accurate mental model? Respond ONLY with this JSON (no extra text): {\"score\": <float 0.0-1.0>, \"reason\": \"<one sentence>\"}"
    user_content = f"""{history_block}

QUESTION: {question}
ANSWER: {answer}"""

    raw = _llm_critique(system, user_content)
    return -1.0 if raw is None else _parse_llm_json(raw)



# ═════════════════════════════════════════════════════════════════════════════
# LLM METRIC 13 — Red Flag Detector (RFD)
# ═════════════════════════════════════════════════════════════════════════════

def red_flag_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
) -> Dict[str, Any]:
    """
    LLM judge: detects blame-shifting, avoidance, contradictions with prior turns,
    or implausible exaggeration.
    Returns {"score": -1.0, "flags": []} if LLM is unavailable.
    Score: 0.0 (many red flags) – 1.0 (no red flags)
    """
    history_block = (f"\n\nFull conversation:\n{_history_text(chat_history)}"
                     if chat_history else "")
    system = "You are an experienced interviewer watching for warning signs. Identify any red flags: blaming teammates/management without personal responsibility, refusing to discuss a failure, contradicting something said earlier, obvious exaggeration or implausible claims, completely avoiding the question. Respond ONLY with this JSON: {\"score\": <float 0.0-1.0 where 1.0 = zero red flags>, \"flags\": [<short flag descriptions or empty list>]}"
    user_content = f"""{history_block}

QUESTION: {question}
ANSWER: {answer}"""

    raw = _llm_critique(system, user_content)
    if raw is None:
        return {"score": -1.0, "flags": []}
    try:
        obj   = json.loads(re.search(r'\{.*\}', raw, re.S).group())
        score = float(obj.get("score", -1.0))
        score = round(score / 10 if score > 1 else score, 4)
        return {"score": score, "flags": obj.get("flags", [])}
    except Exception:
        return {"score": _parse_llm_json(raw), "flags": []}


def calculate_turn_metrics(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
    behavioral_phase: bool = False,
    run_llm_metrics: bool = True,
) -> Metrics:
    """
    Compute all metrics for the current interview turn.

    Args:
        question         : Interviewer's current question.
        answer           : Candidate's current answer.
        chat_history     : Prior turns as list of {"role", "content"} dicts.
                           Pass None or [] for the first turn.
        behavioral_phase : Set True during STAR / behavioural questions.
        run_llm_metrics  : Set False to skip LLM API calls (faster / offline).

    Returns:
        Dict of metric_name → score.
        LLM metrics return -1.0 when GOOGLE_API_KEY is not configured.
    """
    m: Metrics = {}

    # Embedding-based metrics
    m["QAR"] = question_answer_relevance(question, answer, chat_history)
    m["TDS"] = topical_depth_score(question, answer, chat_history)
    m["ACS"] = answer_completeness_score(question, answer, chat_history)
    m["SS"]  = specificity_score(question, answer, chat_history)
    m["CCS"] = confidence_clarity_score(question, answer, chat_history)

    if behavioral_phase:
        star = star_score(question, answer, chat_history)
        m["STAR_turn"]       = star["STAR_turn"]
        m["STAR_cumulative"] = star["STAR_cumulative"]
        m["STAR_components"] = star["components_turn"]

    # LLM-judged metrics
    if run_llm_metrics:
        m["FARQ"] = factual_accuracy_reasoning_quality(question, answer, chat_history)
        rfd       = red_flag_score(question, answer, chat_history)
        m["RFD"]       = rfd["score"]
        m["RFD_flags"] = rfd["flags"]

    return m


# ─────────────────────────────────────────────────────────────────────────────
# Quick smoke-test
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    history: List[Turn] = [
        {"role": "user",      "content": "Tell me about your background."},
        {"role": "assistant", "content": "I have 5 years of backend experience with Python and AWS."},
        {"role": "user",      "content": "What databases have you used?"},
        {"role": "assistant", "content": "Worked with Postgres and MongoDB; used Redis for caching."},
    ]

    q = "Describe a scalable architecture you designed end to end."
    a = (
        "In my last role I led the redesign of our order-processing service on Kubernetes. "
        "Because we were hitting 10 000 requests/second, I introduced Kafka for async event "
        "streaming, which decoupled the payment service from inventory. "
        "This reduced average p95 latency by 40% and cut infrastructure costs by 20%. "
        "For example, during Black Friday we handled 3x normal traffic with zero downtime."
    )

    results = calculate_turn_metrics(
        question=q,
        answer=a,
        chat_history=history,
        behavioral_phase=True,
        run_llm_metrics=True,   # flip to True once GOOGLE_API_KEY is set
    )

    print("=== Turn Metrics ===")
    for k, v in results.items():
        print(f"  {k:22s}: {v}")