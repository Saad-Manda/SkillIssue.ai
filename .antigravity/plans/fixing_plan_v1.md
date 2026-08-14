# SkillIssue.ai — Phase-Wise Fixation Plan

> **Scope**: Architecture redesign across Router, Phase Summarizer, Question Generator, and Planner based on user's design decisions and system diagnosis.

---

## Design Decisions Locked In

Before the plan — a clear statement of the two key design decisions, as I understand them from your comments:

### Decision 1: 2-Case Question Model (not 3)

| Case | Name | Meaning |
|------|------|---------|
| `DEPENDENT` | Follow-up | Same topic, builds on context. Covers BOTH "different angle on same topic" AND "proper follow-up on specific claim". Both use the same context base — just different attack vectors. |
| `TOPIC_CHANGED` | Topic transition | Router has decided to move to the next topic. |

> **Why "different angle" = DEPENDENT**: The topic itself IS the independence boundary (designed that way by the planner). Within a topic, every question is contextually dependent on the same set of turns — whether it probes a specific claim or explores a new facet. Calling it "independent" was architecturally wrong because it threw away what the candidate actually said. The distinction between "angle" and "follow-up" is *question style*, not a routing case.

### Decision 2: Router Gives Intent, Not Reason

The router no longer returns `{ is_dependent: bool, reason: str }`.

It returns an `intent` — a structured signal about **how the next question should be asked**:

```json
{
  "intent": "dependent_followup | dependent_new_angle | advance_topic",
  "focus": "short phrase (what to zero-in on or what angle to explore)"
}
```

- **`dependent_followup`** — Probe a specific claim/gap from the last answer(s). Focus = what to probe.
- **`dependent_new_angle`** — Candidate answered well enough; explore a different facet of the same topic. Focus = suggested angle direction.
- **`advance_topic`** — Topic sufficiently covered (or counter soft-limit reached). Triggers TOPIC_CHANGED in question generator.

> No more `reason` paragraph passed as "HIGHEST PRIORITY directive" to question_generator. Instead, a clean `focus` string that the question_generator can use as a lightweight signal.

### Decision 3: Topic Counter is Soft, Not Hard

- Counter still exists per topic (`current_topic_question_count`).
- It is provided to the router as **context** (e.g., "you've asked 3 questions on this topic, soft limit is 4").
- The router decides `advance_topic` — there is no hard `if k >= max_question_count` block forcing a branch.
- This makes routing adaptive: if candidate mastered topic in 2 questions, router can advance early. If still unclear at max, router can extend by returning `dependent_followup`.

### Decision 4: Phase Summarizer Only on Phase Transition

- Phase summarizer is **NOT called after every turn**.
- It is only called when the router returns `advance_topic` AND the next topic is in a **different phase**.
- Input to phase summarizer: all turns from the just-completed phase + running summaries of all prior phases.
- This eliminates 1 LLM call per turn (saves ~20% of total LLM calls per session).

---

## Phase 1 — Router Redesign

**Goal**: Replace binary `is_dependent` + `reason` with intent-based `intent` + `focus`. Remove hard counter check. Give router topic context (counter + soft limit).

### Files Changed

#### [MODIFY] [router/agent.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/router/agent.py)

**What changes**:
- Remove the `if k >= max_question_count` hard block entirely.
- Always call the router LLM (no early hard exit for counter).
- Pass `k` and `max_question_count` to the prompt as soft context.
- Parse the new `{ intent, focus }` response instead of `{ is_dependent, reason }`.
- Map `intent` to `system_state`:
  - `advance_topic` → `current_turn_status = "TOPIC CHANGED"`, `is_curr_question_independent = True`
  - `dependent_followup` / `dependent_new_angle` → `is_curr_question_independent = False`, `current_turn_status = focus`
- Still handle: last topic of last phase → `should_generate_report = True`

**What stays**:
- Topic lookup logic (same)
- `is_final_topic` check (same — still needed before routing to report)
- Session logging calls

#### [MODIFY] [router/prompt.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/router/prompt.py)

**What changes**:
- Rewrite system prompt: explain 3 intent values with when to use each.
- Pass only **current-topic turns** as chat context (not full history) — this alone is a major latency win (O(n) → O(k) tokens where k = questions per topic, typically ≤ 4).
- Add topic counter context: "You have asked {k} questions on this topic. Soft limit is {max_question_count}. You may exceed it if warranted."
- Output schema: `{ "intent": "...", "focus": "..." }`

**Prompt input slimming** (critical):
```
Current topic: <topic_name>
Topic questions so far: <k> (soft limit: <max_question_count>)
Current topic turns (newest last): [only turns where topic_id == current_topic_id]
Last turn from previous topic (bridge context): <last non-current-topic turn, if any>
```

---

## Phase 2 — Phase Summarizer Redesign

**Goal**: Call phase summarizer only on phase transition. Provide all phase turns + prior phase running summaries as input. Eliminate per-turn LLM call.

### Where the Call Currently Lives

`orchestrator.py` currently has: `question_generator → phase_summarizer → metric_calculator`. Phase summarizer runs unconditionally every turn.

### Files Changed

#### [MODIFY] [orchestrator.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/orchestrator.py)

**What changes**:
- Remove `graph.add_edge("question_generator", "phase_summarizer")`.
- Add conditional edge from `question_generator`: if a phase transition just occurred → `phase_summarizer`, else → `metric_calculator`.
- Add edge `phase_summarizer → metric_calculator` (unchanged).

Requires a new routing helper in `utils.py`:
```python
def _route_after_question_generator(state: SystemState) -> str:
    # A phase transition occurred if current_turn_status == "TOPIC CHANGED"
    # and the new phase differs from the last phase in chat history.
    # This flag is set by question_generator when it transitions to a new phase.
    if state.phase_transition_occurred:
        return "phase_summarizer"
    return "metric_calculator"
```

#### [MODIFY] [states.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/models/states/states.py)

**What changes**:
- Add `phase_transition_occurred: bool = False` to `SystemState`.
- This flag is set by `question_generator_node` when it changes `current_phase_name` to a new value.
- Reset to `False` at the start of `question_generator_node`.

#### [MODIFY] [question_generator/agent.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/question_generator/agent.py)

**What changes**:
- In the `TOPIC CHANGED` branch, after updating `current_phase_name`: detect if `new_phase.name != prev_phase` → set `system_state.phase_transition_occurred = True`.
- At start of node: `system_state.phase_transition_occurred = False`.

#### [MODIFY] [phase_summarizer/agent.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/phase_summarizer/agent.py)

**What changes**:
- Remove the `same_phase_summary_prompt` branch entirely (no longer called mid-phase).
- The node now always receives a completed phase. Input: all turns from the completed phase + all prior phase summaries.
- Simplify to a single code path: generate summary for the completed phase using all its turns.

#### [MODIFY] [phase_summarizer/prompt.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/phase_summarizer/prompt.py)

**What changes**:
- Remove `same_phase_summary_prompt` function.
- Rewrite `phase_change_summary_prompt` → `phase_summary_prompt(phase_name, all_phase_turns, prior_phase_summaries)`.
- Input: all turns (full Q&A list) for the phase that just ended + running summaries of prior phases.
- This gives the summarizer complete information about what was covered, removing the need for the incremental update pattern.

---

## Phase 3 — Question Generator: Collapse to 2 Branches

**Goal**: Remove the `INDEPENDENT` branch. Collapse to `TOPIC_CHANGED` and `DEPENDENT` only. Clean up slicing logic.

### Files Changed

#### [MODIFY] [question_generator/agent.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/question_generator/agent.py)

**What changes**:
- Delete the entire `INDEPENDENT` branch (lines 235-302 in current code).
- `is_indep` field is no longer meaningful — delete its usage.
- The two cases:
  1. `reason == "TOPIC CHANGED"` → call `topic_transition_prompt(...)` (rename of `independent_question_prompt` with `is_topic_transition=True`)
  2. else → `DEPENDENT` branch — covers both `dependent_followup` and `dependent_new_angle` intents.
- Delete `chat_history_pre_topic` slicing entirely (was only needed by INDEPENDENT).
- In the DEPENDENT branch:
  - For `dependent_followup`: pass `current_topic_turns` (all turns in current topic).
  - For `dependent_new_angle`: same context, but `focus` from router tells it which angle.
  - The `focus` string replaces the `router_reason` directive — it's a cleaner, shorter signal.
- Counter update: always `+= 1` in both branches (no more `= 1` reset bug — it's gone because INDEPENDENT is gone).

#### [MODIFY] [question_generator/prompt.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/question_generator/prompt.py)

**What changes**:
- Remove `independent_question_prompt`'s non-transition mode (`is_topic_transition=False` path).
- Keep and rename the transition mode → `topic_transition_prompt(...)`.
- Keep `dependent_question_prompt` — add `angle_focus: str = ""` parameter that maps to the router's `focus` field.
- When `angle_focus` is set and intent was `dependent_new_angle`: add mode instruction "Explore this angle of the same topic: {angle_focus}. Do NOT probe the specifics of their last answer."
- When `angle_focus` is set and intent was `dependent_followup`: add mode instruction "Probe this aspect: {angle_focus}."
- Both are the same function, same context shape — just a different mode instruction injected. This is clean.

> Note: The prompt context for DEPENDENT is simplified — we now pass current topic turns instead of the complex `chat_history_pre_topic` slice.

---

## Phase 4 — Planner Enhancement: evaluation_angles per Topic

**Goal**: Add `evaluation_angles` to `Topic` model so the question generator has structured direction per topic rather than just a name string.

> [!NOTE]
> This is a quality improvement, not a bug fix. Can be done independently after Phase 1-3 are stable.

### Files Changed

#### [MODIFY] [plan_model.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/models/plan_model.py)

```python
class Topic(BaseModel):
    topic_id: str
    topic: str
    source: str
    weight: float
    max_question_count: int  # Kept as soft guidance for router
    evaluation_angles: List[str] = []  # NEW: ["conceptual", "practical tradeoffs", "edge cases"]
```

#### [MODIFY] [planner/prompt.py](file:///Users/sufi_spryzen/Knowledge Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/planner/prompt.py)

**What changes**:
- Instruct the planner to generate 2-3 `evaluation_angles` per topic.
- These angles are ordered: broad → deep. The question generator uses them as targets across the topic's questions.

#### [MODIFY] [question_generator/prompt.py](file:///Users/sufi_spryzen/Knowledge Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/question_generator/prompt.py)

**What changes**:
- In `dependent_question_prompt` (and `topic_transition_prompt`): include `topic.evaluation_angles` in the TOPIC CONTEXT block so the LLM has structured direction.
- For `dependent_new_angle` intent: if router's `focus` is empty but `evaluation_angles` exist, pick the angle matching the current question count (angle #k).

---

## Execution Order

```
Phase 1 (Router)          — unblocks everything else; independent of phases 2-4
Phase 2 (Phase Summarizer) — depends on Phase 1 (needs to know about phase transitions)
Phase 3 (Question Gen)    — depends on Phase 1 (router intent drives branch selection)
Phase 4 (Planner)         — independent; do after 1-3 are stable
```

> Phases 2 and 3 can be done in parallel once Phase 1 is complete.

---

## Open Questions

> [!IMPORTANT]
> **Q1: `current_turn_status` field name** — After Phase 1, `current_turn_status` changes meaning. It previously held the router's `reason` paragraph. Now it holds the `intent` string (e.g., `"advance_topic"`). Should we rename this field to `router_intent` and add `router_focus` as a separate field in `SystemState`? This would be cleaner. Confirm before Phase 1 starts.

> [!IMPORTANT]
> **Q2: Router chat context scope** — For the router prompt, I'm proposing to send only current-topic turns (not full history). But on the very first question of a topic, there are 0 turns yet — the router is evaluating an answer that just came in. So it should receive: the turns for the current topic (including the turn that was just answered), plus optionally the last 1 turn from the previous topic. Is this the right window?

> [!NOTE]
> **Q3: Phase transition detection** — The `phase_transition_occurred` flag I'm adding is set in `question_generator`. Alternatively, `router` could set it (since router knows about topic advancement and could look up if the next topic is in a new phase). Which agent should own this flag?

> [!NOTE]
> **Q4: `max_question_count` field** — With Phase 1, this field becomes a "soft guidance" for the router rather than a hard limit. The planner prompt should be updated to describe it as a soft guideline. Do you want to rename it to `suggested_question_count` in the model, or keep the name for backward compatibility?
