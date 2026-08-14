# Antigravity Skills & Commands Workspace

Welcome to your Antigravity-native automation environment! 

We have taken reference from the `link-in-bio-page-builder` repository, extracted all skills and commands, and **fully contextualized them to exploit the unique superpowers of the Antigravity agent**.

---

## 📂 Directory Structure

All files are structured inside the `.antigravity/` folder in your workspace root:

```text
.antigravity/
├── README.md                   # This documentation hub
├── ANTIGRAVITY-template.md      # Template for creating project rules (ANTIGRAVITY.md)
├── commands/                   # Structural workflows for agent execution
│   ├── init-workspace.md       # ⭐ Scaffold the full AI workflow into any project (this!)
│   ├── prime.md                # Quick loading of codebase understanding
│   ├── create-rules.md         # Codebase analysis to generate ANTIGRAVITY.md
│   ├── create-prd.md           # Multi-dimensional Product Requirements Document writer
│   ├── plan-feature.md         # Feature planning to compile an implementation_plan artifact
│   ├── execute.md              # Performing changes from plan using chunked-replace tools
│   └── commit.md               # Conventional staging and atomic commits
├── skills/                     # Specialized technical skill instructions
│   ├── agent-browser/
│   │   └── SKILL.md            # Visual browser automation (agent-browser CLI & read_url_content)
│   └── e2e-test/
│       └── SKILL.md            # E2E orchestration with parallel subagents & reports
├── templates/                  # Starter blueprints for project files
│   ├── PRD-template.md         # Product Requirements Document starter
│   └── reference/              # Reference spec templates
│       ├── api-template.md
│       ├── architecture-template.md
│       ├── database-template.md
│       └── testing-template.md
└── plans/                      # Implementation plan artifacts (auto-created by plan-feature.md)
```

---

## ⚡ The "Antigravity Exploit": How We Contextualized the Skills

We transformed Claude Code rules into **Antigravity-native guidelines** to maximize performance, speed, and safety:

### 1. Tool Alignment & Native Utilities
- **Fast Web Scraping**: In the `agent-browser` skill, we integrated Antigravity's native `read_url_content` tool. It fetches and converts documentation pages to Markdown instantly without the overhead of starting a Chromium instance. For complex logins and UI interactions, we rely on the `agent-browser` CLI via `run_command`.
- **Precise Code Modification**: In `execute.md`, the instructions explicitly direct the agent to use Antigravity's high-efficiency chunked editing tools (`replace_file_content` for single contiguous edits and `multi_replace_file_content` for separate chunks of edits) instead of expensive and error-prone whole-file overrides.

### 2. Parallel Subagent Orchestration (E2E Test & Planning)
- **Concurrent Spawning**: In the `e2e-test` skill, instead of serial steps, we exploit Antigravity's `define_subagent` and `invoke_subagent` tools. It concurrently spins up three specialized agents (`AppResearcher`, `DatabaseResearcher`, and `BugHunter`) using `Workspace: 'share'` to analyze the codebase simultaneously.
- **Reactive Wakeup**: We instructed the agent to rely on Antigravity's reactive notifications and one-shot `schedule` timers rather than busy-polling or looping. This saves tokens and accelerates test execution.

### 3. Premium Artifact Integration
- **Interactive Progress Tracking**: In E2E testing, we utilize Antigravity's `IsArtifact: true` and `ArtifactType: 'task'` metadata to render visual, interactive checklists.
- **Rich Document Rendering**: In `create-prd.md` and `plan-feature.md`, we integrated Github alerts (`> [!NOTE]`, `> [!IMPORTANT]`, etc.), GFM tables, and Mermaid flowcharts. When compiled as artifacts, these documents render with premium typography and diagrams in your UI.

---

## 🛠️ How to Trigger these Skills & Commands

You can tell Antigravity to run any of these commands by referencing them in your prompts. When Antigravity executes them:
1. It will load the target file from `.antigravity/` using the `view_file` tool.
2. It will set `IsSkillFile: true` in the `view_file` call, which informs the agent's system to strictly treat the Markdown instructions as active operational skills.
3. It will run the tools (subagents, shell processes, or code replacements) exactly as instructed.

### Try these requests:
- *"**Bootstrap a new project** — Initialize a new project at `~/projects/myapp` using `.antigravity/commands/init-workspace.md`."*
- *"**Prime yourself** with our project context using `.antigravity/commands/prime.md`."*
- *"**Analyze our codebase** and generate custom rules using `.antigravity/commands/create-rules.md`."*
- *"**Write a PRD** for our new feature using `.antigravity/commands/create-prd.md`."*
- *"**Plan a new feature** — Use `.antigravity/commands/plan-feature.md` to build an implementation plan for [Feature Name]."*
- *"**Execute the plan** at `.antigravity/plans/my-feature.md` using `.antigravity/commands/execute.md`."*
- *"**Commit the changes** using `.antigravity/commands/commit.md`."*
- *"**Run a full E2E test** following `.antigravity/skills/e2e-test/SKILL.md`."*

### Recommended Daily Workflow:
```
New Session   →  prime.md          (load context)
New Feature   →  plan-feature.md   (create plan artifact)
Implement     →  execute.md        (precise code changes)
Ship          →  commit.md         (semantic git commit)
New Project   →  init-workspace.md (bootstrap anywhere!)
```
