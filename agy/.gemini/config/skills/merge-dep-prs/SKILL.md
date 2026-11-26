---
name: merge-dep-prs
description: >-
  Find, audit, merge, validate, and push all open dependency PRs (Dependabot, Renovate, etc.) into the base branch, resolving lockfile conflicts and verifying checks.
  Trigger: /merge-dep-prs, /merge-deps, "merge dep prs", "merge dependency prs", "merge dependabot prs", "merge renovate prs".
---

# Merge Dependency PRs Skill

Discover all open dependency pull requests (Dependabot, Renovate, and similar bots), audit checks and breaking changes, merge them cleanly into the base branch, resolve manifest/lockfile conflicts, verify build/lint/test gates, and push.

## Inputs & Options

- `[repo_path]` (Optional): Target repository path. Defaults to current directory (`pwd`).
- `--dry-run` (Optional): List matching dependency PRs, check statuses, and planned merge order without modifying git or remote.
- `--skip-major` (Optional): Skip major-version dependency bumps (`0.x -> 1.0`, `N.x -> (N+1).x`).
- `--include-failing` (Optional): Attempt to merge and fix PRs with failing CI checks instead of skipping them.
- `--strategy <merge|squash|gh>` (Optional): Defaults to local `--no-ff` merge commits + single push; falls back to `gh pr merge` when branch protection blocks direct pushes.

## Tool Hygiene

- Pipe all GitHub CLI commands to `cat`: `rtk gh <command> | cat`.
- Prefix shell commands with `rtk` where subcommands exist (`rtk git status`, `rtk rg`, `rtk uv`).
- Inside `context-mode` sandbox (`ctx_execute`), skip `rtk` and print derived summaries only.

## Protocol

### 1. Discover & Classify Open PRs

1. Resolve repository root and base branch:

   ```bash
   git rev-parse --show-toplevel
   BASE_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
   ```

2. Fetch open PR metadata:

   ```bash
   rtk proxy gh pr list --state open \
     --json number,title,headRefName,baseRefName,author,labels,isDraft,mergeable,mergeStateStatus,statusCheckRollup,files,url | cat
   ```

3. Match dependency PRs when ANY criterion holds:
   - **Author**: `dependabot[bot]`, `app/dependabot`, `renovate[bot]`, `app/renovate`, `mend-for-github-com[bot]`, `pyup-bot`, `snyk-bot`.
   - **Branch prefix**: `dependabot/`, `renovate/`, `deps/`, `chore/deps`.
   - **Labels + title**: labels containing `dependencies`, `dependabot`, or `renovate`, OR titles matching `^(chore|build|fix)\(deps(-dev)?\):`, `^deps:`, `bump .+ from .+ to `, `Update dependency `.

4. Exclude and record as `Skipped`:
   - Non-dependency PRs (human feature/bugfix PRs).
   - Draft PRs (`isDraft == true`) or PRs labeled `do-not-merge`, `hold`, or `wip`.
   - PRs with failing checks (`FAILURE`, `TIMED_OUT`, `ACTION_REQUIRED`, `CANCELLED`) unless `--include-failing` is set.
   - Major-version bumps when `--skip-major` is set.

5. If zero eligible dependency PRs remain, stop and report `No eligible open dependency PRs`. If `--dry-run`, emit the audit table and stop.

### 2. Inspect Diffs & Breaking Changes

1. For each eligible PR, inspect diff (`gh pr diff <num> | cat`) and release notes in the PR body.
2. Pay extra attention to:
   - **Major version bumps**: Search codebase usage (`rtk rg`) for affected libraries/actions and verify no breaking API or runner changes (e.g., Node runtime bump on self-hosted runners, removed inputs, changed selector/parser semantics).
   - **Lockfile format/revision bumps**: Verify local and CI tool versions (e.g., `uv`, `cargo`, `npm`, `pnpm`) support the updated lockfile revision.
3. Order merges to minimize churn and conflicts:
   1. CI / GitHub Actions workflow bumps (e.g., `.github/workflows/*`).
   2. Patch and minor dependency bumps.
   3. Major dependency bumps (last, so any failure isolates cleanly).

### 3. Pre-Merge Sync & Branch Protection Check

1. Verify clean working tree:

   ```bash
   git status --porcelain=v1
   ```

   If uncommitted changes exist, stash them (`git stash push -m "pre-merge-deps-stash"`) and restore after Step 6.

2. Fetch remote state and update local base branch:

   ```bash
   git fetch origin --prune
   git checkout "$BASE_BRANCH"
   git pull --ff-only origin "$BASE_BRANCH"
   ```

3. Check branch protection on `$BASE_BRANCH`:

   ```bash
   gh api "repos/{owner}/{repo}/branches/$BASE_BRANCH/protection" 2>/dev/null | cat || true
   ```

   - **Unprotected (HTTP 404 / no push block)**: Use local batch merge (Step 4A) — resolves multi-PR lockfile conflicts cleanly and validates everything together before a single push.
   - **Protected (direct push blocked or required reviews/status checks)**: Use remote sequential merge (Step 4B).

### 4. Execute Merges & Resolve Lockfile Conflicts

#### 4A. Local Batch Merge (Default)

For each PR in merge order:

1. Save rollback checkpoint:

   ```bash
   PRE_SHA=$(git rev-parse HEAD)
   ```

2. Merge using the `merge-pr` helper script (or `git merge --no-ff` directly):

   ```bash
   ~/.gemini/config/skills/merge-pr/scripts/merge-pr.sh --pr "<num>" --base "$BASE_BRANCH"
   ```

3. If conflicts occur (`git diff --name-only --diff-filter=U`):
   - **Manifest files** (`pyproject.toml`, `Cargo.toml`, `package.json`, `go.mod`, workflow YAML): merge both dependency updates cleanly, remove conflict markers, and stage explicitly.

   - **Lockfiles** (`uv.lock`, `Cargo.lock`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `go.sum`, `Gemfile.lock`): resolve manifest conflicts first, then regenerate lockfile natively rather than hand-editing hashes:
     - Python (`uv`): `rtk uv lock`
     - Rust (`cargo`): `cargo generate-lockfile` (or `cargo update -p <crate>`)
     - Node: `npm install --package-lock-only` / `pnpm install --lockfile-only` / `bun install`
     - Go: `go mod tidy`

   - Stage resolved files explicitly (`git add <file>`) — never stage secrets (`no-secrets.md`).

   - Finalize merge commit:

     ```bash
     git commit --no-edit || git commit -m "Merge pull request #<num> from <head_branch>"
     ```

4. Track `(pr_number, PRE_SHA)` pairs so a single broken PR can be isolated if Step 5 fails.

#### 4B. Protected Base Branch Fallback (`gh pr merge`)

When direct pushes to `$BASE_BRANCH` are disallowed:

1. Merge PRs sequentially via GitHub CLI:

   ```bash
   rtk gh pr merge "<num>" --merge --delete-branch | cat
   ```

   (Use `--squash` if repository enforces squash merges.)

2. If a subsequent PR becomes `CONFLICTING` after an earlier lockfile merge, request bot rebase (`gh pr comment <num> --body "@dependabot rebase" | cat` or check Renovate's rebase checkbox) and report it as `Pending rebase`.

3. Sync local `$BASE_BRANCH` after merges (`git pull --ff-only origin "$BASE_BRANCH"`).

### 5. Post-Merge Verification Gates

Run relevant project checks before pushing (for Step 4A):

1. **Lockfile & dependency sync**:
   - Python (`uv`): `rtk uv lock --check && rtk uv sync --frozen`
   - Rust (`cargo`): `rtk err cargo check --locked`
   - Node: `npm ci` / `pnpm install --frozen-lockfile`
   - Go: `go mod verify`
2. **Tests, build & linters** (detect repo tooling):
   - **Taskfile**: `task check`, `task test`, `task lint` (distinguish newly introduced errors from pre-existing issues in untouched files)
   - **Python**: `rtk uv run pytest`, `rtk uv run ruff check .`
   - **Rust**: `rtk test cargo test`, `rtk err cargo clippy`
   - **Node**: `npm test`, `npm run lint`
   - **Go**: `go test ./...`, `golangci-lint run`
   - **Workflows / Docs**: `yamllint-rs` on changed `.github/workflows/*`, `rtk typos --format brief` when spellcheck action bumped, site build (`zensical build` / `mkdocs build`) when applicable.
3. **Failure handling**:
   - If a breaking major bump or bad update fails checks, diagnose root cause.
   - If trivial and safe (e.g., minor config/test update), apply surgical fix and commit (`fix: resolve post-merge issue for PR #<num>`).
   - Otherwise, roll back the offending PR (replay cleanly without it from before its `$PRE_SHA`), re-verify the remaining PRs, and report the offending PR as `Skipped (failed verification: <reason>)`.

### 6. Push Base Branch & Confirm Remote States

1. Verify branch and clean tree:

   ```bash
   test "$(git branch --show-current)" = "$BASE_BRANCH"
   test -z "$(git status --porcelain=v1)"
   ```

2. Push to remote:

   ```bash
   git push origin "$BASE_BRANCH"
   ```

3. Verify all merged PRs transitioned to `MERGED` (re-check once if GitHub lags asynchronously after push):

   ```bash
   for pr in <merged_prs>; do
     rtk gh pr view "$pr" --json number,title,state,url | cat
   done
   ```

4. Prune remote tracking branches (`git fetch origin --prune`), remove any local feature branches (`git branch -d <branch> 2>/dev/null || true`), and restore stashed changes if stashed in Step 3 (`git stash pop`).

### 7. Terse Status Report

Emit concise summary:

- **Merged PRs**: `#<num>` — `<title>` (`MERGED`)
- **Skipped PRs**: `#<num>` — `<reason>` (or `None`)
- **Conflicts resolved**: `<count>` files (or `None`)
- **Quality gates**: `Passed (<checks_run>)`
- **Remote status**: pushed to `origin/<base_branch>`, remaining open PR count, and triggered CI run URL if available
