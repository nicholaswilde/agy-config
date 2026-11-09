---
name: update-pr-branch
description: >-
  Merge main into a PR branch to update it, resolve merge conflicts and post-merge build/test issues, and push. Never merges PR into main.
  Trigger: /update-pr-branch, /update-pr, "update pr branch", "update pr", "merge main into pr", "sync pr branch", "sync pr with main".
---

# Update PR Branch Skill

Fetch upstream `main` (or default base branch), merge it into an active pull request branch to bring it up to date, resolve merge conflicts and post-merge breakages, and push the updated branch.

## Safety Invariant

> [!CAUTION]
> **STRICT PROHIBITION: SHALL NOT MERGE PR INTO MAIN**
>
> - Merge direction is strictly one-way: `main` -> `<pr_branch>`.
> - Never checkout `main` and run `git merge <pr_branch>`.
> - Never execute `gh pr merge`.
> - If active branch is `main` or `master`, abort immediately unless switching to target PR branch.
> - The target of all commits and pushes is exclusively the PR branch.

## Inputs

- `[pr_target]` (Optional): PR number (e.g. `12`) or feature branch name (e.g. `feat/wifi-retry`).
  - If omitted: targets active branch if not `main`/`master`.
- `[repo_path]` (Optional): Local repository path. Defaults to current directory (`pwd`).

## Tool Hygiene

- Pipe all GitHub CLI commands to `cat`: `rtk gh <command> | cat`.
- Prefix shell commands with `rtk` where subcommands exist (`rtk git status`, `rtk git diff`).
- Preserve working context: keep raw diffs and logs bounded; parse errors directly.

## Protocol

### 1. Resolve Target Repository and Branches

1. Resolve repository root:

   ```bash
   git rev-parse --show-toplevel
   ```

2. Detect base branch name:

   ```bash
   BASE_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
   ```

3. Determine PR branch:
   - If numeric PR passed: `gh pr checkout <pr_target> | cat`
   - If branch name passed: `git checkout <pr_target>`
   - If no argument passed: inspect current branch via `git branch --show-current`.
     - If current branch equals `$BASE_BRANCH` (or `main`/`master`): query open PRs via `rtk gh pr list | cat` and checkout target PR. If none specified, abort.

4. **Hard Guard**: Verify active branch is NOT the base branch:

   ```bash
   CURRENT=$(git branch --show-current)
   test "$CURRENT" != "$BASE_BRANCH" && test "$CURRENT" != "main" && test "$CURRENT" != "master"
   ```

### 2. Pre-Merge Sync & Working Tree Check

1. Verify clean working tree:

   ```bash
   git status --porcelain=v1
   ```

   If uncommitted changes exist, stash them before proceeding (`git stash push -m "pre-merge-stash"`).

2. Fetch latest remote base branch:

   ```bash
   git fetch origin "$BASE_BRANCH"
   ```

### 3. Execute Merge into PR Branch

Run helper script or execute git merge directly:

```bash
~/.gemini/config/skills/update-pr-branch/scripts/update-pr-branch.sh --base "$BASE_BRANCH"
```

Or direct command on PR branch:

```bash
git merge "origin/$BASE_BRANCH" --no-edit
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
   - `HEAD`: PR branch implementation.
   - `origin/<base_branch>`: Incoming changes from base branch.
3. Synthesize resolution:
   - Retain PR branch functional intent while adopting updated signatures, dependencies, and formatting from base branch.
   - Remove conflict markers completely.
   - Stage resolved files: `git add <resolved_file>`.
4. Finalize merge commit:

   ```bash
   git commit --no-edit || git commit -m "chore: merge origin/$BASE_BRANCH into $(git branch --show-current)"
   ```

### 5. Resolve Post-Merge Build, Lint, and Test Issues

Merge may complete cleanly while introducing semantic breaks, compiler errors, or test regressions.

1. Detect project tooling and run verification suite:
   - **Taskfile**: `task check`, `task lint`, or `task test`
   - **Rust / Cargo**: `cargo check`, `cargo test`, `cargo clippy`
   - **PlatformIO**: `pio test -e native`, `pio run -e <env>`
   - **Python**: `rtk uv run pytest`, `rtk uv run ruff check .`
   - **Node / TypeScript**: `npm test`, `npm run lint`
   - **Go**: `go test ./...`, `golangci-lint run`
2. If failures occur:
   - Diagnose root cause from compiler diagnostics or test failure assertions.
   - Apply surgical fixes directly to affected files.
   - Re-run verification suite until all quality gates pass.
   - Stage fixed files explicitly (enforce `no-secrets.md`).
   - Commit fixes using Conventional Commits:

     ```bash
     git commit -m "fix: resolve post-merge issues with $BASE_BRANCH"
     ```

### 6. Push Updated PR Branch

1. **Safety Verification**:
   Verify current branch is still PR branch and NOT base branch:

   ```bash
   CURRENT=$(git branch --show-current)
   if [ "$CURRENT" = "$BASE_BRANCH" ] || [ "$CURRENT" = "main" ] || [ "$CURRENT" = "master" ]; then
     echo "CRITICAL: Current branch is base branch. Aborting push." >&2
     exit 1
   fi
   ```

2. Push updated PR branch to remote upstream:

   ```bash
   git push origin "$CURRENT"
   ```

3. Confirm remote PR status:

   ```bash
   rtk gh pr view "$CURRENT" --json number,title,state,url | cat
   ```

> [!IMPORTANT]
> Do NOT call `gh pr merge`. Leave PR open for review and remote CI.

### 7. Terse Status Report

Emit concise summary:

- Updated branch: `<pr_branch>`
- Base branch merged: `origin/<base_branch>`
- Merge conflicts resolved: `<count>` files (or `None`)
- Quality gates: `Passed (<checks_run>)`
- Remote push status: `pushed to origin/<pr_branch>`
- Safety confirmation: `PR NOT merged into main`
