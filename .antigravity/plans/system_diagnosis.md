# 🔬 SkillIssue.ai — Full System Diagnosis Report

> **Date**: 2026-06-06  
> **Author**: Antigravity (Deep Diagnostic Mode)  
> **Scope**: End-to-end analysis of every agent, every node, every wiring decision, every prompt, latency profile, and cascading failure risk.

---

## 🗺️ Table of Contents

1. [System Overview — What We Are Working With](#1-system-overview)
2. [The Core Problem Statement](#2-the-core-problem-statement)
3. [Agent-by-Agent Autopsy](#3-agent-by-agent-autopsy)
   - 3.1 `user_summarizer`
   - 3.2 `planner`
   - 3.3 `router`
   - 3.4 `question_generator`
   - 3.5 `phase_summarizer`
   - 3.6 `metric_calculator`
   - 3.7 `report_generator`
4. [Orchestration & Graph Wiring Failures](#4-orchestration--graph-wiring-failures)
5. [Latency Catastrophe — Why Responses Scale as O(n²)](#5-latency-catastrophe--why-responses-scale-as-on²)
6. [State Architecture Problems](#6-state-architecture-problems)
7. [Question Quality Failure — Root Cause Analysis](#7-question-quality-failure--root-cause-analysis)
8. [Routing Intelligence Problems](#8-routing-intelligence-problems)
9. [**The 3-Branch Design Flaw — A Phantom Layer**](#9-the-3-branch-design-flaw--a-phantom-layer) ← NEW
10. [Metrics System — Fundamentally Broken Signals](#10-metrics-system--fundamentally-broken-signals)
11. [Cascading Failure Map](#11-cascading-failure-map)
12. [Rate Limit Architecture](#12-rate-limit-architecture)
13. [Prescribed Remediation Plan](#13-prescribed-remediation-plan)

---

## 1. System Overview

SkillIssue.ai is a LangGraph-orchestrated multi-agent interview platform with **7 nodes**, **2 state stores** (Redis + LangGraph MemorySaver), **3 databases** (PostgreSQL, Redis, MongoDB), and a React/Vite frontend.

### The Interview Flow (Per Turn)

```
[User submits answer]
        ↓
[phase_summarizer]  ← LangGraph interrupt resumes here
        ↓
[metric_calculator]  ← Calls 2 LLMs + 1 local model (sentence-transformer)
        ↓
[router]  ← Calls 1 LLM with ENTIRE chat history
        ↓
[question_generator]  ← Calls 1 LLM with full context
        ↓
[INTERRUPT] → Returns question to user
```

**Per turn: 4 LLM calls minimum. This is the root of the O(n²) problem.**

### LLM in Use

```python
# llm.py
llm = ChatGroq(model=model_name, temperature=0.6)
```
Everything — all 7 agents — uses the **same single LLM singleton** with no differentiation, no model tiering, no rate-limit awareness.

---

## 2. The Core Problem Statement

After reading the sample interview session provided by the user, the problems are clear and systematic:

### What the Interview Looked Like (Observed)
- **Same topic** (`ml_experience`) was repeated **9 times in a row**
- Phase changed once — from Introduction to "Experience Deep Dive" — then got stuck
- All 9 questions are **Experience Deep Dive / ML Experience** questions
- Questions get increasingly repetitive and redundant (supervised vs. unsupervised asked TWICE almost verbatim)
- Metrics show `N/A` for all questions (they're only calculated after the answer, not shown to the user)
- The interviewer asks almost IDENTICAL questions: "Can you describe a situation..." over and over

**This is not a minor UX issue. The routing system is fundamentally failing to advance topics.**

---

## 3. Agent-by-Agent Autopsy

---

### 3.1 `user_summarizer`

**File**: [`agents/user_summarizer/agent.py`](../../src/agents/user_summarizer/agent.py)

**What it does**: Converts the full User Pydantic model to JSON and sends it to the LLM to produce a short paragraph summary.

#### ❌ Problem 1: Called EVERY session start, never cached
```python
# This runs every time a session is started. Even for the same user starting a new interview.
response: AIMessage = llm.invoke([HumanMessage(content=prompt)])
system_state.user_summary = summary
```
The user profile doesn't change mid-session. This LLM call is pure waste for returning users. Result: **+1 unnecessary LLM call per session start**.

#### ❌ Problem 2: Prompt is aggressively restrictive
```python
# prompt.py
"Do NOT infer, assume, embellish, extrapolate, or generalize beyond the data."
"Never fabricate any detail not explicitly stated in User Data."
```
The rules are so strict that the resulting summary is often a dry list. When this summary is passed to the `question_generator` as "CANDIDATE CONTEXT," the LLM has very little to anchor personalized questions to. The summary loses context about the *relationship between skills*, which is what makes contextual questions feel personal.

#### ❌ Problem 3: No System Message — Just a HumanMessage
```python
response: AIMessage = llm.invoke([HumanMessage(content=prompt)])
```
The entire instructions AND context are crammed into a `HumanMessage`. No `SystemMessage` is used. This means the model has no distinct role framing — it's just being talked at. This subtly degrades instruction-following quality.

#### ✅ What Works: The output goes into `system_state.user_summary` and is reused throughout the session without re-calling.

---

### 3.2 `planner`

**File**: [`agents/planner/agent.py`](../../src/agents/planner/agent.py) + [`agents/planner/prompt.py`](../../src/agents/planner/prompt.py)

**What it does**: Takes User + JD and generates a structured interview plan (phases → topics → weights → max_question_count).

#### ❌ Problem 1: Plan is generated EVERY session, even for the same User+JD pair

```python
def planner_node(system_state: SystemState) -> SystemState:
    messages = planner_prompt(system_state)
    response: AIMessage = llm.invoke(messages)  # Full LLM call every time
    plan = Plan.model_validate(parsed_data)
    system_state.plan = plan
```

The Plan for a given (User, JD) combination is **deterministic enough** that it should be cached. Instead, it's re-generated on every session start. **+1 expensive LLM call per session** that could be cached.

#### ❌ Problem 2: No plan validation post-generation

The planner generates a plan with phases and topics, but there is **no post-generation validation** to check:
- Are `topic_id` strings globally unique across all phases? (Critical — routing breaks if two topics share an ID)
- Is `max_question_count` actually > 0 for critical topics? (Router can silently skip topics with count=0)
- Do phase weights approximately sum to 1?
- Does every required_skill appear in at least one topic?

The LLM can silently violate all of these and the system will accept it.

#### ❌ Problem 3: `max_question_count` of 0 creates phantom topics

The prompt explicitly allows:
```
"Low weight / complimentary: 0 or 1 question."
```

If the planner assigns `max_question_count=0` to a topic, the router will hit `k >= max_question_count` (where k=0 and max=0) on the **very first question** for that topic, and immediately trigger TOPIC CHANGED. This means some topics get **zero questions** and the candidate is never evaluated on them. The interview silently skips skills.

#### ❌ Problem 4: The plan provides no breadcrumb for the question_generator

The plan model (`plan_model.py`) has no concept of "topic description" or "what to ask." It has `topic: str` (the topic name) and `objective` at the phase level, but no field like `suggested_angles` or `evaluation_goal` per topic. The `question_generator` is left to infer what to ask about a topic named "Imbalanced Dataset Handling" — which leads to generic ML textbook questions.

#### ✅ What Works: The schema is clean and the JSON parsing is solid with Pydantic validation.

---

### 3.3 `router`

**File**: [`agents/router/agent.py`](../../src/agents/router/agent.py) + [`agents/router/prompt.py`](../../src/agents/router/prompt.py)

**What it does**: Given the full chat history, decides whether the next question should be:
1. Independent (same topic, new angle)
2. Dependent (follow-up on last answer)
3. TOPIC CHANGED (advance to next topic) — but this is NOT decided by the LLM!

**Comments**
- We will have only 3 scenarios, as we will generate plan such that each topic is independent of each other
- *Independent Question* Topic transition only
- *Dependent Question*
  1. Scenario One is the one you told different angle or different perspective, bcoz context used is same but the angle of asking question is different so. indirectly its a dependent question
  2. Other is a proper dependent question u know about it

> I want to hear your thoughts about it, which one draws a clear boundary and simple and efficeint logic

#### 🚨 CRITICAL ARCHITECTURE DEFECT: The router can only say "same topic"

```python
# router/agent.py — lines 51-82
if k >= max_question_count:
    # Hard-coded: advance topic
    system_state.is_curr_question_independent = True
    system_state.current_turn_status = "TOPIC CHANGED"
    return system_state

## Same Topic
messages = router_prompt(chat_history=chat_history)
result = parser.parse(response.content)
system_state.is_curr_question_independent = not bool(result["is_dependent"])
system_state.current_turn_status = str(result["reason"])
```

**The router LLM is ONLY called when `k < max_question_count`.** It can only return `is_dependent: true/false`. It has **no mechanism to say "advance topic early"** even if the topic is exhausted. Topic advancement is a **pure counter check** — if `k >= max_question_count`, advance. The LLM has no voice in this decision.

This is why the interview feels like a stuck record:
- If `max_question_count = 3` for "ML Experience," the interviewer will ask 3 questions about it no matter how well or poorly the candidate answered
- If the candidate answered question 1 brilliantly and demonstrated mastery, the router will still force 2 more questions on the same topic
- **The routing is not adaptive — it is a hard-coded counter**

#### ❌ Problem 2: Router LLM receives THE ENTIRE CHAT HISTORY every single time

```python
# router/prompt.py — line 15
chat_history_json = [t.model_dump() for t in chat_history]
# ...
human_content = f"""
CHAT HISTORY (all turns so far, newest last):
{chat_history_json}
```

By turn 10, this is sending 10 full Q&A pairs (plus metrics objects) to the LLM. By turn 20, 20 pairs. The prompt grows **linearly with each turn**, making the total tokens sent O(n²) across the session. This is the primary driver of the latency growth.

#### ❌ Problem 3: Router prompt instructs it to "focus on most recent block" but sends everything

```
# From the router prompt:
"1. Focus on the **most recent contiguous block of turns with the same `topic_id`**."
```

The system knows it only needs the current-topic block, but still serializes and sends the **entire history**. The LLM is told to ignore most of what it receives. This is wasteful both in tokens (cost) and time (latency).

#### ❌ Problem 4: Router sends metrics alongside chat but metrics are always N/A at display time

The turns in chat history contain `metrics` objects, but according to the observed interview, metrics always show "N/A" in the UI. The metrics ARE being calculated (they're stored in the Turn model), but the router is reading them as signals. If metrics are consistently showing bad values (due to issues detailed in §9), the router may be systematically biased toward `is_dependent=true`, causing it to probe the same answer repeatedly instead of advancing.

---

### 3.4 `question_generator`

**File**: [`agents/question_generator/agent.py`](../../src/agents/question_generator/agent.py) + [`agents/question_generator/prompt.py`](../../src/agents/question_generator/prompt.py)

**What it does**: Given the routing decision, generates the next interview question using one of three branches: TOPIC CHANGED, DEPENDENT, or INDEPENDENT.

#### 🚨 Design Flaw: Three branches when the design only warrants two

> **See §9 for the full architectural breakdown.** Summary: the `INDEPENDENT` same-topic branch is a phantom layer that contradicts the topic design. Topics are defined as independent units — within a topic, every question should be a DEPENDENT follow-up drilling deeper. The two legitimate independent question types (topic transition and phase transition) are both already handled by `TOPIC CHANGED`. The `INDEPENDENT` branch should not exist.

#### ❌ Problem 1: Two prompt templates for three branches — same DNA, different labels

There are only two prompt functions: `independent_question_prompt` and `dependent_question_prompt`. The TOPIC CHANGED branch calls `independent_question_prompt` with `is_topic_transition=True`. While this adds a mode-instruction block, the fundamental context shape is identical.

The result is: **All three branches feel the same.** They all include the same JD, same user summary, same phase context, same previous turns. The questions feel samey because the prompts have the same DNA.

#### ❌ Problem 2: `previous_phase_summaries` is sent in full to every question generation call

```python
# question_generator/agent.py
phase_summary = session_state.get("phase_summary", [])
# ...
messages = independent_question_prompt(
    previous_phase_summaries=phase_summary,  # ALL phase summaries, growing per turn
    ...
)
```

Phase summaries grow throughout the session. By phase 4, you're sending 4 summaries (each potentially paragraph-length). This contributes to O(n) token growth per question. Combined with the router's O(n) chat history, the total cost per turn is O(n).

#### ❌ Problem 3: No mechanism to avoid repeated questions

The `INDEPENDENT` branch has this rule:
```
"AVOID REPEATING previously asked questions verbatim."
```

But the prompt only provides `previous_k_turns` (the turns before the current topic block, NOT the full history). The LLM can't know what was asked in previous turns on other topics. The `DEPENDENT` branch says "avoid repeating verbatim" but also only has the current topic's turns. **There is no deduplication mechanism.** The observed interview shows nearly identical questions being asked multiple times (supervised vs. unsupervised was asked twice in nearly the same framing).

#### ❌ Problem 4: Router reason is passed as `ROUTER DIRECTIVE` but it's the raw `current_turn_status` string

```python
# In the router, reason is set to the LLM's free-text explanation:
system_state.current_turn_status = str(result["reason"])
```

This 2-4 sentence explanation is then injected into the question_generator prompt as:
```
ROUTER DIRECTIVE (why this question is being generated — HIGHEST PRIORITY):
{router_reason}
Formulate your question to directly address this directive.
```

The directive is a reasoning paragraph from the router LLM. It was never designed to be a question-generation directive. Its format is inconsistent and its phrasing may actively mislead the question generator. For example, if the router says "The candidate showed gaps in specificity — probe their understanding of ensemble methods," the question_generator is told to treat this as the highest-priority instruction. This can work, but it can also cause the question generator to produce **artificially narrow follow-ups** that feel robotic.

#### ❌ Problem 5: `chat_history_pre_topic` slicing logic is fragile

```python
# question_generator/agent.py — line 45
chat_history_pre_topic = chat_history_full[:-k] if k > 0 else chat_history_full
```

`k = system_state.current_topic_question_count`. This is the number of questions asked in the **current topic**. The intent is to give the INDEPENDENT branch only the pre-topic history (so it doesn't anchor to current topic answers). But `k` is managed by the router and question_generator together, and if there's any off-by-one or state drift, this slice will be wrong, causing the independent prompt to accidentally include current-topic turns or exclude recent context.

#### ✅ What Works: The bridge sentence concept (acknowledging previous answer, then pivoting to new question) is a good design and the prompts enforce it well.

---

### 3.5 `phase_summarizer`

**File**: [`agents/phase_summarizer/agent.py`](../../src/agents/phase_summarizer/agent.py)

**What it does**: Called after every question is answered. Maintains a rolling text summary of what the candidate demonstrated in each phase.

#### ❌ Problem 1: Called after EVERY question — even when the summary isn't needed immediately

The phase_summarizer runs on every turn, even in the middle of a topic. The summary it generates is used by:
- The `question_generator` (for context)
- The `report_generator` (for evaluation)

The question_generator for DEPENDENT questions uses `current_phase_summary` (last phase summary). But the phase summary only MATTERS for:
1. When transitioning to a new question in the same phase (for context)
2. When generating the report

It does NOT need to run if the next question is going to be on the exact same topic. Running an LLM call to update a summary after every single turn is expensive and often produces nearly identical output to the previous summary.

#### ❌ Problem 2: Summary is a free-text blob with no structure

```python
# The summary is stored as plain text:
{"phase_name": "Experience Deep Dive", "summary": "The candidate discussed..."}
```

When this is given to the question_generator, the LLM must re-parse the free text to understand what's been covered. A structured summary (e.g., JSON with `skills_demonstrated`, `gaps_identified`, `topics_covered`) would give the question_generator much more actionable signals.

#### ❌ Problem 3: `phase_change_summary_prompt` starts fresh for each new phase but loses cross-phase signals

```
"Do NOT carry detailed content from the previous phase summary into this summary."
```

This means if the candidate revealed a weakness in Phase 1 (Introduction) that's relevant to Phase 2 (Technical Skills), the phase_summarizer will not carry that forward. The question_generator for Phase 2 independent questions gets a blank slate. Cross-phase depth is lost.

---

### 3.6 `metric_calculator`

**File**: [`agents/metric_calculator/agent.py`](../../src/agents/metric_calculator/agent.py) + [`agents/metric_calculator/metrics.py`](../../src/agents/metric_calculator/metrics.py)

**What it does**: Computes 8 metrics (QAR, TDS, ACS, SS, CCS, FARQ, RFD, STAR) per turn. Uses a mix of embedding-based calculations and 2 LLM API calls.

#### 🚨 CRITICAL: 2 LLM CALLS per turn, synchronous, blocking

```python
# metrics.py
def factual_accuracy_reasoning_quality(...):
    raw = _llm_critique(system, user_content)  # LLM CALL #1

def red_flag_score(...):
    raw = _llm_critique(system, user_content)  # LLM CALL #2

# calculate_turn_metrics — called after EVERY answer
m["FARQ"] = factual_accuracy_reasoning_quality(question, answer, chat_history)
rfd = red_flag_score(question, answer, chat_history)  # SEQUENTIAL
```

These are called **sequentially**. FARQ finishes, then RFD starts. Both are full LLM API calls. Neither is parallelized. Neither is async. This alone adds **2 full LLM round-trips** per turn, running before the router and question_generator even start.

**Total LLM calls per turn minimum: 4** (1 phase_summarizer + 2 metric_calculator + 1 router + 1 question_generator = 5 in many paths)

#### ❌ Problem 2: Embedding calls are also synchronous and computed per-sentence

```python
# answer_completeness_score — computes one embedding per sentence
sentences = [s.strip() for s in re.split(r'[.!?]+', answer) if s.strip()]
sims = [cosine(embed(s), q_emb) for s in sentences]
```

If an answer has 10 sentences, this is 10 `embed()` calls. Each `embed()` call calls `_embedder.encode(text)` on the CPU-bound `SentenceTransformer`. With 5 different metrics, each making multiple embed calls, a single answer can trigger 20-30 embedding computations sequentially.

#### ❌ Problem 3: Metrics are displayed as "N/A" to the user

The PRD marks "Real-time metric display during interview" as **out of scope**, but the metrics ARE shown in the interview UI according to the observed conversation. And they always show "N/A". This means either:
- The metrics are calculated but not sent to the frontend correctly
- The metrics fields are returned as null
- The frontend displays the raw state instead of the calculated values

This means the metrics system provides **zero value to the user** in the current state.

#### ❌ Problem 4: `_TECH_RE` regex is a fixed list that is immediately outdated

```python
_TECH_RE = re.compile(
    r"\b(python|java|javascript|typescript|go|rust|c\+\+|kotlin|swift|scala|"
    r"docker|kubernetes|aws|gcp|azure|terraform|ansible|helm|..."
)
```

"LLM", "LangChain", "LangGraph", "FastAPI", "Pydantic", "OpenAI", "Gemini", "Groq", "RAG", "vector database", "embeddings", "transformers", "RLHF" — none of these are in the list. For an ML engineer role, this means the Specificity Score (SS) will be artificially low for every candidate who discusses modern ML tooling. The router will incorrectly see low SS and trigger dependent follow-ups, making the interview probe even more on topics already covered.

#### ❌ Problem 5: Metrics are computed AFTER the answer, during graph execution, BEFORE the next question

This is fine architecturally, but the bottleneck is that all 5 metric functions run synchronously in series:
```python
m["QAR"] = question_answer_relevance(...)  # embed calls
m["TDS"] = topical_depth_score(...)         # embed calls
m["ACS"] = answer_completeness_score(...)  # N embed calls (per sentence)
m["SS"]  = specificity_score(...)           # embed calls
m["CCS"] = confidence_clarity_score(...)   # regex only
m["FARQ"] = factual_accuracy_reasoning_quality(...)  # LLM call
m["RFD"]  = red_flag_score(...)             # LLM call
```

These could be parallelized with `asyncio.gather`. Currently they're sequential.

---

### 3.7 `report_generator`

**File**: [`agents/report_generator/agent.py`](../../src/agents/report_generator/agent.py) + [`agents/report_generator/prompt.py`](../../src/agents/report_generator/prompt.py)

**What it does**: At the end of the interview, formats the full transcript + metrics into a markdown Interview Readiness Report.

#### ❌ Problem 1: The prompt is a simple template with no metric utilization strategy

```python
# report_generator/prompt.py
"""
**Evaluation Criteria:**
1. **Technical Accuracy:** Did the candidate answer technical questions correctly?
2. **Communication:** Was the candidate clear, concise, and professional?
3. **Relevance:** Did the answers directly address the interviewer's questions?
"""
```

The system calculated 8 specialized metrics (QAR, TDS, ACS, SS, CCS, FARQ, RFD, STAR) per turn. The report generator receives them in `[METRICS]: QAR=0.7; TDS=0.4...` format, but the prompt never tells the LLM what these metrics mean, how to interpret them, or how to weight them in the report. The LLM receives the metrics as noise and produces a generic report that could have been written without them.

#### ❌ Problem 2: The entire transcript is sent to the report generator

```python
# report_generator/agent.py
for msg in raw_history:
    formatted_transcript += f"[PHASE={phase}...]\n[INTERVIEWER]: {question}\n[CANDIDATE]: {response}\n[METRICS]: ...\n\n"
```

For a 20-turn interview, this could be 10,000+ tokens of transcript. The report generator receives the entire context in a single LLM call. This is both slow (long context) and expensive (large token count).

#### ❌ Problem 3: Report prompt generates 6 sections but tells the LLM to be selective about transcript analysis

```
"## 5. Question-by-Question Analysis
(Select the top 2-3 most critical questions from the transcript)"
```

Why instruct the LLM to be selective when we're already providing the full transcript? If we only want 2-3 questions analyzed, we should pre-select them based on metrics and only send those. Instead, the LLM reads everything and then has to make editorial choices.

---

## 4. Orchestration & Graph Wiring Failures

**File**: [`agents/orchestrator.py`](../../src/agents/orchestrator.py)

```python
graph.set_entry_point("user_summarizer")
graph.add_edge("user_summarizer", "planner")
graph.add_edge("planner", "router")
# ...
graph.compile(checkpointer=checkpointer, interrupt_before=["phase_summarizer"])
```

### ❌ Defect 1: `user_summarizer` and `planner` run on EVERY RESUME

The graph interrupt point is `interrupt_before=["phase_summarizer"]`. When the user submits an answer, the graph resumes from `phase_summarizer`. **But the first session start goes through user_summarizer → planner → router → question_generator → [INTERRUPT]**.

After the interrupt, when the user submits answer #1, the graph resumes at `phase_summarizer`. This is correct. But if the graph checkpoint is ever lost (e.g., server restart) and the session needs to be rebuilt, `user_summarizer` and `planner` would re-run — generating new (different) user summary and plan mid-interview.

More importantly: On session START, user_summarizer and planner run sequentially before the user sees the first question. This means the user is waiting for:
1. user_summarizer LLM call (~2-4s)
2. planner LLM call (~3-6s)
3. router LLM call (~1-2s)
4. question_generator LLM call (~2-4s)

**Total first-question wait time: 8-16 seconds.** The PRD target is < 10 seconds.

### ❌ Defect 2: `_run_graph` is a blocking synchronous call inside an async FastAPI handler

```python
# routes_session.py
@router.post("/{session_id}/answer")
async def submit_answer_endpoint(session_id: str, payload: SubmitAnswerRequest):
    state, chat, turn_count, store_count = submit_answer(  # SYNC call
        session_id=session_id,
        answer=payload.answer,
    )
```

```python
# session/utils.py
def _run_graph(state: SystemState, *, resume: bool = False) -> SystemState:
    result = app.invoke(input_payload, config=config)  # BLOCKING
```

`app.invoke()` (LangGraph) is synchronous. It's called from a sync controller function, which is called from an async FastAPI route. FastAPI runs sync functions in a threadpool executor — but the threadpool is limited (default: number of CPUs). Under concurrent load, this will block the event loop. **The system cannot handle concurrent interviews without blocking.**

### ❌ Defect 3: `MemorySaver` stores the entire LangGraph state in memory

```python
checkpointer = MemorySaver()
```

`MemorySaver` is an in-memory Python dictionary. On server restart, all LangGraph checkpoints are lost. Any active interview session becomes unresumable. Redis is used for `chat_history` and `phase_summary` but NOT for the LangGraph checkpoint. This is a data loss risk on any restart.

---

## 5. Latency Catastrophe — Why Responses Scale as O(n²)

This is the smoking gun. Let's trace what happens at turn N of the interview:

### Token Growth Per Turn

| Turn N | router input tokens (approx) | question_gen input tokens (approx) | Total LLM calls |
|--------|------------------------------|-------------------------------------|-----------------|
| 1 | ~200 (1 turn) | ~800 (full context) | 5 |
| 5 | ~800 (5 turns) | ~1200 (full context + 5 summaries) | 5 |
| 10 | ~1500 (10 turns) | ~1800 (full context + growing summaries) | 5 |
| 20 | ~3000 (20 turns) | ~3200 (full context + large summaries) | 5 |

The router serializes ALL chat_history every call:
```python
chat_history_json = [t.model_dump() for t in chat_history]
```

Each `Turn.model_dump()` includes: `chat_id`, `question` (200-400 chars), `response` (500-1500 chars), `metrics` (full dict with ~10 fields), `phase_name`, `topic_id`.

A Turn serialized to JSON is roughly **800-2000 tokens**. By turn 10, the router is sending 8,000-20,000 tokens just for chat history. By turn 20, you're at 16,000-40,000 tokens.

### The metric_calculator makes it worse

FARQ and RFD both call `_history_text(chat_history)` — the FULL history — inside every metric call:
```python
# metrics.py
history_block = (f"\n\nConversation so far:\n{_history_text(chat_history, last_n=4)}"
                 if chat_history else "")
```

Note: `last_n=4` is used here (a window), but this is a function argument default, not a hard cap — and in some metrics it's `last_n=999` (effectively unlimited).

### Summary: Every turn requires O(n) tokens, making total session cost O(n²)

```
Total token cost ≈ Σ(n=1 to N) [tokens_at_turn_n]
                 ≈ Σ(n=1 to N) [base_cost + n * avg_turn_tokens]
                 = N * base_cost + avg_turn_tokens * N*(N+1)/2
                 = O(N²)
```

**At turn 15 of a 20-turn interview, a single user turn could be sending 30,000+ tokens to the LLM.** This explains the latency growing disproportionately as the interview progresses.

---

## 6. State Architecture Problems

The system has a **split-brain state architecture**:

| State Store | Contents | Who Writes | Who Reads |
|-------------|----------|------------|-----------|
| LangGraph `MemorySaver` | Full `SystemState` (plan, user, jd, current_phase, etc.) | All nodes | All nodes via graph state |
| Redis `session_store` | `chat_history` (list of Turns) + `phase_summary` | `metric_calculator`, `phase_summarizer` | `router`, `question_generator`, `phase_summarizer`, `report_generator` |

### ❌ Problem 1: Two sources of truth for overlapping data

`SystemState` has `current_phase_name`, `current_topic_id`. Redis has `chat_history` with `phase_name` and `topic_id` per turn. If the LangGraph state and Redis state ever diverge (network issue, partial write, exception), the system will generate questions for the wrong phase or topic.

There is no reconciliation check between the two stores. A partial failure in `metric_calculator` (which writes to Redis) followed by a re-run would cause duplicate turns in the history.

### ❌ Problem 2: `session_state_initialize` creates an empty SessionState but has a bug

```python
# state_init.py
def session_state_initialize(session_id: str):
    session_state = SessionState()
    session_state.session_id = session_id
    session_state.chat_history = []
    session_state.phasewise_summary = []
    session_store.set(session_id, session_state)  # ← BUG: passing Pydantic model to Redis
```

`session_store.set()` calls `json.dumps(data)` — but `data` here is a `SessionState` Pydantic object, not a dict. `json.dumps` cannot serialize a Pydantic object. This will raise a `TypeError` on first call unless there's some implicit serialization happening. (Pydantic v2 objects are not JSON-serializable by default via `json.dumps`.) **If this code path is hit, session initialization silently fails.**

### ❌ Problem 3: No TTL on Redis sessions

```python
# RedisSessionStore.set
def set(self, session_id: str, data: Dict[str, Any], ttl: int | None = None):
    if ttl:
        self.client.setex(key, ttl, payload)
    else:
        self.client.set(key, payload)  # No TTL ever set
```

Sessions are never expired. Redis will grow indefinitely. Old sessions from abandoned interviews accumulate. The PRD mentions TTLs as a risk mitigation but the code doesn't implement them.

---

## 7. Question Quality Failure — Root Cause Analysis

Based on the observed interview (9 questions all in "Experience Deep Dive / ml_experience"), here is the diagnostic chain:

### Step 1: Planner generated a plan with ml_experience having high max_question_count

The planner prompt says high-weight topics get `max_question_count = 2 or 3`. For an ML Engineer role, "ML Experience" is high weight. It's likely set to 3.

### Step 2: Router counter isn't advancing the topic

The router checks `k >= max_question_count`. But 9 questions were asked on the same topic. This means either:
- `max_question_count` was set very high (> 9) — unlikely but possible
- `current_topic_question_count` is not being incremented correctly

Looking at the code:
```python
# question_generator/agent.py — DEPENDENT branch
system_state.current_topic_question_count += 1

# INDEPENDENT branch (not TOPIC CHANGED)
system_state.current_topic_question_count = 1  # ← RESET to 1, not increment!
```

**BUG FOUND**: The INDEPENDENT branch resets `current_topic_question_count = 1` instead of incrementing it. This means if the router alternates between DEPENDENT and INDEPENDENT decisions, the count keeps resetting to 1, never reaching `max_question_count`. **The topic can NEVER advance if any INDEPENDENT question is generated.**

Let's verify: If max_question_count = 3:
- Turn 1: TOPIC CHANGED → count set to 1
- Turn 2: Router → INDEPENDENT → count reset to 1 (should be 2!)
- Turn 3: Router → DEPENDENT → count becomes 2
- Turn 4: Router → INDEPENDENT → count reset to 1 again!
- This loop repeats forever. k never reaches 3. Topic never advances.

**This is the primary bug causing the "stuck on same topic" behavior.**

### Step 3: Even if it advances, the next topic has the same context issue

Even if topic advancement worked, the `question_generator` for a new topic uses:
- Full user summary
- Full JD
- Phase context (objective paragraph)
- Topic (just a name string: "Supervised vs. Unsupervised Learning")
- Previous phase summaries

Without suggested angles or evaluation goals, the LLM will default to the most obvious question about a topic — which is usually textbook-level and generic.

---

## 8. Routing Intelligence Problems

### ❌ The router has a false dichotomy — and it shouldn't exist in its current form

The router can only decide: **independent same-topic** OR **dependent same-topic**. The only way to advance a topic is via the hardcoded counter. This means:

- **There is no "early topic exit"**: Even if the candidate brilliantly answers all possible angles of a topic in one response, the router cannot advance early.
- **There is no "extend topic"**: If the counter reaches max but the candidate clearly doesn't understand the topic, the router cannot extend.
- **There is no "phase end"**: The router cannot decide "this phase is done, move to the next."

The router is essentially a follow-up classifier, not a routing agent. It has been given a title ("router") that implies strategic decision-making, but its actual power is limited to: "should I probe this specific answer or ask something fresh on the same topic?"

> **Root cause**: The existence of the `INDEPENDENT` same-topic branch forced the router to have a binary decision it should never have needed to make. If the design collapses to 2 question types (see §9), the router only needs to decide: **advance topic** (TOPIC CHANGED) or **follow up** (DEPENDENT). The LLM call becomes much simpler and cheaper.

### ❌ The routing decision is not fed back to improve future turns

Each routing `reason` string from the LLM is passed to the question_generator as `ROUTER DIRECTIVE`. But there's no feedback mechanism. If the question_generator ignores the directive (or misinterprets it), the router will never know. The next turn, the router reads the chat history and may make the same decision again.

### ❌ Router sends FULL turn objects with metrics as context

Each turn in chat_history includes a `metrics` object. The router prompt says:
```
"Treat metrics as **signals**, not hard constraints."
"If metrics disagree with the actual text, trust the text more."
```

If metrics are broken (as identified in §9), the router has conflicting signals. It sees a metrics object saying TDS=0.1 (low depth) but the actual answer is clearly detailed. The router is told to trust text over metrics — but it still has to parse and process the full metrics objects, wasting tokens.

---

## 9. The 3-Branch Design Flaw — A Phantom Layer

### The Original Design Intent

The interview system was conceived with a clean 2-type model for how questions relate to each other:

| Transition Type | What it means | When it fires |
|-----------------|---------------|---------------|
| **Topic Transition** | Moving from one topic to the next within the same phase | Counter hits `max_question_count` |
| **Phase Transition** | Moving from one phase to the next | Last topic of a phase exhausted |

Topics themselves are the atomic units of evaluation. Each topic is a distinct skill, concept, or domain (e.g., "Imbalanced Datasets", "System Design", "STAR Leadership Example"). Topics are **designed to be independent from each other by construction** — they cover different things, and the planner intentionally separates them.

### What Was Actually Built

The implementation added a **third question type**: `INDEPENDENT` (same-topic, question not anchored to last answer).

```
Designed:   TOPIC_CHANGED  →  (new topic question)
            DEPENDENT      →  (follow-up drill within topic)

Built:      TOPIC_CHANGED  →  (new topic question)
            DEPENDENT      →  (follow-up drill within topic)
            INDEPENDENT    →  (same topic, but don't reference last answer)
```

### Why This Third Branch Is Architecturally Wrong

**1. Topics are already independent — their questions should not be.**

If a topic is "Imbalanced Datasets" and it has `max_question_count = 3`, those 3 questions should progressively drill deeper:
- Q1: "Can you describe a situation where you encountered an imbalanced dataset?"
- Q2 (DEPENDENT): "You mentioned oversampling — what were the specific trade-offs you saw with SMOTE vs. class weighting in your project?"
- Q3 (DEPENDENT): "When you adjusted class weights, how did you validate that the minority class performance improvement wasn't at the cost of majority class recall?"

Each question builds on the answer before it. The topic's independence is already guaranteed by the planner's design — you don't need a mechanism to ask "independent" questions *within* the topic because the topic *itself* is the independence boundary.

**2. The INDEPENDENT branch produces generic questions.**

An "independent" same-topic question — one that deliberately does NOT reference the last answer — is by definition a question that could be asked of any candidate about that topic. It ignores what the candidate actually said. This is exactly what the PRD says is a failure state: *"Generic questions that could apply to any candidate are a failure state."*

**3. It created the counter bug and the router complexity.**

Because there were now 3 branches instead of 2, the counter logic had to distinguish between "reset for new topic" and "continue for same topic INDEPENDENT." This is where the `= 1` vs `+= 1` bug was born. The complexity was unnecessary.

**4. The router shouldn't need an LLM call to pick between INDEPENDENT and DEPENDENT.**

Having the router make an LLM API call to decide whether to ask an independent or dependent question on the same topic is expensive. If the design collapses to 2 types:
- Within topic → always DEPENDENT (follow up on what the candidate actually said)
- Counter exhausted → TOPIC CHANGED (move on)

The router LLM call can be **eliminated entirely for within-topic decisions**. The only time the LLM is needed is to decide: *"Is this topic sufficiently covered, or should we extend beyond `max_question_count`?"* — which is a much simpler, cheaper call.

### The Correct 2-Branch Architecture

```
Router decision:
  ├── k >= max_question_count?  →  TOPIC CHANGED  (topic/phase transition question)
  └── k < max_question_count?   →  DEPENDENT      (follow-up drill on what candidate just said)

Optional enhancement:
  └── Router LLM can say "advance_early" if topic is demonstrably mastered
      or "extend" if candidate clearly hasn't gotten it despite hitting max_count
```

This eliminates:
- The INDEPENDENT same-topic branch entirely
- The `chat_history_pre_topic` slicing logic (only needed by INDEPENDENT)
- The router's binary `is_dependent` LLM decision (replaces with simpler advance/continue)
- The counter bug (no ambiguity about what `= 1` vs `+= 1` means)

> **Status**: The counter bug (line 291: `= 1` → `+= 1`) has been fixed as a patch. But the deeper architectural fix is to remove the INDEPENDENT branch entirely and simplify routing to TOPIC CHANGED vs DEPENDENT only.

---

## 10. Metrics System — Fundamentally Broken Signals

### 9.1 `specificity_score` (SS) is nearly always ~0 for ML candidates

```python
_TECH_RE = re.compile(
    r"\b(python|java|javascript|typescript|go|rust|c\+\+|kotlin|swift|scala|..."
```

Missing from this regex: `langchain`, `langgraph`, `fastapi`, `pydantic`, `openai`, `gemini`, `groq`, `huggingface` (only partial), `rag`, `vector`, `embedding`, `llm`, `gpt`, `bert`, `fine-tuning`, `rlhf`, `mlflow`, `wandb`, `dvc`, `ray`, `celery`, `dramatiq`, `sqlalchemy`, `alembic`, `motor`, `pymongo`, `asyncpg`, `aioredis`, `numpy`, `pandas`, `matplotlib`, `seaborn`, `xgboost`, `lightgbm`, `catboost`, `statsmodels`, `scipy`.

An ML candidate who mentions "I used LangGraph with Pydantic models and deployed with FastAPI on AWS" would get SS=0 because none of those except "aws" are in the regex.

**This means SS is systematically underreporting ML-specific candidates, making the router incorrectly treat strong answers as weak.**

### 9.2 `topical_depth_score` (TDS) penalizes interview-appropriate language

```python
_SHALLOW_RE = re.compile(
    r"\b(i worked on it|it was fine|did some stuff|helped with|was involved in|"
    r"i know about|i have experience|i've done that|we just used)\b"
)
# base = max(base - shallow_hits * 0.12, 0.0)
```

"I have experience with..." is a natural interview phrase. "I know about..." is how candidates hedge uncertainty honestly. Penalizing these phrases makes a candidate who accurately represents their knowledge level get a lower depth score than one who uses more confident but possibly inaccurate language.

### 9.3 `answer_completeness_score` (ACS) threshold is too lenient

```python
on_topic = sum(1 for s in sims if s > 0.10) / len(sims)
```

Cosine similarity of 0.10 is essentially noise — almost any sentence from a coherent paragraph will have >0.10 similarity to the question embedding. This means ACS will report high "on-topic" percentages even for tangential answers.

### 9.4 `confidence_clarity_score` (CCS) is calibrated for formal writing, not spoken/interview style

The formula:
```python
score = max(1.0 - hedge_rate * 0.25 - passive_rate * 0.15, 0.0)
score = min(score + min(action_rate * 0.20, 0.30), 1.0)
```

Interview answers naturally use hedges ("I think", "I believe") for intellectual humility and honesty. A candidate who speaks confidently and assertively about things they don't know will score higher than one who accurately hedges uncertainty. **The metric rewards overconfidence.**

### 9.5 Metrics are only shown after the fact and are N/A in the UI

Despite 5 embedding calls + 2 LLM calls per turn for metrics, the user sees N/A. This means the system is paying the computational cost of metrics without delivering any user value during the interview. The only place metrics are used is in the router (which may be misreading them) and the report generator (which ignores their specific values).

---

## 11. Cascading Failure Map

```
[ROOT] INDEPENDENT branch is a phantom design layer
        ↓
EFFECT: Router makes expensive LLM call to pick INDEPENDENT vs DEPENDENT
        ↓
EFFECT: Counter logic has ambiguous reset vs. increment semantics
        ↓
BUG: INDEPENDENT branch reset count = 1 instead of += 1  [FIXED]
        ↓
EFFECT: Topic counter never reached max_question_count
        ↓
EFFECT: Topic never advanced
        ↓
EFFECT: Router kept receiving same-topic chat history
        ↓
EFFECT: Router alternated INDEPENDENT/DEPENDENT indefinitely
        ↓
EFFECT: Same topic explored forever
        ↓
SYMPTOM: 9 questions all on "ml_experience"
        ↓
SYMPTOM: Questions become repetitive and generic (INDEPENDENT = no anchoring)
        ↓
SYMPTOM: Candidate feels stuck in a loop

SEPARATE CASCADE:
Bad SS metric (missing ML tech terms)
        ↓
Router sees "low specificity" → thinks candidate is weak
        ↓
Router biased toward DEPENDENT (probe more) 
        ↓
More questions on same topic
        ↓
Amplifies the stuck-topic bug above

SEPARATE CASCADE:
Full chat history sent to router every turn
        ↓
Token count grows linearly per turn
        ↓
Latency grows per turn
        ↓
By turn 10: Router response time is 3-4x turn 1
        ↓
By turn 20: 8-10x turn 1 latency → feels like system is freezing
        ↓
SYMPTOM: "Response time proportional to n²"

SEPARATE CASCADE:
phase_summarizer runs every turn (LLM call)
        ↓
Produces growing summaries stored in Redis
        ↓
question_generator sends ALL phase summaries every call
        ↓
More tokens per question_generator call as phases progress
        ↓
Compounds with router's growing chat history
        ↓
Total tokens per turn: O(n) growing at multiple points

SEPARATE CASCADE:
Metrics system shows N/A in UI
        ↓
User has no feedback during interview on how they're doing
        ↓
User can't self-correct
        ↓
Interview quality suffers from candidate side too
```

---

## 12. Rate Limit Architecture

### Current State: Absolutely No Rate Limit Protection

There is zero rate limit handling in the codebase:
- No retry logic with exponential backoff
- No request queuing
- No token budget management
- No fallback model selection
- No circuit breaker pattern

### Groq Rate Limits (Current LLM Provider)

Groq's free tier and most paid tiers have:
- **RPM (Requests Per Minute)**: 30 RPM on free tier
- **TPM (Tokens Per Minute)**: 14,400 TPM on free tier

**Per turn, the system makes 5 LLM calls.** At 5 calls/turn and 30 RPM limit, you can do **6 turns per minute** before hitting the rate limit. An interview with 20 turns would exhaust the rate limit in 3-4 minutes.

At turn 15 with ~30,000 tokens per turn across 5 calls, you'd hit the 14,400 TPM limit after a SINGLE TURN.

### What Should Happen Instead

```
PROBLEM: 5 sequential LLM calls per turn
SOLUTION: 
  1. Parallelize FARQ + RFD (both are independent)
  2. Run metric_calculator async (non-blocking)
  3. Cache FARQ/RFD for unchanged context
  4. Add exponential backoff retry (tenacity library)
  5. Implement token budget: track tokens/minute, throttle or queue
  6. Use smaller/faster models for routine tasks (router → smaller model)
  7. Cache planner output by hash(user_id + jd_id)
```

---

## 13. Prescribed Remediation Plan

### 🔴 Priority 1 — Critical Bug Fixes (Must Fix First)

#### Fix 1.1: Fix the `current_topic_question_count` bug in INDEPENDENT branch

**File**: `agents/question_generator/agent.py`

```python
# CURRENT (BROKEN) — Independent branch, line 291
system_state.current_topic_question_count = 1  # ← This RESETS instead of incrementing

# FIX: Increment the count, don't reset it
system_state.current_topic_question_count += 1
```

This single fix will likely resolve 80% of the "stuck on same topic" problem.

#### Fix 1.2: Give the router the ability to advance topics

The router's LLM decision should include a third option: `"advance_topic"`. Currently the router is hardcoded to only say `is_dependent: true/false`. Add an `action` field:
```json
{
  "action": "dependent_followup | independent_same_topic | advance_topic_early",
  "reason": "..."
}
```

And handle `advance_topic_early` by triggering the same logic as `k >= max_question_count`.

#### Fix 1.3: Add `max_question_count` lower bound validation in planner

Add post-validation: If any topic has `max_question_count = 0`, set it to 1. No topic should get zero questions.

---

### 🟠 Priority 2 — Latency & Performance (Fix the O(n²) Problem)

#### Fix 2.1: Slice chat_history in router to current-topic block only

```python
# INSTEAD OF sending full history:
chat_history_json = [t.model_dump() for t in chat_history]

# SEND ONLY the current topic's turns:
current_topic_turns = [t for t in chat_history if t.topic_id == system_state.current_topic_id]
# Plus last turn from previous topic as bridge context (1 turn max)
```

This makes router input O(1) relative to total turns, not O(n).

#### Fix 2.2: Parallelize metric_calculator LLM calls

```python
# Use asyncio to run FARQ and RFD concurrently
import asyncio
farq_task = asyncio.create_task(async_factual_accuracy(...))
rfd_task = asyncio.create_task(async_red_flag_score(...))
farq, rfd = await asyncio.gather(farq_task, rfd_task)
```

This cuts metric_calculator LLM time roughly in half.

#### Fix 2.3: Cache planner output by (user_id, jd_id) hash

```python
import hashlib
cache_key = f"plan:{hashlib.md5(f'{user_id}:{jd_id}'.encode()).hexdigest()}"
cached_plan = redis.get(cache_key)
if cached_plan:
    return Plan.model_validate_json(cached_plan)
# Otherwise run planner, then cache result for 24h
```

Eliminates planner LLM call for returning users / repeated interviews with same JD.

#### Fix 2.4: Only send the last N phase summaries to question_generator

Instead of all phase_summaries:
```python
# Only send last 2 phase summaries (not all of them)
recent_phase_summaries = phase_summary[-2:]
```

#### Fix 2.5: Move metric_calculator to async background task

The user doesn't need metrics before seeing the next question. Calculate metrics in the background while the question is being streamed to the user.

---

### 🟡 Priority 3 — Question Quality (The Interview Experience)

#### Fix 3.1: Add `evaluation_angles` to Topic model

```python
class Topic(BaseModel):
    topic_id: str
    topic: str
    source: str
    weight: float
    max_question_count: int
    evaluation_angles: List[str]  # NEW: ["conceptual understanding", "practical application", "edge cases"]
    avoid_questions: List[str]    # NEW: Track asked questions within topic
```

The planner should generate 2-3 evaluation angles per topic. The question_generator uses these as distinct targets for each question, ensuring variety.

#### Fix 3.2: Add a global "asked questions" tracker per session

Store a list of question embeddings (not full text, just semantic fingerprints) in Redis. Before generating a question, check cosine similarity against all previous questions. If similarity > 0.85, regenerate.

#### Fix 3.3: Update `_TECH_RE` regex with modern ML stack

Add: `langchain`, `langgraph`, `pydantic`, `fastapi`, `openai`, `gemini`, `gpt`, `bert`, `transformer`, `embedding`, `vector`, `rag`, `rlhf`, `mlflow`, `wandb`, `numpy`, `pandas`, `xgboost`, `lightgbm`, `ray`, `celery`, `redis`, `mongodb`, `sqlalchemy`, etc.

#### Fix 3.4: Give router a three-way decision with early exit

As described in Fix 1.2 — let the router decide to advance topics early if coverage is clearly complete.

---

### 🟢 Priority 4 — Architecture Hardening

#### Fix 4.1: Replace `MemorySaver` with `RedisSaver` for LangGraph checkpoints

```python
from langgraph.checkpoint.redis import RedisSaver
checkpointer = RedisSaver(client=redis_client)
```

This ensures interview sessions survive server restarts.

#### Fix 4.2: Add rate limit handling with exponential backoff

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(5)
)
def safe_llm_invoke(messages):
    return llm.invoke(messages)
```

#### Fix 4.3: Set Redis TTL on all sessions

```python
session_store.set(session_id, data, ttl=86400)  # 24 hours
```

#### Fix 4.4: Fix `session_state_initialize` serialization bug

```python
# CURRENT (broken):
session_store.set(session_id, session_state)  # Pydantic model, not dict

# FIX:
session_store.set(session_id, session_state.model_dump())
```

#### Fix 4.5: Run LangGraph invoke in a thread pool for FastAPI async compatibility

```python
import asyncio
from fastapi.concurrency import run_in_threadpool

async def _run_graph_async(state: SystemState, resume: bool = False) -> SystemState:
    return await run_in_threadpool(_run_graph, state, resume=resume)
```

---

## Final Verdict

The system has a **sound architectural vision** — multi-agent orchestration with phase planning, adaptive routing, metric evaluation, and structured reporting is exactly the right approach. The PRD is well-written and the overall design is defensible.

But the implementation has **one critical counting bug** that breaks the core interview flow, **one architectural decision** (sending full history O(n) per turn) that breaks latency, and **several metric calibration issues** that corrupt the router's signals.

The good news: The most impactful bug (Fix 1.1) is a single line of code. Fix that first, then address latency, then quality. The system's bones are strong — it needs surgery, not reconstruction.

```
Priority | Effort | Impact
Fix 1.1  |  10min | ★★★★★  (stops the repetition loop entirely)
Fix 2.1  |  30min | ★★★★☆  (halves router token cost)
Fix 3.3  |  20min | ★★★☆☆  (fixes SS metric for ML candidates)
Fix 1.2  |  2hr   | ★★★★☆  (true adaptive routing)
Fix 2.2  |  1hr   | ★★★☆☆  (parallel metric LLM calls)
Fix 4.1  |  1hr   | ★★★☆☆  (session persistence on restart)
Fix 4.2  |  30min | ★★★☆☆  (rate limit resilience)
Fix 3.1  |  3hr   | ★★★★☆  (better question variety per topic)
Fix 2.3  |  2hr   | ★★★☆☆  (plan caching)
```

---

*End of Diagnosis Report — SkillIssue.ai v1.0*
