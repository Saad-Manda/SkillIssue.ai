import re
import math
from collections import Counter
from typing import List, Dict, Any, Optional

# ─────────────────────────────────────────────
# Type alias for a single chat turn
# ─────────────────────────────────────────────
Turn = Dict[str, str]  # {"role": "user"|"assistant", "content": str}


############################################
# Helper Utilities
############################################

def tokenize(text: str) -> List[str]:
    return re.findall(r'\b\w+\b', text.lower())


def sentence_split(text: str) -> List[str]:
    return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]


def cosine_similarity(vec1: Counter, vec2: Counter) -> float:
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum(vec1[x] * vec2[x] for x in intersection)
    sum1 = sum(v ** 2 for v in vec1.values())
    sum2 = sum(v ** 2 for v in vec2.values())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    return numerator / denominator if denominator else 0.0


def extract_all_answers(chat_history: List[Turn]) -> str:
    """Concatenate all assistant answers from history."""
    return " ".join(t["content"] for t in chat_history if t.get("role") == "assistant")


def extract_all_questions(chat_history: List[Turn]) -> str:
    """Concatenate all user questions from history."""
    return " ".join(t["content"] for t in chat_history if t.get("role") == "user")


############################################
# 1. Question–Answer Relevance Score (QAR)
############################################
# Measures how well the current answer addresses the current question.
# Optionally uses chat history to check if the question was already addressed
# in a previous turn (context carryover).

def question_answer_relevance(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None
) -> float:
    q_vec = Counter(tokenize(question))
    a_vec = Counter(tokenize(answer))

    semantic_sim = cosine_similarity(q_vec, a_vec)
    keyword_overlap = len(set(q_vec.keys()) & set(a_vec.keys())) / max(len(set(q_vec.keys())), 1)

    score = 0.6 * semantic_sim + 0.4 * keyword_overlap

    # Bonus: if question keywords were already addressed in prior turns,
    # the current answer continuing them gets a small coherence lift.
    if chat_history:
        prior_answers = extract_all_answers(chat_history)
        prior_vec = Counter(tokenize(prior_answers))
        carryover = cosine_similarity(q_vec, prior_vec)
        score = score * 0.85 + carryover * 0.15  # slight blend

    return round(min(score, 1.0), 4)


############################################
# 2. Topical Depth Score (TDS)
############################################
# Measures domain depth of the current answer.
# With history: rewards answers that go DEEPER than prior answers
# (adds a novelty bonus if current answer introduces new domain tokens).

DOMAIN_MARKERS = {
    "because", "internally", "architecture", "tradeoff",
    "complexity", "performance", "scalable", "optimize",
    "latency", "throughput", "concurrency", "bottleneck",
    "algorithm", "cache", "indexing", "schema", "pipeline",
}

def topical_depth_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None
) -> float:
    tokens = tokenize(answer)
    total_words = len(tokens) or 1

    domain_density = sum(1 for t in tokens if t in DOMAIN_MARKERS) / total_words
    causal_markers = len([t for t in tokens if t in {"because", "therefore", "thus", "hence"}]) / total_words
    example_presence = 1.0 if re.search(
        r"\b(for example|for instance|in my project|we implemented|such as|consider)\b",
        answer.lower()
    ) else 0.0

    score = (0.4 * domain_density + 0.3 * causal_markers + 0.3 * example_presence)

    # History novelty: reward new domain tokens not seen in prior turns
    if chat_history:
        prior_tokens = set(tokenize(extract_all_answers(chat_history)))
        new_domain_tokens = [t for t in tokens if t in DOMAIN_MARKERS and t not in prior_tokens]
        novelty_bonus = min(len(new_domain_tokens) / max(len(DOMAIN_MARKERS), 1), 0.2)
        score += novelty_bonus

    return round(min(score * 5, 1.0), 4)


############################################
# 3. Technical Correctness Proxy (TCP)
############################################
# Penalises hedging/uncertainty language.
# With history: repeated uncertainty across turns compounds the penalty.

def technical_correctness_proxy(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None
) -> float:
    contradiction_patterns = [
        r"\bi don'?t know\b",
        r"\bnot sure\b",
        r"\bmaybe\b",
        r"\bi'?m not certain\b",
        r"\bcould be wrong\b",
    ]

    hits = sum(bool(re.search(p, answer.lower())) for p in contradiction_patterns)
    penalty = hits * 0.2

    # History: if the candidate was uncertain in prior turns too, add a small extra penalty
    if chat_history:
        prior_text = extract_all_answers(chat_history).lower()
        prior_hits = sum(bool(re.search(p, prior_text)) for p in contradiction_patterns)
        penalty += min(prior_hits * 0.05, 0.2)  # capped carry-forward penalty

    return round(max(1.0 - penalty, 0.0), 4)


############################################
# 4. Specificity Score (SS)
############################################
# Rewards concrete numbers and named tools/technologies.
# With history: avoids rewarding repeated mentions of the same tools
# across turns (diminishing returns).

TECH_PATTERN = r"\b(python|docker|aws|react|sql|tensorflow|kubernetes|redis|kafka|postgres|mongodb|fastapi|celery|nginx|graphql|typescript|go|rust|java|spring|django)\b"

def specificity_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None
) -> float:
    tokens = tokenize(answer)
    total_words = len(tokens) or 1

    numeric_tokens = len(re.findall(r"\b\d+(\.\d+)?%?\b", answer))
    tool_mentions = re.findall(TECH_PATTERN, answer.lower())

    # History: only count tools not already mentioned in prior turns
    if chat_history:
        prior_tools = set(re.findall(TECH_PATTERN, extract_all_answers(chat_history).lower()))
        new_tools = [t for t in tool_mentions if t not in prior_tools]
        effective_tools = len(new_tools)
    else:
        effective_tools = len(tool_mentions)

    score = (numeric_tokens + effective_tools) / total_words
    return round(min(score * 10, 1.0), 4)


############################################
# 5. Confidence vs Uncertainty Score (CUS)
############################################
# Measures how confidently the candidate answers.
# With history: flags a pattern of consistent uncertainty across all turns.

HEDGE_WORDS = {"maybe", "probably", "i think", "not sure", "possibly", "i believe", "might be"}

def confidence_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None
) -> float:
    sentences = sentence_split(answer)
    total_sentences = len(sentences) or 1

    hedge_count = sum(1 for h in HEDGE_WORDS if h in answer.lower())
    penalty = hedge_count / total_sentences

    if chat_history:
        prior_text = extract_all_answers(chat_history).lower()
        prior_hedge = sum(1 for h in HEDGE_WORDS if h in prior_text)
        # Normalise by number of prior turns
        prior_turns = sum(1 for t in chat_history if t.get("role") == "assistant")
        if prior_turns:
            pattern_penalty = min(prior_hedge / (prior_turns * len(HEDGE_WORDS)), 0.3)
            penalty += pattern_penalty

    return round(max(1.0 - penalty, 0.0), 4)


############################################
# 6. Resume Alignment Score (RAS)
############################################
# Checks how much of the current answer references the candidate's resume.
# With history: looks at cumulative resume coverage across all answers so far.

def resume_alignment_score(
    question: str,
    answer: str,
    resume_entities: List[str],
    chat_history: Optional[List[Turn]] = None
) -> Dict[str, float]:
    lower_entities = [e.lower() for e in resume_entities]
    answer_tokens = set(tokenize(answer))

    turn_overlap = len(answer_tokens & set(lower_entities)) / max(len(lower_entities), 1)

    cumulative_overlap = turn_overlap
    if chat_history:
        all_text = extract_all_answers(chat_history) + " " + answer
        all_tokens = set(tokenize(all_text))
        cumulative_overlap = len(all_tokens & set(lower_entities)) / max(len(lower_entities), 1)

    return {
        "RAS_turn": round(turn_overlap, 4),
        "RAS_cumulative": round(cumulative_overlap, 4),
    }


############################################
# 7. Coverage Progress Contribution (CPC)
############################################
# Combined metric: how much this turn advances coverage of the topic.
# With history: tracks cumulative topic coverage across turns.

def coverage_progress_contribution(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None
) -> Dict[str, float]:
    qar = question_answer_relevance(question, answer, chat_history)
    tds = topical_depth_score(question, answer, chat_history)
    turn_cpc = round(qar * tds, 4)

    cumulative_cpc = turn_cpc
    if chat_history:
        # Simple proxy: average QAR*TDS across all prior turns + current
        prior_scores = []
        questions = [t["content"] for t in chat_history if t.get("role") == "user"]
        answers   = [t["content"] for t in chat_history if t.get("role") == "assistant"]
        for q, a in zip(questions, answers):
            prior_qar = question_answer_relevance(q, a)
            prior_tds = topical_depth_score(q, a)
            prior_scores.append(prior_qar * prior_tds)
        all_scores = prior_scores + [turn_cpc]
        cumulative_cpc = round(sum(all_scores) / len(all_scores), 4)

    return {
        "CPC_turn": turn_cpc,
        "CPC_cumulative": cumulative_cpc,
    }


############################################
# 8. Behavioral STAR Score
############################################
# Checks if the answer follows the Situation-Task-Action-Result structure.
# With history: checks whether STAR components are spread across turns
# (partial STAR in each turn is valid in multi-turn interviews).

def star_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None
) -> Dict[str, float]:
    def _star_components(text: str) -> Dict[str, bool]:
        t = text.lower()
        return {
            "situation": bool(re.search(r"\b(project|situation|challenge|context|background)\b", t)),
            "task":      bool(re.search(r"\b(task|responsible|goal|objective|assigned)\b", t)),
            "action":    bool(re.search(r"\b(i did|we implemented|i developed|i built|i led|i created|i designed)\b", t)),
            "result":    bool(re.search(r"\b(result|improved|increased|reduced|achieved|delivered|outcome)\b", t)),
        }

    turn_components = _star_components(answer)
    turn_score = round(sum(turn_components.values()) / 4, 4)

    cumulative_score = turn_score
    if chat_history:
        # Merge components across all turns — partial STAR across turns still counts
        combined_text = extract_all_answers(chat_history) + " " + answer
        combined_components = _star_components(combined_text)
        cumulative_score = round(sum(combined_components.values()) / 4, 4)

    return {
        "STAR_turn": turn_score,
        "STAR_cumulative": cumulative_score,
        "components": turn_components,
    }


############################################
# 9. Conversation Coherence Score (NEW)
############################################
# Measures how well the current answer connects to the prior conversation.
# Only meaningful when chat_history is provided.

def conversation_coherence_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None
) -> float:
    if not chat_history:
        return 1.0  # no history to be incoherent with

    prior_context = extract_all_questions(chat_history) + " " + extract_all_answers(chat_history)
    answer_vec  = Counter(tokenize(answer))
    context_vec = Counter(tokenize(prior_context))

    return round(cosine_similarity(answer_vec, context_vec), 4)


############################################
# 10. Verbosity Penalty Score (NEW)
############################################
# Penalises answers that are either too short (under-explained)
# or excessively long (padding/rambling).
# With history: flags if verbosity pattern is consistent across turns.

def verbosity_score(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
    min_words: int = 30,
    max_words: int = 300
) -> float:
    tokens = tokenize(answer)
    n = len(tokens)

    if n < min_words:
        score = n / min_words          # ramps from 0 → 1
    elif n > max_words:
        excess = n - max_words
        score = max(1.0 - (excess / max_words), 0.0)
    else:
        score = 1.0

    return round(score, 4)


############################################
# Master Metric Calculator
############################################

def calculate_turn_metrics(
    question: str,
    answer: str,
    chat_history: Optional[List[Turn]] = None,
    resume_entities: Optional[List[str]] = None,
    behavioral_phase: bool = False,
) -> Dict[str, Any]:
    """
    Calculate all metrics for the current turn.

    Args:
        question:         The interviewer's current question.
        answer:           The candidate's current answer.
        chat_history:     List of prior turns as {"role": ..., "content": ...} dicts.
                          Pass None or [] if this is the first turn.
        resume_entities:  List of skills/tools extracted from the resume (optional).
        behavioral_phase: Set True when the interview is in the behavioral/STAR phase.

    Returns:
        Dict of metric names → scores (floats or nested dicts).
    """
    metrics: Dict[str, Any] = {}

    metrics["QAR"]  = question_answer_relevance(question, answer, chat_history)
    metrics["TDS"]  = topical_depth_score(question, answer, chat_history)
    metrics["TCP"]  = technical_correctness_proxy(question, answer, chat_history)
    metrics["SS"]   = specificity_score(question, answer, chat_history)
    metrics["CUS"]  = confidence_score(question, answer, chat_history)
    metrics["CCS"]  = conversation_coherence_score(question, answer, chat_history)
    metrics["VS"]   = verbosity_score(question, answer, chat_history)

    cpc = coverage_progress_contribution(question, answer, chat_history)
    metrics["CPC_turn"]       = cpc["CPC_turn"]
    metrics["CPC_cumulative"] = cpc["CPC_cumulative"]

    if resume_entities:
        ras = resume_alignment_score(question, answer, resume_entities, chat_history)
        metrics["RAS_turn"]       = ras["RAS_turn"]
        metrics["RAS_cumulative"] = ras["RAS_cumulative"]
    else:
        metrics["RAS_turn"]       = 0.0
        metrics["RAS_cumulative"] = 0.0

    if behavioral_phase:
        star = star_score(question, answer, chat_history)
        metrics["STAR_turn"]       = star["STAR_turn"]
        metrics["STAR_cumulative"] = star["STAR_cumulative"]
        metrics["STAR_components"] = star["components"]

    return metrics


############################################
# Quick demo
############################################

if __name__ == "__main__":
    history: List[Turn] = [
        {"role": "user",      "content": "Tell me about your background."},
        {"role": "assistant", "content": "I have 5 years of experience in backend development using Python and AWS."},
        {"role": "user",      "content": "What databases have you worked with?"},
        {"role": "assistant", "content": "I've worked with Postgres and MongoDB. We used Redis for caching to improve performance."},
    ]

    current_question = "Can you describe a scalable architecture you designed?"
    current_answer   = (
        "In my last project we implemented a microservices architecture on Kubernetes. "
        "Because we had high throughput requirements, I designed a pipeline with Kafka "
        "for async processing, which reduced latency by 40%. For example, the order service "
        "was decoupled from payment processing to improve scalability."
    )

    resume = ["python", "aws", "kubernetes", "kafka", "postgres", "redis", "docker"]

    results = calculate_turn_metrics(
        question=current_question,
        answer=current_answer,
        chat_history=history,
        resume_entities=resume,
        behavioral_phase=True,
    )

    print("=== Turn Metrics ===")
    for k, v in results.items():
        print(f"  {k}: {v}")