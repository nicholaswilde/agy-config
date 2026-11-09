---
name: merge-pr
description: >-
  Merge a PR into main (or base branch), resolve merge conflicts and post-merge build/test issues, and push. PR number passed as argument.
  Trigger: /merge-pr, /merge-pr-to-main, "merge pr", "merge pr to main", "merge pr into main", "land pr".
---

# Merge PR Skill

Fetch and merge an open pull request into `main` (or target base branch), resolve merge conflicts and post-merge breakages, verify quality gates, and push the resolved base branch.

## Inputs

- `<pr_number>` (Required): The numeric identifier of the pull request to merge (e.g. `123`).
  - Passed via slash command: `/merge-pr 123` or `/merge-pr-to-main 123`.
  - Or passed to helper script: `merge-pr.sh --pr 123` or `merge-pr.sh 123`.
- `[repo_path]` (Optional): Local repository path. Defaults to current directory (`pwd`).
- `[--squash|--merge]` (Optional): Merge strategy. Defaults to `--no-ff` merge commit.

## Tool Hygiene

- Pipe all GitHub CLI commands to `cat`: `rtk gh <command> | cat`.
- Prefix shell commands with `rtk` where subcommands exist (`rtk git status`, `rtk git diff`).
- Preserve working context: keep raw diffs and logs bounded; parse diagnostics directly.

## Protocol

### 1. Resolve Target Repository, Base Branch, and PR Metadata

1. Resolve repository root:

   ```bash
   git rev-parse --show-toplevel
   ```

2. Retrieve PR metadata via `gh`:

   ```bash
   PR_JSON=$(rtk gh pr view "<pr_number>" --json number,title,headRefName,baseRefName,state | cat)
   ```

   Verify `state == "OPEN"`. Abort if PR is already closed or merged.
   Extract target `BASE_BRANCH` (default `main`) and `HEAD_BRANCH`.

### 2. Pre-Merge Sync & Working Tree Check

1. Verify clean working tree:

   ```bash
   git status --porcelain=v1
   ```

   If uncommitted changes exist, stash them before proceeding (`git stash push -m "pre-merge-stash"`).

2. Fetch remote base branch and PR branch:

   ```bash
   git fetch origin "$BASE_BRANCH"
   git fetch origin "$HEAD_BRANCH"
   ```

### 3. Checkout Base Branch & Execute Merge

1. Checkout and update local base branch:

   ```bash
   git checkout "$BASE_BRANCH"
   git pull --ff-only origin "$BASE_BRANCH"
   ```

2. Run helper script or execute git merge directly:

   ```bash
   ~/.gemini/config/skills/merge-pr/scripts/merge-pr.sh --pr "<pr_number>" --base "$BASE_BRANCH"
   ```

   Or direct merge on base branch:

   ```bash
   git merge "origin/$HEAD_BRANCH" --no-ff -m "Merge pull request #$PR_NUMBER from $HEAD_BRANCH"
   ```

Outcomes:

- **Exit 0 (Clean Merge)**: Advance to Step 5 (Post-Merge Validation).
- **Exit non-zero (Conflicts)**: Advance to Step 4 (Merge Conflict Resolution).

### 4. Resolve Merge Conflicts

1. Identify conflicted paths:

   ```bash
   git diff --name-only --diff-filter=U
   ```

2. Inspect conflict regions (`<<<<<<< HEAD`, `=======`, `>>>>>>>`):
   - `HEAD`: Base branch code.
   - `origin/<head_branch>`: Incoming PR changes.
3. Synthesize resolution:
   - Preserve all PR features and fixes while adapting to base branch state.
   - Remove conflict markers completely.
   - Stage resolved files: `git add <resolved_file>`.
4. Finalize merge commit:

   ```bash
   git commit --no-edit || git commit -m "Merge pull request #$PR_NUMBER from $HEAD_BRANCH"
   ```

### 5. Resolve Post-Merge Build, Lint, and Test Issues

Merge may complete without conflict while breaking builds, types, or tests.

1. Detect project tooling and run verification suite:
   - **Taskfile**: `task check`, `task lint`, or `task test`
   - **Rust / Cargo**: `cargo check`, `cargo test`, `cargo clippy`
   - **PlatformIO**: `pio test -e native`, `pio run -e <env>`
   - **Python**: `rtk uv run pytest`, `rtk uv run ruff check .`
   - **Node / TypeScript**: `npm test`, `npm run lint`
   - **Go**: `go test ./...`, `golangci-lint run`
2. If failures occur:
   - Diagnose root cause from error diagnostics or test failure assertions.
   - Apply surgical fixes directly to affected files.
   - Re-run verification suite until all quality gates pass.
   - Stage fixed files explicitly (enforce `no-secrets.md`).
   - Commit fixes:

     ```bash
     git commit -m "fix: resolve post-merge issues for PR #$PR_NUMBER"
     ```

### 6. Push Base Branch & Sync PR

1. Verify current branch is base branch:

   ```bash
   CURRENT=$(git branch --show-current)
   test "$CURRENT" = "$BASE_BRANCH"
   ```

2. Push merged base branch to remote upstream:

   ```bash
   git push origin "$BASE_BRANCH"
   ```

3. Confirm remote PR status:

   ```bash
   rtk gh pr view "<pr_number>" --json number,title,state,url | cat
   ```

   GitHub marks PR merged automatically when the merge commit lands in the base branch. If still open (e.g. after squash), close explicitly:

   ```bash
   rtk gh pr close "<pr_number>" --comment "Merged into $BASE_BRANCH" | cat
   ```

4. Optional cleanup: delete local feature branch if present:

   ```bash
   git branch -d "$HEAD_BRANCH" 2>/dev/null || true
   ```

### 7. Terse Status Report

Emit concise summary:

- Merged PR: `#<pr_number>` (`<title>`)
- Target branch: `<base_branch>`
- Merge conflicts resolved: `<count>` files (or `None`)
- Quality gates: `Passed (<checks_run>)`
- Remote push status: `pushed to origin/<base_branch>`
- PR state: `Merged`
