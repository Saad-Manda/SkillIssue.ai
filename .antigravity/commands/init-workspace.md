---
description: Scaffold a complete AI-native workflow environment into any greenfield or brownfield project directory
argument-hint: [target-directory-path]
---

# Init Workspace: Bootstrap AI-Native Development Environment

## Overview

This command installs the complete **Antigravity AI Workflow** scaffold — including commands, skills, templates, reference specs, and the project constitution files — into any greenfield or brownfield project directory in a single operation.

> [!IMPORTANT]
> **No source code is touched.** This command only creates AI-workflow documentation and tooling files. All existing application code is preserved without modification.

---

## Mission

Given a `$ARGUMENTS` target path (or the current workspace root if omitted), install:

| Asset | Destination | Purpose |
|-------|-------------|---------|
| `.antigravity/` | `<target>/.antigravity/` | Commands, skills, templates, and plans directories |
| `ANTIGRAVITY.md` | `<target>/ANTIGRAVITY.md` | Project constitution / global rules |
| `PRD.md` | `<target>/PRD.md` | Product Requirements Document |
| `reference/` | `<target>/reference/` | Architecture, API, database, and testing specs |

---

## Phase 1: DETECT Environment

### 1.1 Resolve Source & Target Paths

- The **Source Vault** is the workspace where this command file lives (i.e., the directory containing `.antigravity/`).
  - Use `list_dir` on the current workspace root to confirm that `.antigravity/`, `ANTIGRAVITY.md`, and `PRD.md` exist.
  - Store this as `SOURCE_ROOT`.

- The **Target Directory** is `$ARGUMENTS` if provided, otherwise use the current workspace root.
  - Use `list_dir` to check whether `$ARGUMENTS` is an existing directory.
  - If it does not exist, use `run_command` to create it: `mkdir -p "$ARGUMENTS"`.
  - Store this as `TARGET_ROOT`.

### 1.2 Detect Mode (Greenfield vs Brownfield)

Inspect the target directory contents using `list_dir`:

| Condition | Mode |
|-----------|------|
| Target is empty or contains only dotfiles and `.git/` | **🟢 Greenfield** — clean new project |
| Target has source code files, `package.json`, `src/`, `apps/`, etc. | **🟡 Brownfield** — existing codebase overlay |

Print the detected mode clearly in the output before proceeding.

---

## Phase 2: COPY Workflow Assets

Perform all copy operations using `run_command` with `cp` and `mkdir -p` commands. Use the safe copy strategy below — **never overwrite existing files** unless explicitly requested.

### 2.1 Copy `.antigravity/` Directory

```bash
# Create target directory structure first
mkdir -p "$TARGET_ROOT/.antigravity/commands"
mkdir -p "$TARGET_ROOT/.antigravity/skills/agent-browser"
mkdir -p "$TARGET_ROOT/.antigravity/skills/e2e-test"
mkdir -p "$TARGET_ROOT/.antigravity/templates/reference"
mkdir -p "$TARGET_ROOT/.antigravity/plans"
```

Then copy each asset group individually using `run_command`:

**Core config files** (always copy, these are framework — not project-specific):
```bash
cp "$SOURCE_ROOT/.antigravity/README.md" "$TARGET_ROOT/.antigravity/README.md"
cp "$SOURCE_ROOT/.antigravity/ANTIGRAVITY-template.md" "$TARGET_ROOT/.antigravity/ANTIGRAVITY-template.md"
```

**Commands** (always copy — these are universal workflow commands):
```bash
cp "$SOURCE_ROOT/.antigravity/commands/prime.md"       "$TARGET_ROOT/.antigravity/commands/prime.md"
cp "$SOURCE_ROOT/.antigravity/commands/create-rules.md" "$TARGET_ROOT/.antigravity/commands/create-rules.md"
cp "$SOURCE_ROOT/.antigravity/commands/create-prd.md"  "$TARGET_ROOT/.antigravity/commands/create-prd.md"
cp "$SOURCE_ROOT/.antigravity/commands/plan-feature.md" "$TARGET_ROOT/.antigravity/commands/plan-feature.md"
cp "$SOURCE_ROOT/.antigravity/commands/execute.md"     "$TARGET_ROOT/.antigravity/commands/execute.md"
cp "$SOURCE_ROOT/.antigravity/commands/commit.md"      "$TARGET_ROOT/.antigravity/commands/commit.md"
cp "$SOURCE_ROOT/.antigravity/commands/init-workspace.md" "$TARGET_ROOT/.antigravity/commands/init-workspace.md"
```

**Skills** (always copy — these are reusable technical skills):
```bash
cp "$SOURCE_ROOT/.antigravity/skills/agent-browser/SKILL.md" "$TARGET_ROOT/.antigravity/skills/agent-browser/SKILL.md"
cp "$SOURCE_ROOT/.antigravity/skills/e2e-test/SKILL.md"      "$TARGET_ROOT/.antigravity/skills/e2e-test/SKILL.md"
```

**Templates** (always copy — these are starter blueprints):
```bash
cp "$SOURCE_ROOT/.antigravity/templates/PRD-template.md"                    "$TARGET_ROOT/.antigravity/templates/PRD-template.md"
cp "$SOURCE_ROOT/.antigravity/templates/reference/api-template.md"          "$TARGET_ROOT/.antigravity/templates/reference/api-template.md"
cp "$SOURCE_ROOT/.antigravity/templates/reference/architecture-template.md" "$TARGET_ROOT/.antigravity/templates/reference/architecture-template.md"
cp "$SOURCE_ROOT/.antigravity/templates/reference/database-template.md"     "$TARGET_ROOT/.antigravity/templates/reference/database-template.md"
cp "$SOURCE_ROOT/.antigravity/templates/reference/testing-template.md"      "$TARGET_ROOT/.antigravity/templates/reference/testing-template.md"
```

### 2.2 Copy Reference Specs

Create the `reference/` directory and populate with templated spec files. **Skip if the target file already exists** to avoid overwriting existing documentation:

```bash
mkdir -p "$TARGET_ROOT/reference"
```

For each spec (`api`, `architecture`, `database`, `testing`):
- Check if `$TARGET_ROOT/reference/{spec}.md` already exists using `list_dir` or a `test -f` check via `run_command`.
- If it **does NOT exist**: copy `$SOURCE_ROOT/.antigravity/templates/reference/{spec}-template.md` → `$TARGET_ROOT/reference/{spec}.md`
- If it **already exists**: log a yellow warning `"reference/{spec}.md already exists — skipping."` and skip.

### 2.3 Install ANTIGRAVITY.md

The project constitution file. Use the template as the base:

- If `$TARGET_ROOT/ANTIGRAVITY.md` **does NOT exist**:
  - **Greenfield**: Copy from `$SOURCE_ROOT/.antigravity/ANTIGRAVITY-template.md` as-is.
  - **Brownfield**: Copy from `$SOURCE_ROOT/.antigravity/ANTIGRAVITY-template.md` but set a reminder in the output to run `create-rules.md` to auto-populate it from the codebase.
- If it **already exists**: Log `"ANTIGRAVITY.md already exists — skipping to preserve your configuration."` and skip.

### 2.4 Install PRD.md

The product requirements document starter:

- If `$TARGET_ROOT/PRD.md` **does NOT exist**:
  - Copy `$SOURCE_ROOT/.antigravity/templates/PRD-template.md` → `$TARGET_ROOT/PRD.md`
- If it **already exists**: Log `"PRD.md already exists — skipping to preserve existing requirements."` and skip.

---

## Phase 3: VERIFY Installation

After all copy operations, verify the installation using `list_dir` to confirm each of the following paths exist in `TARGET_ROOT`:

```text
✔  .antigravity/README.md
✔  .antigravity/ANTIGRAVITY-template.md
✔  .antigravity/commands/prime.md
✔  .antigravity/commands/create-rules.md
✔  .antigravity/commands/create-prd.md
✔  .antigravity/commands/plan-feature.md
✔  .antigravity/commands/execute.md
✔  .antigravity/commands/commit.md
✔  .antigravity/commands/init-workspace.md
✔  .antigravity/skills/agent-browser/SKILL.md
✔  .antigravity/skills/e2e-test/SKILL.md
✔  .antigravity/templates/PRD-template.md
✔  .antigravity/templates/reference/api-template.md
✔  .antigravity/templates/reference/architecture-template.md
✔  .antigravity/templates/reference/database-template.md
✔  .antigravity/templates/reference/testing-template.md
✔  .antigravity/plans/              (empty directory — ready for plans)
✔  reference/api.md
✔  reference/architecture.md
✔  reference/database.md
✔  reference/testing.md
✔  ANTIGRAVITY.md
✔  PRD.md
```

Report any missing items as errors. Report skipped items in yellow.

---

## Phase 4: REGISTER Global Shell Command (Optional)

If the user asked to install a global shell command, use `run_command` to register the `init-ai-workflow.sh` script as a shell alias:

```bash
bash "$SOURCE_ROOT/scripts/init-ai-workflow.sh" --install
```

Then instruct the user to reload their shell:
```bash
source ~/.zshrc
```

After installation, the command `init-ai [target-path]` becomes available globally from any terminal directory.

---

## Phase 5: OUTPUT Report

Generate a clear, well-formatted completion summary in the conversation:

### ✅ Installation Complete

Print a full structured report:

```
╔══════════════════════════════════════════════════════════╗
║     Antigravity AI Workflow — Installation Complete       ║
╚══════════════════════════════════════════════════════════╝

  Mode:    🟢 Greenfield  |  🟡 Brownfield
  Target:  /absolute/path/to/target

  INSTALLED:
  ✔  .antigravity/  — 7 commands, 2 skills, 5 templates
  ✔  reference/     — 4 spec files
  ✔  ANTIGRAVITY.md — Project constitution
  ✔  PRD.md         — Product requirements starter

  SKIPPED (already existed):
  ⚠  reference/api.md — preserved existing file
```

---

### 🚀 Next Steps (Mode-Specific)

#### If Greenfield:
1. **Define your product** — Edit `PRD.md` with your requirements using the structured template as a guide. Or ask Antigravity: *"Help me fill out PRD.md for a [type of app] that does [functionality]."*
2. **Set up rules** — Edit `ANTIGRAVITY.md` with your tech stack, or ask: *"Read `.antigravity/commands/create-rules.md` and generate rules from scratch."*
3. **Prime the AI** — At the start of each new session, say: *"Prime yourself using `.antigravity/commands/prime.md`."*
4. **Plan your first feature** — Say: *"Plan [Feature Name] using `.antigravity/commands/plan-feature.md`."*

#### If Brownfield:
1. **Auto-generate rules** — Ask Antigravity: *"Analyze our codebase and generate global rules using `.antigravity/commands/create-rules.md`."* This will inspect your stack and populate `ANTIGRAVITY.md` automatically.
2. **Fill reference specs** — Edit the generated `reference/` files with your existing API contracts, DB schema, and architecture decisions.
3. **Prime the AI** — Say: *"Prime yourself with our project context using `.antigravity/commands/prime.md`."*
4. **Start planning features** — Use `.antigravity/commands/plan-feature.md` for any new capabilities.

---

## Recommended Workflow After Setup

```
Session Start
     │
     ▼
 prime.md          ← Load context into Antigravity memory
     │
     ▼
 create-prd.md     ← Define requirements (or edit PRD.md manually)
     │
     ▼
 plan-feature.md   ← Build implementation plan artifact
     │
     ▼
 execute.md        ← Execute the plan with precision tools
     │
     ▼
 commit.md         ← Atomic semantic git commits
```
