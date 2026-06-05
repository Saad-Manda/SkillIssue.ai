# Bug Fix Plan: Conversational Bridging in Question Generator Prompts

> [!IMPORTANT]
> **Status**: Confirmed — Root causes verified against live source files.

---

## 1. Bug Confirmation: Is the Report Correct?

**Yes. Partially confirmed and partially mis-described.** After reading every relevant source file, the core symptom is real but the report's diagnosis of the source is outdated. Here is the precise current state:

### What the report claims
> The prompts "explicitly and strictly forbid the LLM from doing this" via rules like `"Generate ONLY one interview question"` and `"Do NOT include explanation, labels..."`, and `independent_question_prompt` commands `"The question must NOT require the candidate's last answer to be understandable"`.

### What the code actually does **today** (after Bug 2 fix was partially applied)

Reading `prompt.py` carefully:

**In `independent_question_prompt` (L59–L63):**
```python
CONVERSATION FLOW (MANDATORY)
- Use RECENT CHAT CONTEXT to maintain continuity of tone, seniority level, and progression.
- The question must include a short conversational bridge that links to the ongoing interview flow.
- The bridge can reference high-level direction (e.g., interests, role focus, phase shift), but not depend on details of the last answer.
- Avoid abrupt topic jumps; move from broad → role-aligned → technical depth naturally.
```

A `CONVERSATION FLOW` block exists. It asks for a "short conversational bridge." **But it is undermined by the `OUTPUT RULES` block (L97–L103) in the same function**, which is the critical tension point:

```python
OUTPUT RULES:
- Generate ONLY one interview question.
- Keep it concise.
- Do NOT include explanation, labels, numbering, JSON, or meta commentary.
- Do NOT ask multi-part or layered questions.
```

The rule `"Generate ONLY one interview question"` directly contradicts the `CONVERSATION FLOW` block's intent. The LLM receives **two conflicting instructions**: "include a conversational bridge" vs "output ONLY one interview question." In practice, the stricter, more explicit OUTPUT RULES win — the bridge is dropped.

**In `dependent_question_prompt` (L148–L155):**
```python
BRANCH MODE: DEPENDENT (HARD CONSTRAINT)
- The new question must be a follow-up question.
- It must explicitly depend on prior conversation context.
```

There is **no** `CONVERSATION FLOW` block in the dependent prompt at all. No bridge instruction exists. The `OUTPUT RULES` are identical (L179–L184) — same restrictive constraint.

**The independent_question_prompt `BRANCH MODE` block (L66–L71):**
```python
BRANCH MODE: INDEPENDENT (STRICT)
- The question must NOT require the candidate's last answer to be understandable or answerable.
- The question must NOT probe, challenge, or drill into a specific claim from the last answer.
```

This is the direct cause the bug report identifies. "Must NOT require..." is a **semantic constraint** on the question itself (correct, for maintaining topical independence). But the LLM conflates this with "do not acknowledge the prior conversation at all," creating abruptness.

---

## 2. Root Cause Analysis

### Root Cause 1 — OUTPUT RULES override CONVERSATION FLOW via conflicting instruction weight

**File**: `src/agents/question_generator/prompt.py` L97–L103

The phrase `"Generate ONLY one interview question"` reads to the LLM as: *"your entire response must be a question sentence."* The word **ONLY** and the constraint **one interview question** instruct the model to strip any non-question preamble. This fatally collides with the bridge instruction:

| Instruction | Location | Effect on LLM |
|---|---|---|
| `"include a short conversational bridge"` | `CONVERSATION FLOW`, system prompt | Encourages 1–2 acknowledgment sentences before the question |
| `"Generate ONLY one interview question"` | `OUTPUT RULES`, system prompt | Overrides — LLM strips everything except the bare question |
| `"Do NOT include explanation, labels..."` | `OUTPUT RULES`, system prompt | Further suppresses any bridging language |

The ONLY keyword is the lynchpin. LLMs treat absolute quantifier constraints (`ONLY`, `MUST NOT`, `NEVER`) as hard stops that override softer stylistic guidance.

### Root Cause 2 — `dependent_question_prompt` has zero conversational bridge instruction

**File**: `src/agents/question_generator/prompt.py` L128–L184

The `dependent_question_prompt` function has:
- A `FOLLOW-UP QUALITY RULES` block — ensures the question is anchored to prior context ✅
- A `BRANCH MODE: DEPENDENT` block — enforces follow-up semantics ✅
- **No** `CONVERSATION FLOW` block — there is zero instruction to acknowledge the candidate's prior answer conversationally ❌
- The same inhibiting `OUTPUT RULES` block ❌

Dependent questions are arguably the most important place for bridging: the interviewer is explicitly building on what the candidate just said. Yet this prompt is the one with the largest gap.

### Root Cause 3 — BRANCH MODE constraint is semantically over-broad

**File**: `src/agents/question_generator/prompt.py` L66–L71

```python
BRANCH MODE: INDEPENDENT (STRICT)
- The question must NOT require the candidate's last answer to be understandable or answerable.
```

This instruction is architecturally correct — an independent question must stand alone. However, the phrasing bleeds into conversational behavior. The LLM interprets "must not require the candidate's last answer" as "should not reference or relate to the candidate's last answer in any way" — which suppresses even a brief natural acknowledgment like *"That's a solid point on scalability. Let's shift gears slightly..."*.

The constraint correctly targets the **question content** but incorrectly suppresses **conversational framing**.

### Root Cause 4 — OUTPUT RULES are positioned as the **last** instruction before message construction

**File**: `src/agents/question_generator/prompt.py` L105 and L187

```python
system_content = base_instruction + "\n" + mode_instruction + "\n" + constraints
```

In LLM prompt engineering, the **final instructions in the system prompt carry the most weight** (recency bias in attention). By placing the `OUTPUT RULES` (`constraints`) last in the system prompt, they are the most salient instruction block when the model generates output. This guarantees the ONLY-question rule dominates over the earlier bridge request.

### Root Cause Summary Table

| Root Cause | Location | Why it Causes the Bug |
|---|---|---|
| RC1: `"Generate ONLY one interview question"` conflicts with bridge instruction | `OUTPUT RULES` in both prompts | `ONLY` is an absolute quantifier; overrides softer bridge guidance |
| RC2: `dependent_question_prompt` has no bridge instruction at all | `dependent_question_prompt` L128–L155 | Even if OUTPUT RULES were relaxed, there's nothing to enable bridging |
| RC3: BRANCH MODE phrasing is semantically over-broad | `independent_question_prompt` L66–L71 | "must NOT require last answer" suppresses conversational framing, not just question content |
| RC4: `constraints` block is last in system prompt | Both prompt functions L105, L187 | Recency bias gives OUTPUT RULES highest priority in LLM attention |

---

## 3. Impact Assessment

| Symptom | Root Cause(s) |
|---|---|
| Raw abrupt questions with no preamble | RC1, RC4 — OUTPUT RULES dominate, strip any bridge language |
| Dependent follow-ups feel interrogatory | RC2 — no bridge instruction exists; RC1 — OUTPUT RULES eliminate preamble |
| Independent topic transitions feel like interrogation restarts | RC3 — "must NOT require last answer" bleeds into conversational suppression |
| Candidate feels ignored/not heard | RC1, RC2 — their previous answer is never acknowledged before the next question arrives |
| Interviewer feels robotic vs. conversational | All RCs compound — zero warmth, zero continuity of dialogue tone |

---

## 4. The Fix

### Strategy

The fix requires three coordinated changes, all in `prompt.py`:

1. **Restructure OUTPUT RULES** in both prompt functions to permit (and explicitly shape) a two-part response format: a brief acknowledgment followed by the question. This removes the conflicting `ONLY one question` constraint without opening the floodgates to verbose LLM behavior.

2. **Add a `CONVERSATION FLOW` block to `dependent_question_prompt`** to mirror the one already present in `independent_question_prompt`, tailored to dependent/follow-up context.

3. **Refine the BRANCH MODE constraint in `independent_question_prompt`** to narrow it to question *content* rather than conversational *framing*.

### Design Principles

- The bridge must be **mandatory but bounded**: 1–2 sentences maximum.
- The bridge must be **natural, not formulaic**: avoid prescribing exact phrases like "Great answer!" or "That's interesting."
- The bridge for **dependent** questions should explicitly acknowledge what the candidate said.
- The bridge for **independent** questions should acknowledge high-level direction (phase shift, topic change) without depending on specific last-answer content.
- The constraint `"ONLY one interview question"` should be replaced with a **two-part output format** instruction.

### Files to Change

| File | Change |
|---|---|
| `src/agents/question_generator/prompt.py` | (1) Restructure `OUTPUT RULES` in both functions; (2) Add `CONVERSATION FLOW` to `dependent_question_prompt`; (3) Narrow `BRANCH MODE` phrasing in `independent_question_prompt` |

> [!NOTE]
> No changes needed to `agent.py`, `router/`, `states.py`, or any other file. This bug is entirely contained within the LLM prompt instructions in `prompt.py`.

---

## 5. Implementation Checklist

### Step 1 — Fix `independent_question_prompt`: Narrow BRANCH MODE wording

**File**: `src/agents/question_generator/prompt.py` L66–L71

The goal is to clarify that the "must NOT require" constraint applies to the **question content**, not to the **conversational opening**.

```diff
 mode_instruction = """
 BRANCH MODE: INDEPENDENT (STRICT)
-- The question must NOT require the candidate's last answer to be understandable or answerable.
-- The question must NOT probe, challenge, or drill into a specific claim from the last answer.
+- The question itself must NOT require the candidate's last answer to be understandable or answerable.
+- The question itself must NOT probe, challenge, or drill into a specific claim from the last answer.
+- You MAY (and should) open with a brief 1-2 sentence acknowledgment that references the overall
+  conversation direction — but the question that follows must stand alone.
 - The question must be aligned to current phase/topic.
 """
```

### Step 2 — Fix `independent_question_prompt`: Replace OUTPUT RULES with two-part format

**File**: `src/agents/question_generator/prompt.py` L97–L103

```diff
 constraints = """
 OUTPUT RULES:
-- Generate ONLY one interview question.
-- Keep it concise.
-- Do NOT include explanation, labels, numbering, JSON, or meta commentary.
-- Do NOT ask multi-part or layered questions.
+Your response MUST have exactly two parts, in this order:
+
+1. BRIDGE (1–2 sentences): Naturally acknowledge the conversation so far — the candidate's general
+   approach, a topic they covered, or the direction of the interview. Do NOT evaluate or praise
+   with hollow phrases ("Great answer!", "Interesting!"). Be natural and human.
+2. QUESTION (1 sentence): The next interview question. It must be self-contained — no dependency
+   on the last answer's specifics.
+
+Do NOT include labels, numbering, JSON, or meta commentary.
+Do NOT ask multi-part or layered questions.
+Keep the total response concise (3–5 sentences combined).
 """
```

### Step 3 — Fix `dependent_question_prompt`: Add `CONVERSATION FLOW` block

**File**: `src/agents/question_generator/prompt.py` L128–L155

Insert a new `CONVERSATION FLOW` block into the `base_instruction` of `dependent_question_prompt`, after `QUESTION STYLE RULES`:

```diff
 base_instruction = """
 You are a practical, industry-style Technical Interviewer generating exactly one interview question.

 INTERVIEW PHILOSOPHY:
 - Evaluate clarity of thinking, fundamentals, and reasoning.
 - Ask what a real interviewer would ask in a real interview.

 FOLLOW-UP QUALITY RULES:
 - Explicitly anchor to prior context (a claim, design choice, trade-off, assumption, or gap).
 - Use prior responses to probe depth, trade-offs, edge cases, or contradictions.
 - If candidate gave a claim/design/decision earlier, ask them to justify, extend, or stress-test it.
 - Avoid generic standalone questions that could be asked without prior context.
 - Avoid repeating previously asked questions verbatim.

 QUESTION STYLE RULES:
 - Keep the question clear, conversational, and easy to understand.
 - Test one main idea only.
 - Keep scope tight and relevant.
+
+CONVERSATION FLOW (MANDATORY):
+- Before asking your question, open with 1–2 sentences that acknowledge something specific from
+  the candidate's most recent answer (a claim they made, a technology they mentioned, a trade-off
+  they described, or an approach they took).
+- The acknowledgment does NOT need to be evaluative — simply referencing what they said is enough.
+- Do NOT use hollow filler phrases ("Great answer!", "That's very interesting!").
+- The acknowledgment should flow naturally into the follow-up question.
 """
```

### Step 4 — Fix `dependent_question_prompt`: Replace OUTPUT RULES with two-part format

**File**: `src/agents/question_generator/prompt.py` L179–L184

```diff
 constraints = """
 OUTPUT RULES:
-- Generate ONLY one interview question.
-- Keep it concise.
-- Do NOT include explanation, labels, numbering, JSON, or meta commentary.
-- Do NOT ask multi-part or layered questions.
+Your response MUST have exactly two parts, in this order:
+
+1. BRIDGE (1–2 sentences): Acknowledge something specific from the candidate's prior answer —
+   a claim, a design decision, a technology choice, or a gap you observed. Be natural and
+   conversational. Do NOT use hollow filler ("Great!", "Interesting!"). Make it feel like a
+   real interviewer heard them.
+2. QUESTION (1 sentence): The follow-up question. It must directly build on the prior conversation.
+
+Do NOT include labels, numbering, JSON, or meta commentary.
+Do NOT ask multi-part or layered questions.
+Keep the total response concise (3–5 sentences combined).
 """
```

---

## 6. Expected Behaviour After Fix

### Before (current behaviour)

```
Interviewer: "What is your approach to database indexing?"
Candidate:   "I usually create indexes on high-cardinality columns. I've used B-tree indexes
              primarily in Postgres, and composite indexes when queries filter on multiple columns."
Interviewer: "How would you handle the N+1 query problem in an ORM-heavy application?"
```
*(abrupt pivot — no acknowledgment, feels like an interrogation restarting)*

### After (expected behaviour)

```
Interviewer: "What is your approach to database indexing?"
Candidate:   "I usually create indexes on high-cardinality columns. I've used B-tree indexes
              primarily in Postgres, and composite indexes when queries filter on multiple columns."
Interviewer: "You mentioned using composite indexes for multi-column query filters — that's a
              common strategy under read-heavy workloads. How would you decide when a composite
              index is worth the write overhead, especially in a write-heavy production system?"
```
*(bridge references the candidate's specific point; follow-up question is anchored and natural)*

---

## 7. Validation

After applying the fix:

```bash
# 1. Verify no import/config errors in the graph
python -c "from src.agents.orchestrator import _build_graph; _build_graph(); print('Graph OK')"

# 2. Run backend tests
pytest src/tests/ -v --cov=src --cov-report=term-missing
```

**Manual Smoke Test** — run a live interview session and verify:

| Check | Expected |
|---|---|
| After any candidate answer, the next question starts with 1–2 acknowledgment sentences | ✅ |
| The acknowledgment is specific (references something from prior answer) | ✅ |
| The acknowledgment is not hollow ("Great answer!", "Interesting!") | ✅ |
| The question portion (after the bridge) is a single, clear, well-scoped question | ✅ |
| DEPENDENT questions explicitly anchor to the candidate's specific claim | ✅ |
| INDEPENDENT questions reference overall interview direction, not specific last-answer content | ✅ |
| Total response length stays under 5 sentences | ✅ |
| TOPIC CHANGED transitions feel smooth (bridge can reference phase shift) | ✅ |

---

## 8. Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| LLM ignores the two-part format and reverts to bare question | Low | Format is specified clearly in OUTPUT RULES with `MUST`; reinforced by CONVERSATION FLOW block earlier in system prompt |
| Bridge becomes evaluative/hollow ("Great!", "Excellent!") despite instruction | Low | Explicit negative examples ("Do NOT use hollow filler") in the instruction |
| Bridge becomes too long (3+ sentences) | Low | Bounded explicitly to `1–2 sentences`; total response cap of `3–5 sentences` |
| `TOPIC CHANGED` branch gets an awkward bridge | Low | `TOPIC CHANGED` paths use `independent_question_prompt` — bridge is framed around high-level direction, not specific last-answer content. Still appropriate. |
| Token count increases | Negligible | A 1–2 sentence bridge adds ~30–50 tokens per turn. Negligible vs. the chat history payload. |
| Parsing/processing downstream is affected | None | The output is plain text consumed by `system_state.current_question = new_question` — no structured parsing is applied to the question text. Adding a bridge sentence before the question does not break any downstream consumer. |

---

## 9. Relationship to Bug 2 Fix

> [!NOTE]
> This bug is **orthogonal** to the Bug 2 fix (Router Reason Propagation). Bug 2 ensured the LLM knows *what* to ask. Bug 3 ensures the LLM knows *how* to frame it conversationally. Both fixes are needed and do not conflict. After both fixes are applied:
> - The `ROUTER DIRECTIVE` (from Bug 2) tells the LLM the specific gap to probe.
> - The `CONVERSATION FLOW` and two-part `OUTPUT RULES` (from Bug 3) tell the LLM to acknowledge the candidate before probing that gap.
> Together they produce questions that are both **targeted** (Bug 2) and **conversational** (Bug 3).
