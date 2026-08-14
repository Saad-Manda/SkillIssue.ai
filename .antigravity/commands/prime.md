# Prime: Load Project Context for Antigravity

## Objective

Build a comprehensive understanding of the codebase by analyzing its structure, documentation, and key files using Antigravity's advanced toolset.

## Process

### 1. Analyze Project Structure

- **List Directory Contents**: Use the `list_dir` tool to recursively explore the workspace root. Identify major folders (`src/`, `app/`, `tests/`, etc.).
- **List Tracked Files**: Use `run_command` to run `git ls-files` to see all version-controlled files.
- **Find Specific File Patterns**: Use `grep_search` or `list_dir` to find configuration files (e.g., `package.json`, `tsconfig.json`, `pyproject.toml`, `drizzle.config.ts`).

### 2. Read Core Documentation

- Use `view_file` to read the following if they exist:
  - `README.md` at the project root.
  - `ANTIGRAVITY.md` or `CLAUDE.md` (project-specific rules).
  - Product Requirements Documents (`PRD.md`) or design specs.
  - Database schema definitions or ORM configs.

### 3. Identify Key Files

Identify and read using `view_file`:
- **Main entry points** (e.g., `src/main.ts`, `app/main.py`, `index.js`).
- **Dependency & Build files** (e.g., `package.json`, `pyproject.toml`).
- **Database/Schema configurations** (e.g., `schema.ts`, `models.py`).

### 4. Understand Git & Work State

Use `run_command` to run:
- `git status` (to see uncommitted changes or current branch).
- `git log -n 10 --oneline` (to understand recent commits and progress).

## Output Report

Provide a concise, easy-to-scan summary covering:

### Project Overview
- Purpose and type of application.
- Primary technologies and frameworks.
- Current version or overall development state.

### Architecture & Folder Structure
- High-level directory organization (list key folders and their purposes).
- Main architectural patterns (MVC, Layered, Event-driven, etc.).

### Tech Stack
- Languages and runtimes.
- Frameworks and major libraries.
- Database, ORM, and migrations.
- Test runner and linting tools.

### Core Patterns & Style Guidelines
- Code style and naming conventions observed.
- Error handling and logging patterns.
- Testing approach.

### Current Git State
- Active branch.
- Uncommitted changes (if any).
- Last few commits.
