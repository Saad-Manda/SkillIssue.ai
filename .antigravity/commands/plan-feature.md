---
description: Create a comprehensive implementation plan artifact using deep codebase analysis, parallel subagents, and precise verification steps
---

# Plan Feature: Generate Implementation Plan Artifact

## Mission

Transform a feature request or bug ticket into a **comprehensive implementation plan artifact** using Antigravity's advanced capabilities (subagents, codebase analysis tools, and structured markdown rendering).

> [!IMPORTANT]
> **No Code is Written in this Phase.**
> The sole goal of this command is to compile a context-rich, 100% correct, step-by-step plan that allows an execution agent to succeed in a single run without needing to pause for further research.

---

## The Antigravity Planning Process

### Phase 1: Feature Deciphering
- Analyze the requirements and user expectations.
- Map out affected subsystems, modules, components, and tables.
- Evaluate estimated complexity (Low, Medium, High).

### Phase 2: Parallel Codebase Research (Subagent Power)
To accelerate and deepen understanding, the planning agent should define and invoke specialized subagents using `define_subagent` and `invoke_subagent`.
- **`codebase_researcher`**: Tasked with finding similar features, naming conventions, import hierarchies, and design patterns.
- **`dependency_analyst`**: Tasked with scanning dependency files, identifying package versions, checking official documentation, and validating API compatibility.
- Use **Reactive Wakeup**: Do not poll. Simply stop calling tools and let the system notify you when subagents have returned their results.

### Phase 3: Pattern Discovery & Mapping
Extract exact patterns from the codebase:
- **File Naming & Folder Organization**: Where do files of this type live? How are they named?
- **Error Handling & Custom Exceptions**: What patterns are standard for catching and throwing errors?
- **Logging**: What logger is used? What metadata is attached to logs?
- **Testing**: What framework is used? How are mock objects and fixtures structured?

### Phase 4: Plan Compilation (Artifact Creation)
Write the resulting plan as an **implementation plan artifact** under the directory `.antigravity/plans/{kebab-case-feature-name}.md` in the workspace root.
- When creating this file using the `write_to_file` tool:
  - Set `IsArtifact` to `true`.
  - Set `ArtifactMetadata` -> `ArtifactType` to `"implementation_plan"`.
  - Provide a concise `Summary` explaining what the plan accomplishes.

---

## Implementation Plan Structure

The plan artifact must use the following structural template:

```markdown
# Feature Plan: <kebab-case-feature-name>

> [!NOTE]
> This plan has been generated through parallel codebase analysis and is optimized for one-pass execution success.

## Feature Overview & Business Value
<Detail the user needs, benefit, and core capability>

## Architectural Design & Scope
- **Feature Type**: [New Capability / Enhancement / Refactor / Bug Fix]
- **Complexity**: [Low / Medium / High]
- **Systems Affected**: [List of services, UI directories, or database schemas]
- **Dependencies**: [Any external packages or services]

## Context References

### Mandatory Codebase Files to Read
*List existing files that the execution agent MUST read using `view_file` to match style or integrate correctly:*
- `path/to/existing_file.ts` (lines 50-80) - Naming and logic pattern for X
- `path/to/service.py` - Core business helper to import from

### New Files to Create
*Specify exact paths of all new files:*
- `path/to/new_component.css` - Component styles
- `path/to/new_service.ts` - Business logic controller

### External Documentation & Best Practices
*Provide markdown links with section anchors:*
- [Official Library Docs](https://library.com/docs#feature) - Required for implementing Y

---

## Step-by-Step Tasks

Execute all tasks in strict linear order (top to bottom). Every task is atomic and has its own validation command.

### Task Keywords:
- **CREATE**: Create a new file from scratch.
- **UPDATE**: Modify a specific block inside an existing file.
- **ADD**: Insert new functions/types/components to an existing file.
- **REMOVE**: Safely delete deprecated or clean up code.
- **MIRROR**: Copy a specific pattern from another file (include file and line number reference).

---

### Phase 1: Foundation
#### Task 1.1: CREATE `path/to/file`
- **IMPLEMENT**: Detail exactly what code structures, schemas, interfaces, or mock data to define.
- **PATTERN**: Mirror pattern from `other_file:line`.
- **IMPORTS**: Specific imports required.
- **GOTCHAS**: Known edge cases, circular dependencies, or environment rules to avoid.
- **VALIDATION**: Clear shell command to run via `run_command` (e.g. build check, schema validation, or syntax lint).

---

### Phase 2: Core Implementation
#### Task 2.1: CREATE/UPDATE `path/to/file`
- **IMPLEMENT**: Core business logic, APIs, or database queries.
- **VALIDATION**: Shell command (e.g. run specific unit test).

---

### Phase 3: Integration
#### Task 3.1: UPDATE `path/to/router_or_registry`
- **IMPLEMENT**: Connect new code to existing application routers, middlewares, or lists.
- **VALIDATION**: Start application server or run system-wide checks.

---

### Phase 4: Quality & Validation
#### Task 4.1: CREATE `tests/path/to/test_file`
- **IMPLEMENT**: Unit tests, integration tests, and edge-case validations.
- **VALIDATION**: Test suite execution command (`vitest run path/to/test`, `pytest path/to/test`).

---

## Test & Manual Validation Checklist

### Automated Validation Commands
Execute in order to guarantee 100% regression-free code:
```bash
# Syntax & Types
{typecheck-command}

# Linter & Style
{lint-command}

# Unit Tests
{unit-test-command}

# Integration Tests
{integration-test-command}
```

### Manual Validation Steps
Step-by-step CLI commands (e.g., `curl` payloads) or browser workflows to manually confirm the feature works.

### Acceptance Criteria Checklist
- [ ] Feature implements all functional specifications.
- [ ] Visual design matches layout guidelines and uses correct colors/typography.
- [ ] All validation commands pass with zero warnings/errors.
- [ ] Test coverage meets or exceeds codebase standards.
- [ ] No regression in existing endpoints or UI components.
```
