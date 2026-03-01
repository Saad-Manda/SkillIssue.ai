from __future__ import annotations

import re
import os
import json
import warnings
from typing import Dict, List, Optional, Any

import numpy as np
from langchain_core.messages import SystemMessage, HumanMessage
from sentence_transformers import SentenceTransformer

from ...agents.llm import llm

Turn    = Dict[str, str]
Metrics = Dict[str, Any]

_embedder = SentenceTransformer(model="sentence-transformers/all-MiniLM-L6-v2")


def embed(text: str) -> np.ndarray:
    v = np.array(_embedder.encode(text), dtype=np.float32)
    norm = np.linalg.norm(v)
    if norm > 0:
        v /= norm
    return v


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom > 0 else 0.0



def _llm_critique(system: str, user_content: str) -> Optional[str]:
    """Call project LLM with SystemMessage + HumanMessage; return raw text or None."""
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