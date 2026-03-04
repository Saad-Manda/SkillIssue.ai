"""
Metrics differentiation demo — test_metrics_demo.py
===================================================
Uses only methods from test2_metrics.py to show how each metric differentiates
across positive, negative, ambiguous, and confusing answer types.

Run from project root (use project venv for deps):
  .venv/bin/python -m src.tests.test_metrics_demo
  # or:  python -m src.tests.test_metrics_demo
Set RUN_LLM_METRICS=1 and GOOGLE_API_KEY to include LLM metrics (FARQ, COMM, SSS, RFD).
"""

from __future__ import annotations

import os
import sys
from typing import List, Dict, Any, Tuple

# Import all metric functions from test2_metrics (same package)
from .test2_metrics import (
    question_answer_relevance,
    topical_depth_score,
    answer_completeness_score,
    specificity_score,
    confidence_clarity_score,
    conversation_coherence_score,
    verbosity_balance_score,
    star_score,
    coverage_progress_contribution,
    factual_accuracy_reasoning_quality,
    communication_clarity_score,
    seniority_signal_score,
    red_flag_score,
    calculate_turn_metrics,
)

# Set to True to run LLM-based metrics (requires GOOGLE_API_KEY)
RUN_LLM_METRICS = os.environ.get("RUN_LLM_METRICS", "0").lower() in ("1", "true", "yes")

Turn = Dict[str, str]


# ─────────────────────────────────────────────────────────────────────────────
# Example Q&A pairs: (label, question, answer[, history])
# ─────────────────────────────────────────────────────────────────────────────

EXAMPLES: List[Tuple[str, str, str, List[Turn] | None]] = [
    # ─── POSITIVE: direct, specific, quantified, confident ───
    (
        "POSITIVE_strong",
        "Describe a time you improved system performance.",
        "In my last role I led the migration of our order service to Kubernetes. "
        "Because we were hitting 10,000 requests per second, I introduced Kafka for "
        "async event streaming, which decoupled payment from inventory. "
        "As a result we reduced p95 latency by 40% and cut costs by 20%. "
        "For example, during Black Friday we handled 3x normal traffic with zero downtime. "
        "I designed the rollout, coordinated with SRE, and we shipped it in 6 weeks.",
        None,
    ),
    (
        "POSITIVE_specific",
        "What databases have you used in production?",
        "We used Postgres for transactional data and Redis for caching. "
        "I implemented connection pooling with PgBouncer and reduced query time by 35%. "
        "We also had a MongoDB cluster for document storage—about 2TB—and I wrote the migration "
        "scripts when we moved some collections to Postgres. So: Postgres, Redis, MongoDB, and "
        "we used Elasticsearch for full-text search with roughly 50M documents.",
        None,
    ),
    # ─── NEGATIVE: vague, short, hedging, shallow ───
    (
        "NEGATIVE_vague",
        "Tell me about a challenging technical problem you solved.",
        "I worked on it with the team. It was fine. We did some stuff and it got better. "
        "I have experience with that kind of thing. Maybe we used Python or something. "
        "I'm not sure of the exact details. It was a while ago.",
        None,
    ),
    (
        "NEGATIVE_hedging",
        "Have you led a major project?",
        "Maybe I have. I think I might have been involved in something like that. "
        "I'm not certain if you'd call it leading. Possibly I helped with some decisions. "
        "Things were done and it was probably okay. I guess we could say I was part of it.",
        None,
    ),
    (
        "NEGATIVE_too_short",
        "How do you approach debugging distributed systems?",
        "I add logs and check metrics. Sometimes we use tracing.",
        None,
    ),
    (
        "NEGATIVE_off_topic",
        "What’s your experience with API design?",
        "I really enjoy hiking and reading. I’ve always been curious about nature. "
        "In my free time I like to learn new things. Technology is interesting in general.",
        None,
    ),
    # ─── AMBIGUOUS: mixed signals, partially on-topic ───
    (
        "AMBIGUOUS_partial",
        "Describe your CI/CD pipeline experience.",
        "We had Jenkins and later moved to GitHub Actions. I was involved in setting up "
        "some of the pipelines. The builds were done and deployments were automated. "
        "I think we had something like 20 pipelines. So there was definitely CI/CD.",
        None,
    ),
    (
        "AMBIGUOUS_tangential",
        "How do you handle production incidents?",
        "We use PagerDuty for alerts. The on-call rotation was set up by the team. "
        "When things break we look at dashboards—Grafana and Datadog. So monitoring is key. "
        "I’ve been on call before. It’s important to document runbooks.",
        None,
    ),
    # ─── CONFUSING: odd structure, passive, rambling or contradictory-seeming ───
    (
        "CONFUSING_rambling",
        "What’s one thing you’re proud of in your career?",
        "Well so basically the thing is that when you have a lot of code and the code is "
        "getting bigger and then there are more people and then they need to understand "
        "the code and so we had to think about how to make it better and so we did some "
        "refactoring and it was decided that we would split the monolith and things were "
        "set up over several months and eventually the new services were created and "
        "deployed and it was a team effort and I was part of that and we had meetings "
        "every week and sometimes twice a week to discuss progress and there were a lot "
        "of decisions that were made along the way and in the end things were better "
        "and the deployment was done and we had fewer bugs and that was good.",
        None,
    ),
    (
        "CONFUSING_passive",
        "What role did you play in the last migration?",
        "The migration was done by the team. It was decided that we would use the new stack. "
        "Things were built and deployed. The database was moved. Stuff was tested. "
        "I was involved in it. The rollout was handled by DevOps.",
        None,
    ),
]

# Optional: one example WITH history (for COH, CPC, novelty, redundancy)
HISTORY_EXAMPLE: Tuple[str, str, str, List[Turn]] = (
    "WITH_HISTORY",
    "So what would you do differently in that project?",
    "I would push for feature flags earlier. Because we had a single main branch, "
    "releases were risky. I’d also introduce canary deployments—we had the infra "
    "but didn’t use it. So: feature flags, canaries, and better observability from day one.",
    [
        {"role": "user", "content": "Tell me about a recent project that didn’t go well."},
        {"role": "assistant", "content": "We had a big release that caused outages. The rollout was too broad and we didn’t have feature flags. I was responsible for the deployment strategy."},
        {"role": "user", "content": "So what would you do differently in that project?"},
    ],
)


def print_section(title: str, char: str = "─") -> None:
    width = 72
    print()
    print(char * width)
    print(f"  {title}")
    print(char * width)


def print_metric_descriptions() -> None:
    """What each metric measures and how it differentiates."""
    print_section("What each metric measures and how it differentiates", "═")
    docs = [
        ("QAR (Question–Answer Relevance)", "Semantic similarity between question and answer (embeddings). High when the answer is on-topic; low when off-topic or generic."),
        ("TDS (Topical Depth Score)", "Rewards causal language (because, therefore), examples (for example), and numbers. Penalises shallow filler (e.g. 'I worked on it', 'did some stuff')."),
        ("ACS (Answer Completeness)", "Share of sentences on-topic + length adequacy (~80+ words). Low for very short or mostly off-topic answers."),
        ("SS (Specificity Score)", "Named tech/tools + quantified claims. Differentiates vague answers from concrete ones (e.g. 'Python, Kafka, 40%' vs 'some scripting')."),
        ("CCS (Confidence & Clarity)", "Rewards first-person ownership (I built, I led). Penalises hedging (maybe, I think) and passive voice (was done, was built)."),
        ("COH (Conversation Coherence)", "How well the answer fits the recent thread (needs history). High when the answer continues the topic; 1.0 when no history."),
        ("VBS (Verbosity Balance)", "Penalises too short (<40 words) or too long (>350 + question length). Sweet spot: 40–350 words."),
        ("STAR (Behavioral)", "Situation–Task–Action–Result structure. Turn = this answer; cumulative = across full conversation. For behavioural questions."),
        ("CPC (Coverage Progress)", "QAR × ACS. How much this turn advances the interview. Cumulative = average across turns."),
        ("FARQ (LLM)", "Factual accuracy and logical reasoning. Correct tech claims, coherent reasoning."),
        ("COMM (LLM)", "Communication clarity: structure, ease of following, concise yet complete."),
        ("SSS (LLM)", "Seniority signals: tradeoffs, system thinking, ownership, impact, mentoring."),
        ("RFD (LLM)", "Red-flag detector: blame-shifting, avoidance, contradictions, exaggeration. 1.0 = no flags."),
    ]
    for name, desc in docs:
        print(f"  • {name}\n    {desc}\n")


def run_examples(run_llm: bool) -> None:
    """Run all embedding-based metrics (and optionally LLM) on each example."""
    print_section("Scores by example (embedding + optional LLM)", "═")

    for label, question, answer, history in EXAMPLES:
        print(f"\n  [{label}]")
        print(f"  Q: {question[:70]}{'…' if len(question) > 70 else ''}")
        print(f"  A: {answer[:70]}{'…' if len(answer) > 70 else ''}")

        m = calculate_turn_metrics(
            question=question,
            answer=answer,
            chat_history=history,
            behavioral_phase=True,  # show STAR for all examples
            run_llm_metrics=run_llm,
        )

        # Embedding metrics
        for key in ("QAR", "TDS", "ACS", "SS", "CCS", "COH", "VBS"):
            v = m.get(key)
            if v is not None:
                bar = "█" * int(round(v * 10)) + "░" * (10 - int(round(v * 10)))
                print(f"    {key:4s} {v:.3f}  {bar}")
        if "CPC_turn" in m:
            print(f"    CPC  {m['CPC_turn']:.3f}  (turn)")
        if "STAR_turn" in m:
            print(f"    STAR {m['STAR_turn']:.3f}  (turn)")

        if run_llm:
            for key in ("FARQ", "COMM", "SSS", "RFD"):
                v = m.get(key)
                if v is not None and v >= 0:
                    bar = "█" * int(round(v * 10)) + "░" * (10 - int(round(v * 10)))
                    print(f"    {key:4s} {v:.3f}  {bar}")
            if m.get("RFD_flags"):
                print(f"    RFD_flags: {m['RFD_flags']}")

    # One example with history
    label, question, answer, history = HISTORY_EXAMPLE
    print(f"\n  [{label}]")
    print(f"  Q: {question[:70]}{'…' if len(question) > 70 else ''}")
    print(f"  A: {answer[:70]}{'…' if len(answer) > 70 else ''}")
    print(f"  (history: {len(history)} turns)")
    m = calculate_turn_metrics(
        question=question,
        answer=answer,
        chat_history=history,
        behavioral_phase=False,
        run_llm_metrics=run_llm,
    )
    for key in ("QAR", "TDS", "ACS", "COH", "CPC_turn", "CPC_cumulative"):
        v = m.get(key)
        if v is not None:
            print(f"    {key:18s} {v:.3f}")


def run_single_metric_comparison() -> None:
    """Show one metric (e.g. TDS or CCS) across all examples for direct comparison."""
    print_section("Single-metric comparison (how one metric differentiates)", "═")

    metric_name = "TDS"
    metric_fn = topical_depth_score
    print(f"  Metric: {metric_name} (Topical Depth Score)\n")

    for label, question, answer, history in EXAMPLES:
        v = metric_fn(question, answer, history)
        bar = "█" * int(round(v * 10)) + "░" * (10 - int(round(v * 10)))
        print(f"  {label:22s} {v:.3f}  {bar}")

    print_section("Confidence & Clarity (CCS) across examples", "─")
    metric_fn = confidence_clarity_score
    for label, question, answer, history in EXAMPLES:
        v = metric_fn(question, answer, history)
        bar = "█" * int(round(v * 10)) + "░" * (10 - int(round(v * 10)))
        print(f"  {label:22s} {v:.3f}  {bar}")


def main() -> None:
    run_llm = RUN_LLM_METRICS
    if run_llm:
        print("(LLM metrics enabled: GOOGLE_API_KEY set)")
    else:
        print("(LLM metrics disabled; set RUN_LLM_METRICS=1 and GOOGLE_API_KEY to include FARQ, COMM, SSS, RFD)")

    print_metric_descriptions()
    run_examples(run_llm)
    run_single_metric_comparison()

    print_section("Done", "═")
    print()


if __name__ == "__main__":
    main()
