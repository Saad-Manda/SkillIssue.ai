# Commit: Package & Record Changes

## Objective

Create a structured, clean, and atomic git commit for all uncommitted changes in our workspace using Conventional Commit standards.

## Process

### 1. Inspect Workspace State

Use `run_command` to inspect the status:
```bash
git status
```
Inspect specific modifications to verify nothing unintended is staged:
```bash
git diff HEAD
```
Get a clean porcelain output to see files clearly:
```bash
git status --porcelain
```

### 2. Stage Changes

Stage the modified and newly created files:
```bash
git add <paths-of-modified-files>
```

### 3. Draft Commit Message

Compose a Conventional Commit message following this standard format:
```text
<type>(<scope>): <short description>

[optional body describing the 'why' and technical decisions]
```

#### Commit Types:
- `feat`: A new user-facing capability or API endpoint.
- `fix`: A bug fix in logic, UI, or database queries.
- `docs`: Documentation edits in Markdown, comments, or docstrings.
- `style`: Changes that do not affect code logic (formatting, semi-colons, white-space).
- `refactor`: Code restructuring without changing functional behavior.
- `test`: Adding missing tests or refactoring existing tests.
- `chore`: Updating build scripts, dependencies, or repository configurations.

### 4. Execute Commit

Run the commit command with the finalized message:
```bash
git commit -m "<message>"
```

### 5. Final Report

Provide a brief summary of:
- Stage success status.
- Files committed.
- Commit hash and message.
- Current active branch.
