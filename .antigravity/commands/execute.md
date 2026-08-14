---
description: Execute a planned feature or refactor from an implementation plan artifact
argument-hint: [path-to-plan]
---

# Execute: Implement Planned Tasks

## Overview

Execute the implementation plan written in the plan artifact `$ARGUMENTS` using Antigravity's precise code-manipulation tools. Follow the step-by-step instructions strictly in linear order.

---

## Execution Workflow

### 1. Read & Load the Plan
- **Read the Plan**: Use `view_file` with the `IsSkillFile` parameter set to `true`. This tells Antigravity to treat the plan file as high-importance instructions for the current session.
- **Analyze Tasks**: Understand all task dependencies, key files, and specific gotchas mentioned in the plan.

### 2. Implement Tasks in Order
For each task listed in the plan, perform the following steps:

#### a. Navigate & Verify Current Code
- Before changing any file, read its current contents using `view_file` to understand surrounding context and verify line numbers.

#### b. Write the Code
Use the narrowest, most specific tool for editing:
- **`write_to_file`**: Use this ONLY when creating a new file from scratch.
- **`replace_file_content`**: Use this when making a **single, contiguous block of edits** in an existing file. This is highly cost-effective and precise.
- **`multi_replace_file_content`**: Use this ONLY when making **multiple, non-contiguous edits** across different lines of the same file. Specify separate replacement chunks with exact start and end line ranges.
- **Avoid Whole-File Replacements**: Never replace the entire contents of a file to make minor edits. Always use exact chunk-based replacement tools.

#### c. Run the Validation Command
- Immediately after finishing the edits for a task, run the task's specified `VALIDATION` command using `run_command`.
- If the command fails:
  - Carefully inspect the error output or lint error IDs.
  - Fix the code and re-run the validation command.
  - Do NOT proceed to the next task until the current task's validation command passes with zero errors.

### 3. Implement Tests & Verification
- Once all source files are completed, write the test files specified in the plan's Testing Strategy using `write_to_file`.
- Write robust unit and integration tests covering positive paths, error conditions, and edge cases.

### 4. Global Validation Suite
Execute the global validations listed in the plan using `run_command` in the terminal:
```bash
# Syntax/Types check
# Lint checks
# Complete test suite execution
```
If any server or long-running test is executed, manage it using `manage_task`.

---

## Completion Report

When all tasks and validations have successfully passed, output a clear, professional summary:

### 1. Completed Tasks
- Table of tasks completed, matching their identifiers (e.g. Task 1.1, Task 1.2).
- List of new files created.
- List of existing files modified.

### 2. Testing Results
- Number of new test cases created.
- Command used to run tests.
- Status of test execution (e.g. `All 15 tests passed`).

### 3. Validation Results
- Confirm all typechecks, linters, and format checks passed.
- Output snippets or logs from the success states.

### 4. Git Alignment
- Confirm workspace is clean and ready for committing changes.
- Suggest next steps (e.g. calling `/commit`).
