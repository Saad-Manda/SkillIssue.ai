---
description: Create global project rules (ANTIGRAVITY.md) from codebase analysis
---

# Create Global Rules for Antigravity

Generate an `ANTIGRAVITY.md` file by analyzing the codebase and extracting project patterns.

---

## Objective

Create project-specific global rules that give Antigravity context about:
- What this project is and its purpose.
- The tech stack, build, dev, and test commands.
- The project's directory structure and architecture.
- Specific coding patterns, conventions, and error handling.
- Validation and testing workflows.

---

## Phase 1: DISCOVER

### Identify Project Type

Analyze the codebase using `list_dir` and determine the category:

| Type | Indicators |
|------|------------|
| Web App (Full-stack) | Front-end and back-end directories, API routes |
| Web App (Frontend) | Next.js, Vite, React, Vue, Svelte, static HTML/JS |
| API/Backend | Express, Fastify, FastAPI, Flask, etc. |
| Library/Package | main/exports in package.json, setup.py, pyproject.toml |
| CLI Tool | bin in package.json or CLI entrypoints |
| Monorepo | workspaces configuration, pnpm-workspace.yaml |

### Analyze Configuration Files

Examine configuration files in the root directory:
- `package.json` / `pnpm-lock.yaml` / `bun.lockb` → Node/JS dependencies
- `pyproject.toml` / `requirements.txt` → Python dependencies
- `tsconfig.json` → TypeScript rules
- `vite.config.ts` / `next.config.js` → Frontend compilation settings
- `drizzle.config.ts` / `prisma.schema` → Database ORM mappings

### Map Directory Structure

List the directories to map organization. Identify where components, business logic, models, controllers, routers, and tests live.

---

## Phase 2: ANALYZE PATTERNS

Study existing files in the codebase using `view_file` or `grep_search`:
- **Naming Conventions**: Are files in kebab-case, snake_case, or CamelCase? Do interfaces start with `I`?
- **Error Handling**: Are try-catch blocks used? Are there custom error classes or custom middleware handlers?
- **Logging**: What logger is used (winston, pino, loguru)? What is the standard structure for logs?
- **Testing**: Where are tests stored? Do they mirror the source folder structure? What test framework is used (jest, vitest, pytest)?

---

## Phase 3: GENERATE ANTIGRAVITY.md

Use the template at `.antigravity/ANTIGRAVITY-template.md` as a starting point. Write the final rules file to `ANTIGRAVITY.md` in the root of the project workspace.

### Key Sections for ANTIGRAVITY.md:

1. **Project Overview** - Purpose, MVP goals.
2. **Tech Stack** - Clean, concise GFM table of languages, frameworks, libraries, database, testing, and formatting.
3. **Common Commands** - Code blocks displaying development, build, test, lint, and formatting commands.
4. **Project Structure** - Text-based tree diagram of the folder hierarchy with brief annotations.
5. **Code Patterns & Guidelines** - Naming conventions, error handling, database/ORM usage, logging standards.
6. **Testing & Validation** - Instructions on how to write tests, where they should be saved, and validation commands to run before commits.
7. **Key Files & References** - List of critical files (e.g. database schema, entrypoint, environment template) and their purposes.

---

## Phase 4: OUTPUT REPORT

Provide a summary in the conversation including:
- **File Created**: `ANTIGRAVITY.md` (root directory)
- **Detected Project Type**: Web App / API / Library / etc.
- **Tech Stack Overview**: Key frameworks and databases found.
- **Next Steps**:
  1. Review the generated rules.
  2. Customize any edge-case project configurations.
  3. Add project-specific instructions to refine future iterations.
