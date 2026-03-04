"""
utils.py — Interview Evaluation Metrics
========================================
All metrics operate on the current turn (question + answer) and optionally
consume the full chat history for context-aware scoring.

Embedding backend
-----------------
Uses Google gemini-embedding-001 via langchain_google_genai.  Set GOOGLE_API_KEY
in env (or via config) for embedding-based metrics.

LLM Critic
----------
Uses the project LLM from src/agents/llm.py (ChatGoogleGenerativeAI) with
SystemMessage and HumanMessage.  Set GOOGLE_API_KEY to enable LLM-graded metrics.
If no key is present those metrics return -1.0 so you can detect and skip them.
"""

from __future__ import annotations

import re
import os
import json
import warnings
from typing import Dict, List, Optional, Any

import numpy as np
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from ..agents.llm import llm

# ─────────────────────────────────────────────────────────────────────────────
# Type aliases
# ─────────────────────────────────────────────────────────────────────────────
Turn    = Dict[str, str]    # {"role": "user"|"assistant", "content": str}
Metrics = Dict[str, Any]


# ═════════════════════════════════════════════════════════════════════════════
# EMBEDDING BACKEND  —  Google gemini-embedding-001
# ═════════════════════════════════════════════════════════════════════════════

_embedder = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")


def embed(text: str) -> np.ndarray:
    """
    Google gemini-embedding-001; returns 1-D float32 np.ndarray, L2-normalised.
    """
    v = np.array(_embedder.embed_query(text), dtype=np.float32)
    norm = np.linalg.norm(v)
    if norm > 0:
        v /= norm
    return v


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom > 0 else 0.0


# ═════════════════════════════════════════════════════════════════════════════
# LLM CRITIC BACKEND  —  project LLM (ChatGoogleGenerativeAI) + SystemMessage/HumanMessage
# ═════════════════════════════════════════════════════════════════════════════

_LLM_AVAILABLE: Optional[bool] = None


def _check_llm() -> bool:
    global _LLM_AVAILABLE
    if _LLM_AVAILABLE is not None:
        return _LLM_AVAILABLE
    _LLM_AVAILABLE = bool(os.environ.get("GOOGLE_API_KEY", ""))
    return _LLM_AVAILABLE


def _llm_critique(system: str, user_content: str) -> Optional[str]:
    """Call project LLM with SystemMessage + HumanMessage; return raw text or None."""
    if not _check_llm():
        return None
    try:
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=user_content),
        ]
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as exc:
        warnings.warn(f"LLM critic failed: {exc}")
        return None


def _parse_llm_json(raw: str, field: str = "score") -> float:
    try:
        obj = json.loads(re.search(r'\{.*\}', raw, re.S).group())
        v = float(obj[field])
        return round(v / 10 if v > 1 else v, 4)
    except Exception:
        matches = re.findall(r"\b(\d+(?:\.\d+)?)\b", raw)
        for m in matches:
            v = float(m)
            if 0 <= v <= 10:
                return round(v / 10 if v > 1 else v, 4)
        return -1.0


# ─────────────────────────────────────────────────────────────────────────────
# History helpers
# ─────────────────────────────────────────────────────────────────────────────

def _prior_answers(history: Optional[List[Turn]]) -> str:
    if not history:
        return ""
    return " ".join(t["content"] for t in history if t.get("role") == "assistant")


def _prior_questions(history: Optional[List[Turn]]) -> str:
    if not history:
        return ""
    return " ".join(t["content"] for t in history if t.get("role") == "user")


def _history_text(history: Optional[List[Turn]], last_n: int = 999) -> str:
    if not history:
        return ""
    window = history[-last_n:]
    return "\n".join(f"{t['role'].upper()}: {t['content']}" for t in window)


# ═════════════════════════════════════════════════════════════════════════════
# PRECOMPILED PATTERNS (shared across metrics)
# ═════════════════════════════════════════════════════════════════════════════

_HEDGE_RE = re.compile(
    r"\b(maybe|probably|i think|not sure|possibly|i believe|might be|"
    r"could be|i guess|sort of|kind of|i suppose|i'm not certain)\b", re.I)

_CAUSAL_RE = re.compile(
    r"\b(because|therefore|thus|hence|as a result|which caused|leading to|"
    r"which meant|so that|in order to)\b", re.I)

_EXAMPLE_RE = re.compile(
    r"\b(for example|for instance|such as|specifically|in particular|"
    r"to illustrate|in my project|we implemented|concretely)\b", re.I)

_QUANTITY_RE = re.compile(
    r"\b\d+\s*(%|x|times|ms|seconds|minutes|hours|gb|mb|tb|requests|users|percent|k|m)\b", re.I)

_SHALLOW_RE = re.compile(
    r"\b(i worked on it|it was fine|did some stuff|helped with|was involved in|"
    r"i know about|i have experience|i've done that|we just used)\b", re.I)

_TECH_RE = re.compile(
    r"\b(python|java|javascript|typescript|go|rust|c\+\+|kotlin|swift|scala|"
    r"docker|kubernetes|aws|gcp|azure|terraform|ansible|helm|"
    r"react|vue|angular|nextjs|svelte|fastapi|django|flask|spring|rails|"
    r"sql|postgres|mysql|mongodb|redis|kafka|rabbitmq|elasticsearch|cassandra|"
    r"tensorflow|pytorch|scikit|huggingface|spark|airflow|dbt|"
    r"graphql|grpc|rest|websocket|nginx|linux|git|ci/cd|jenkins|github.actions|"
    r"prometheus|grafana|datadog|sentry|opentelemetry)\b", re.I)

_ACTION_RE = re.compile(
    r"\b(i (built|designed|led|created|implemented|deployed|developed|wrote|"
    r"refactored|migrated|optimised|introduced|reduced|automated|coordinated|"
    r"negotiated|owned|drove|shipped|launched|established|mentored|scaled))\b", re.I)

_PASSIVE_RE = re.compile(
    r"\b(was done|was built|was implemented|was developed|were created|"
    r"it was decided|things were set up|stuff was)\b", re.I)

_STAR_RE = {
    "situation": re.compile(
        r"\b(project|situation|challenge|context|background|scenario|at the time|"
        r"problem we faced|the issue was)\b", re.I),
    "task": re.compile(
        r"\b(task|responsible for|goal|objective|assigned to|my role was|"
        r"i was asked to|needed to|requirement was)\b", re.I),
    "action": _ACTION_RE,
    "result": re.compile(
        r"\b(result|improved|increased|reduced|achieved|delivered|outcome|impact|"
        r"saved|cut|boosted|grew|shipped|launched|decreased|eliminated)\b", re.I),
}


# ═════════════════════════════════════════════════════════════════════════════
# METRIC 1 — Question–Answer Relevance (QAR)
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# METRIC 2 — Topical Depth Score (TDS)
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# METRIC 3 — Answer Completeness Score (ACS)
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# METRIC 4 — Specificity Score (SS)
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# METRIC 5 — Confidence & Clarity Score (CCS)
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# METRIC 6 — Conversation Coherence Score (COH)
# ═════════════════════════════════════════════════════════════════════════════

def conversation_coherence_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
) -> float:
    """
    Measures how topically connected the current answer is to the recent thread.
    Uses a sliding window of the last 4 turns via embeddings.
    Returns 1.0 when no history exists (nothing to be incoherent with).
    Score: 0.0 – 1.0
    """
    if not chat_history:
        return 1.0

    window   = chat_history[-4:]
    ctx      = " ".join(t["content"] for t in window)
    sim_ctx  = cosine(embed(answer), embed(ctx))
    sim_q    = cosine(embed(answer), embed(question))

    return round(min(max(0.5 * sim_ctx + 0.5 * sim_q, 0.0), 1.0), 4)


# ═════════════════════════════════════════════════════════════════════════════
# METRIC 7 — Verbosity Balance Score (VBS)
# ═════════════════════════════════════════════════════════════════════════════

def verbosity_balance_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
    min_words: int = 40,
    max_words: int = 350,
) -> float:
    """
    Penalises under-explaining (too short) and rambling (too long).
    The upper threshold scales with question complexity (longer question → wider window).
    Score: 0.0 – 1.0
    """
    q_words      = len(re.findall(r'\b\w+\b', question))
    adjusted_max = max_words + q_words * 2
    a_words      = len(re.findall(r'\b\w+\b', answer))

    if a_words < min_words:
        score = a_words / min_words
    elif a_words > adjusted_max:
        score = max(1.0 - (a_words - adjusted_max) / adjusted_max, 0.0)
    else:
        score = 1.0

    return round(score, 4)


# ═════════════════════════════════════════════════════════════════════════════
# METRIC 8 — Behavioral STAR Score
# ═════════════════════════════════════════════════════════════════════════════

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


# ═════════════════════════════════════════════════════════════════════════════
# METRIC 9 — Coverage Progress Contribution (CPC)
# ═════════════════════════════════════════════════════════════════════════════

def coverage_progress_contribution(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
) -> Dict[str, float]:
    """
    How much does this turn advance interview coverage?
    Turn CPC = QAR × ACS.  Cumulative = rolling average across all turns.
    Score: 0.0 – 1.0
    """
    qar      = question_answer_relevance(question, answer, chat_history)
    acs      = answer_completeness_score(question, answer, chat_history)
    turn_cpc = round(qar * acs, 4)

    if not chat_history:
        return {"CPC_turn": turn_cpc, "CPC_cumulative": turn_cpc}

    # Pair up prior turns
    prior_scores: List[float] = []
    q_buf: List[str] = []
    for t in chat_history:
        if t["role"] == "user":
            q_buf.append(t["content"])
        elif t["role"] == "assistant" and q_buf:
            q_prev = q_buf.pop(0)
            pqar   = question_answer_relevance(q_prev, t["content"])
            pacs   = answer_completeness_score(q_prev, t["content"])
            prior_scores.append(pqar * pacs)

    all_scores   = prior_scores + [turn_cpc]
    cumulative   = round(sum(all_scores) / len(all_scores), 4)
    return {"CPC_turn": turn_cpc, "CPC_cumulative": cumulative}


# ═════════════════════════════════════════════════════════════════════════════
# LLM METRIC 10 — Factual Accuracy & Reasoning Quality (FARQ)
# ═════════════════════════════════════════════════════════════════════════════

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
# LLM METRIC 11 — Communication Clarity Score (COMM)
# ═════════════════════════════════════════════════════════════════════════════

def communication_clarity_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
) -> float:
    """
    LLM judge: is the answer well-structured, easy to follow, and
    appropriately concise?  Returns -1.0 if LLM unavailable.
    Score: 0.0 – 1.0
    """
    system = "You are evaluating interview communication quality. Rate how clearly and effectively the answer communicates ideas (0.0 to 1.0). Consider: structure, ease of following the argument, appropriate use of jargon, and whether it is concise yet complete. Respond ONLY with this JSON: {\"score\": <float 0.0-1.0>, \"reason\": \"<one sentence>\"}"
    user_content = f"""QUESTION: {question}
ANSWER: {answer}"""

    raw = _llm_critique(system, user_content)
    return -1.0 if raw is None else _parse_llm_json(raw)


# ═════════════════════════════════════════════════════════════════════════════
# LLM METRIC 12 — Seniority Signal Score (SSS)
# ═════════════════════════════════════════════════════════════════════════════

def seniority_signal_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
) -> float:
    """
    LLM judge: does the answer reflect senior-level thinking — explicit tradeoffs,
    system-level perspective, ownership, impact on team / org?
    Returns -1.0 if LLM unavailable.
    Score: 0.0 – 1.0
    """
    history_block = (f"\n\nPrior conversation:\n{_history_text(chat_history, last_n=4)}"
                     if chat_history else "")
    system = "You are a senior engineering hiring manager. Rate how strongly the answer signals senior-level engineering judgment (0.0 to 1.0). Senior signals: explicit tradeoff discussion, edge-case awareness, org/team impact, system-level thinking, decision-making ownership, mentoring others. Respond ONLY with this JSON: {\"score\": <float 0.0-1.0>, \"reason\": \"<one sentence>\"}"
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


# ═════════════════════════════════════════════════════════════════════════════
# MASTER CALCULATOR
# ═════════════════════════════════════════════════════════════════════════════

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
    # m["COH"] = conversation_coherence_score(question, answer, chat_history)
    # m["VBS"] = verbosity_balance_score(question, answer, chat_history)

    # cpc = coverage_progress_contribution(question, answer, chat_history)
    # m["CPC_turn"]       = cpc["CPC_turn"]
    # m["CPC_cumulative"] = cpc["CPC_cumulative"]

    if behavioral_phase:
        star = star_score(question, answer, chat_history)
        m["STAR_turn"]       = star["STAR_turn"]
        m["STAR_cumulative"] = star["STAR_cumulative"]
        m["STAR_components"] = star["components_turn"]

    # LLM-judged metrics
    if run_llm_metrics:
        m["FARQ"] = factual_accuracy_reasoning_quality(question, answer, chat_history)
        # m["COMM"] = communication_clarity_score(question, answer, chat_history)
        # m["SSS"]  = seniority_signal_score(question, answer, chat_history)
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