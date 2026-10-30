---
name: fix-workflow-run
description: >-
  Investigate, debug, and fix a failed remote GitHub Actions workflow run given its run ID.
  Queries run status, lists failed jobs, extracts failing step logs via GitHub CLI, isolates root causes,
  reproduces failures locally, applies surgical fixes, runs quality gates, and pushes fixes.
  Trigger: /fix-workflow-run, /fix-run, "fix workflow run <run_id>", "fix run <run_id>", "look at run <run_id> and fix", "debug run <run_id>".
---

# Fix Workflow Run Skill

Investigate, diagnose, and resolve remote GitHub Actions workflow run failures given a specific workflow run ID.

## Overview

When an automated CI/CD workflow run fails, multiple jobs across operating systems and architectures may fail simultaneously or a single matrix job may fail due to platform-specific edge cases. This skill inspects the overall workflow run, identifies all failing jobs, extracts logs, diagnoses root causes, applies a surgical fix, validates locally, and pushes the resolution.

## Input

- **`<run_id>`** (Required): The numeric identifier of the GitHub Actions workflow run (e.g. `40999951727`).
  - Passed as an argument after the slash command: `/fix-workflow-run <run_id>` or `/fix-run <run_id>`.
  - Or provided naturally in the prompt: `"look at run 40999951727 and fix any issues"`.

## Mandatory Rules & Tool Hygiene

- **Pipe `gh` to `cat`:** Always append `| cat` to all `gh` commands (e.g., `gh run view <run_id> | cat`, `gh run view <run_id> --log-failed | cat`) to bypass interactive terminal pagers and prompts.
- **Context Preservation:** Avoid dumping raw, multi-megabyte log files into context. When run logs contain many jobs or thousands of lines, process them with sandboxed context tools (`ctx_execute` or `ctx_execute_file`) to filter for failing assertions, panic locations, and build errors.
- **Surgical Changes:** Fix the root cause only. Do not refactor adjacent code or add speculative abstractions (Ponytail discipline).

## Protocol

### 1. Inspect Workflow Run Overview

Query the run to view the workflow name, trigger event, and pass/fail status of all constituent jobs:

```bash
gh run view <run_id> | cat
```

Analyze the output:

- Identify all jobs marked with `X` (failed).
- Record the failed job IDs (e.g., `ID 123881774649`).
- Compare failed jobs against passing jobs: Did only `win-msvc` fail while `ubuntu` and `macos` passed? Did all targets fail at the same lint or test step?

### 2. Extract Failed Step Logs

Retrieve failed step logs across all failing jobs in the run:

```bash
gh run view <run_id> --log-failed | cat
```

If multiple jobs failed or the output is large, drill down into specific failed jobs using their job ID:

```bash
gh run view --job <job_id> --log-failed | cat
```

Filter for critical failure signals:

- `failures:` and test names.
- `thread '...' panicked at <file>:<line>`.
- `error[E...]:` or compilation errors.
- Linter warnings treated as errors (`-D warnings`).

### 3. Root Cause Diagnosis & Local Reproduction

1. **Classify Failure Type:**
   - **Environment / Platform-Specific:** Fails on Windows or macOS only (path delimiters, line endings, credential managers, thread scheduling).
   - **Parallel / Race Condition:** Tests pass in isolation but fail when executed concurrently across cores (e.g. concurrent mutation of process-wide environment variables).
   - **General Regression:** A code or configuration edit broke compilation or test assertions everywhere.
2. **Reproduce Locally:**
   - Run the failing target test or build step locally (e.g. `cargo test <test_name>`, `task lint`).
   - If race condition is suspected, simulate environmental contention locally (e.g., setting the environment variables concurrently or running tests with `--test-threads`).

### 4. Implement Surgical Fix

- Implement the minimum code changes necessary to resolve the root cause.
- Follow Test-Driven Development (TDD): ensure the fix resolves the test failure and leaves no regressions.
- Preserve existing style, comments, and project conventions.

### 5. Validate Quality Gates

Run the project's quality verification suite locally:

- Formatting checks (e.g., `task fmt:check` or `cargo fmt -- --check`).
- Linter checks (e.g., `task lint` or `cargo clippy -- -D warnings`).
- Test suite (e.g., `task test` or `cargo test`).

### 6. Commit and Push

Stage modified files explicitly and commit using Conventional Commits:

```bash
git add <file1> <file2>
git commit -m "fix(<scope>): <concise description of the fix>"
git push origin <branch>
```

Provide a terse summary to the user outlining:

- Failed Run ID and failing job matrix targets.
- Root cause diagnosed.
- Surgical changes applied.
- Commit SHA and push status.
