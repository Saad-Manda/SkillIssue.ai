# SkillIssue.ai — Phase-Wise Fixation Plan

> **Scope**: Architecture redesign across Router, Phase Summarizer, Question Generator, and Planner based on user's design decisions and system diagnosis.

---

## Design Decisions Resolved & Locked In

We have aligned on the following core design decisions, which are now built into the implementation plan below:

### 1. 2-Case Question Model (not 3)

| Case | Name | Meaning |
|------|------|---------|
| `DEPENDENT` | Follow-up / New Angle | Same topic, builds on context. Covers BOTH probing a specific claim (`dependent_followup`) AND exploring a different facet of the same topic (`dependent_new_angle`). Both use the same context base. |
| `TOPIC_CHANGED` | Topic transition | Router has decided to move to the next topic. |

### 2. Router Gives Intent and Focus, Not Reason

The router no longer returns `{ is_dependent: bool, reason: str }`. It returns structured intent and focus:
```json
{
  "intent": "dependent_followup | dependent_new_angle | advance_topic",
  "focus": "short phrase (what to probe or what angle to explore; empty if advance_topic)"
}
```

### 3. State Field Naming & Cleaning
To keep the LangGraph `SystemState` clean and strongly typed, we are modifying the following state fields:
- **Rename** `current_turn_status` to `router_intent` (representing the intent string: `"dependent_followup"`, `"dependent_new_angle"`, or `"advance_topic"`).
- **Add** `router_focus: str = ""` (holding the focus phrase returned by the router).
- **Add** `phase_transition_occurred: bool = False` (set by the router when it decides to advance the topic to a new phase).
- **Add** `completed_phase_name: Optional[str] = None` (set by the router when a phase transition is detected, holding the name of the phase that just ended).

### 4. Topic Counter is Soft, Not Hard
- The question count per topic is tracked in `current_topic_question_count` (`k`).
- There are **NO Python/code-level comparisons** (like `if k >= max_question_count:`) forcing a topic transition.
- The router prompt is updated to keep the question count and soft limit guideline in mind to ensure the interview advances and doesn't get stuck. The LLM alone decides when to advance.

### 5. Router Chat Context Scope
To maximize latency wins and keep context relevant:
- The chat context sent to the router consists **only of the turns of the currently running phase** (not the full history across all phases).
- **Previous Phase Summary Logic**:
  - For the first 1-2 questions of a fresh phase (when the count of turns in the current phase is `<= 2`), we include the summary of the previous phase(s) in the router prompt.
  - After 1-2 questions in the phase (when current phase turns `> 2`), the previous phase summary is omitted entirely.

### 6. Phase Transition Detection by Router
- The **Router** owns the phase transition detection. When the router decides `intent == "advance_topic"`, it looks up the next topic in the plan.
- If the next topic's phase differs from the current phase, the router sets `phase_transition_occurred = True` and `completed_phase_name = current_phase_name`.
- On the subsequent resume of the graph (after the candidate answers the transition question), the `phase_summarizer` runs, detects `phase_transition_occurred == True`, summarizes the completed phase, appends it to the phase summaries list, and resets the flags.
- If `phase_transition_occurred == False`, the `phase_summarizer` immediately returns the state in O(1) time without calling the LLM.

---

## Phase 1 — Router Redesign

**Goal**: Replace binary `is_dependent` + `reason` with intent-based `intent` + `focus`. Remove Python-level hard counter check. Implement phase-scoped chat context and previous phase summary inclusion logic. Centralize phase transition detection.

### Files Changed

#### [MODIFY] [states.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/models/states/states.py)
- Rename `current_turn_status` to `router_intent`.
- Add `router_focus: str = ""`.
- Add `phase_transition_occurred: bool = False`.
- Add `completed_phase_name: Optional[str] = None`.

#### [MODIFY] [state_init.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/models/states/state_init.py)
- Update initialization for renamed and new state fields (`router_intent = None`, `router_focus = ""`, `phase_transition_occurred = False`, `completed_phase_name = None`).

#### [MODIFY] [router/agent.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/router/agent.py)
- Remove the Python-level hard limit comparison `if k >= max_question_count:`.
- Perform phase transition detection if the router LLM decides to advance the topic:
  - Retrieve the next topic using `get_next_topic(plan, current_phase_name, current_topic_id)`.
  - If the next topic has a different phase than `current_phase_name`:
    - Set `system_state.phase_transition_occurred = True`
    - Set `system_state.completed_phase_name = system_state.current_phase_name`
  - If there is no next topic (end of interview), set `system_state.should_generate_report = True`.
- Scope the chat history passed to the router:
  - Filter `chat_history` to include only turns matching `system_state.current_phase_name`.
  - If the count of current phase turns is `<= 2`, fetch `phase_summary` from session state and retrieve the summary of the last completed phase (if any) to pass as background context.
  - Otherwise, do not fetch or pass the previous phase summary.
- Map the LLM's JSON output `{ intent, focus }` to:
  - `system_state.router_intent = intent`
  - `system_state.router_focus = focus`
  - `system_state.is_curr_question_independent = (intent == "advance_topic")`

#### [MODIFY] [router/prompt.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/router/prompt.py)
- Rewrite prompt to guide the LLM on the three intents: `advance_topic`, `dependent_followup`, and `dependent_new_angle`.
- Instruct the router to always keep the question count (`k`) and soft limit guideline in mind to prevent getting stuck in one topic.
- Format the input context:
  - Current phase turns only.
  - Optional previous phase summary block (only present if turns <= 2).
  - Current question counter `k` and `max_question_count` soft limit.
- Schema output instruction: `{ "intent": "...", "focus": "..." }`

---

## Phase 2 — Phase Summarizer Redesign

**Goal**: Optimize `phase_summarizer` to run only when a phase transition has occurred. Make it a fast no-op in other turns. Provide all turns of the completed phase as input.

### Files Changed

#### [MODIFY] [phase_summarizer/agent.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/phase_summarizer/agent.py)
- Check `system_state.phase_transition_occurred`. If `False`, return the system state immediately (O(1) no-op bypass).
- If `True`:
  - Fetch all turns from `chat_history` matching `system_state.completed_phase_name`.
  - Fetch all existing summaries from `phase_summary` in Redis.
  - Invoke the LLM to generate the summary for the completed phase.
  - Append the new phase summary to the list in Redis.
  - Reset `system_state.phase_transition_occurred = False` and `system_state.completed_phase_name = None`.
  - Return the updated state.

#### [MODIFY] [phase_summarizer/prompt.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/phase_summarizer/prompt.py)
- Remove `same_phase_summary_prompt` entirely.
- Rewrite `phase_change_summary_prompt` → `phase_summary_prompt(...)` to accept all turns of the completed phase and prior phase summaries, creating a complete summary of the finished phase.

---

## Phase 3 — Question Generator: Collapse to 2 Branches

**Goal**: Remove the `INDEPENDENT` branch. Collapse to `TOPIC_CHANGED` and `DEPENDENT` only. Eliminate complex history slicing.

### Files Changed

#### [MODIFY] [question_generator/agent.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/question_generator/agent.py)
- Eliminate the `INDEPENDENT` branch entirely.
- Read `system_state.router_intent` instead of `is_indep` and `current_turn_status`.
- Two cases:
  1. `router_intent == "advance_topic"` → Move to the next topic in the plan. Call `topic_transition_prompt`. Reset `current_topic_question_count = 1`.
  2. `router_intent in ("dependent_followup", "dependent_new_angle")` → Call `dependent_question_prompt`. Pass `router_focus` as the target focus directive. Increment `current_topic_question_count += 1`.
- Simplify chat context parsing (no more `chat_history_pre_topic` slicing). Pass the current topic turns as context for the dependent branch.

#### [MODIFY] [question_generator/prompt.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/question_generator/prompt.py)
- Remove `independent_question_prompt` non-transition mode. Keep only transition mode as `topic_transition_prompt`.
- Update `dependent_question_prompt` to receive the `router_focus` directive. Customize instructions based on whether it is a `dependent_followup` (probing specific points of prior responses) or `dependent_new_angle` (exploring a new facet of the same topic).

---

## Phase 4 — Planner Enhancement: evaluation_angles per Topic

**Goal**: Update planner prompt to mark `max_question_count` as a soft guideline, and add `evaluation_angles` to the generated plan.

### Files Changed

#### [MODIFY] [plan_model.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/models/plan_model.py)
- Keep `max_question_count` as is.
- Add `evaluation_angles: List[str] = []` to `Topic` model.

#### [MODIFY] [planner/prompt.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/planner/prompt.py)
- Update planner prompt instructions to explicitly state that `max_question_count` is a **soft guideline** rather than a hard limit.
- Instruct the planner to generate 2-3 specific `evaluation_angles` per topic (e.g. `["conceptual understanding", "trade-offs", "edge cases"]`).

#### [MODIFY] [question_generator/prompt.py](file:///Users/sufi_spryzen/Knowledge%20Base/Dev_Workspace/Projects/SkillIssue/SkillIssue.ai/src/agents/question_generator/prompt.py)
- Include `evaluation_angles` in the topic context block.
- For `dependent_new_angle` intent, if `router_focus` is empty, target the next angle based on `current_topic_question_count` (e.g., angle #k).

---

## Execution Order

```
Phase 1 (Router)          — unblocks everything else; updates states & prompts
Phase 2 (Phase Summarizer) — depends on Phase 1 (uses phase_transition_occurred)
Phase 3 (Question Gen)    — depends on Phase 1 (uses router_intent & router_focus)
Phase 4 (Planner)         — independent; do after 1-3 are stable
```

---

## Verification Plan

### Automated Tests
- Run existing test suites: `pytest src/tests/` to verify baseline behavior.
- Add new unit tests for the updated prompt contexts and new state fields in `src/tests/`.

### Manual Verification
- Run the interactive Gradio interface (`python src/gradio.py` or through the FastAPI server) to perform sample interview runs and verify routing decisions, topic transitions, and phase summary outputs.
