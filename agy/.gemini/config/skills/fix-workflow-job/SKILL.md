---
name: fix-workflow-job
description: >-
  Investigate, debug, and fix a failed remote GitHub Actions workflow job given its job ID.
  Queries job details, extracts failing step logs via GitHub CLI, isolates root causes,
  reproduces failures locally, applies surgical fixes, runs quality gates, and pushes fixes.
  Trigger: /fix-workflow-job, /fix-job, "fix workflow job <job_id>", "fix job <job_id>", "debug job <job_id>".
---

# Fix Workflow Job Skill

Investigate, diagnose, and resolve remote GitHub Actions workflow job failures given a specific job ID.

## Overview

When a continuous integration (CI) or deployment workflow job fails, this skill extracts failed step logs, identifies the failure category (compilation, unit test, lint/formatting, matrix/concurrency race, or environment issue), replicates the issue locally where feasible, applies a minimal surgical fix, verifies via tests, and pushes the resolution.

## Input

- **`<job_id>`** (Required): The numeric identifier of the failing GitHub Actions job (e.g. `123881774649`).
  - Passed as an argument after the slash command: `/fix-workflow-job <job_id>` or `/fix-job <job_id>`.
  - Or provided naturally in the prompt: `"fix workflow job 123881774649"`.

## Mandatory Rules & Tool Hygiene

- **Pipe `gh` to `cat`:** Always append `| cat` to all `gh` commands (e.g., `gh run view --job <job_id> --log-failed | cat`) to bypass interactive terminal pagers and prompts.
- **Context Preservation:** Avoid dumping unbounded raw logs into context. When logs exceed ~200 lines, process them with sandboxed context tools (`ctx_execute` or `ctx_execute_file`) to extract only the panic messages, failed assertions, or compile diagnostics into context.
- **Surgical Changes:** Fix the root cause only. Do not refactor adjacent code or add speculative abstractions (Ponytail discipline).

## Protocol

### 1. Inspect Job Metadata & Environment

Query the job to determine its runner platform, target matrix values, and failed steps:

```bash
gh run view --job <job_id> | cat
```

Note:

- Runner OS: Linux, macOS, or Windows.
- Toolchain / runtime versions: Rust stable/beta/nightly, Go version, Node version, Python version.
- Cross-compilation target: e.g. `aarch64-unknown-linux-musl`, `armv7`, `x86_64-pc-windows-msvc`.
- Exact failed step name (e.g., `Run tests`, `Check clippy`, `Build`).

### 2. Extract Failed Step Logs

Retrieve failed log output:

```bash
gh run view --job <job_id> --log-failed | cat
```

If logs are truncated or large:

- Filter for error keywords: `FAILED`, `panicked at`, `error[E`, `failures:`, `assertion failed`.
- Identify the exact file path and line number where the failure occurred.

### 3. Root Cause Diagnosis & Local Reproduction

Categorize the issue and reproduce locally:

- **Unit / Integration Test Failure:**
  - Run the specific test locally: e.g. `cargo test <test_name>` or `npm test -- -t "<pattern>"`.
  - If it passes locally but failed on remote:
    - Check matrix differences: Is it specific to Windows (path separators, line endings, credential store) or macOS?
    - Check concurrency / environment race: Were multiple tests mutating process-wide global environment variables concurrently?
- **Linter / Formatting Failure:**
  - Run the repo's formatting/lint commands (`task fmt:check`, `cargo clippy -- -D warnings`, `npm run lint`).
- **Build / Cross-Compilation Failure:**
  - Check missing system dependencies, platform headers, or cross-compilation target definitions (`cross`, Docker).

### 4. Implement Surgical Fix

- Formulate the minimal change that directly fixes the root cause.
- Follow Test-Driven Development (TDD): ensure a reproduction test exists or write a test verifying the fix before wrapping up.
- Preserve all existing comments and unrelated formatting.

### 5. Validate Quality Gates

Run project verification commands before committing:

- Formatting checks (e.g., `task fmt:check` or `cargo fmt -- --check`).
- Linter checks (e.g., `task lint` or `cargo clippy --workspace --all-targets --all-features -- -D warnings`).
- Local test execution (e.g., `task test` or `cargo test`).

### 6. Commit and Push

Stage modified files explicitly and commit using Conventional Commits:

```bash
git add <file1> <file2>
git commit -m "fix(<scope>): <concise description of the fix>"
git push origin <branch>
```

Provide a terse summary to the user outlining:

- Failed Job ID and runner/matrix target.
- Root cause identified.
- Changes made.
- Commit SHA and push status.
