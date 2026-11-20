---
name: pull-and-fix
description: >-
  Pull remote changes, handle dirty trees, resolve merge/rebase conflicts, fix SSH/network timeouts, and verify quality gates.
  Trigger: /pull-and-fix, /git-pull, /pull, "git pull", "git pull and fix", "pull and fix", "pull and fix issues", "pull <repo>".
---

# Pull and Fix Skill

Fetch and pull latest remote changes into the current branch, safely manage uncommitted changes, diagnose and resolve SSH/network connectivity issues, resolve merge or rebase conflicts, run post-pull verification tests, and report concise status.

## Inputs & Options

- `[repo_path_or_name]` (Optional): Target repository path or directory name under `~/git/nicholaswilde/`. Defaults to current working directory (`pwd`).
- `--prefer-remote` (Optional): When dirty tracked files or merge conflicts occur, prioritize remote incoming versions over local changes.
- `--prefer-local` (Optional): When merge conflicts occur, prioritize local versions.
- `--rebase` / `--ff-only` (Optional): Rebase local commits onto remote or force fast-forward only. Default: fast-forward when possible, otherwise clean merge.

## Tool Hygiene

- Prefix git inspection commands with `rtk` where applicable (`rtk git status`, `rtk git diff`, `rtk git log`).
- Pipe GitHub CLI commands to `cat`: `rtk gh <command> | cat`.
- Preserve secrets: never commit or stage unencrypted credentials, tokens, or private keys (`no-secrets.md`).

## Protocol

### 1. Resolve Target Repository & Tracking Branch

1. Resolve repository root:

   ```bash
   git rev-parse --show-toplevel
   ```

   If `<repo_path_or_name>` argument is provided, resolve absolute path or check `~/git/nicholaswilde/<arg>`.

2. Inspect current branch:

   ```bash
   BRANCH=$(git branch --show-current)
   ```

   If branch name is empty (detached HEAD), abort and prompt to checkout a branch first.

3. Verify upstream tracking branch:

   ```bash
   git rev-parse --abbrev-ref @{u} 2>/dev/null || true
   ```

   If upstream is not configured, check remote branch existence (`git ls-remote --heads origin "$BRANCH"`) and configure tracking:

   ```bash
   git branch --set-upstream-to="origin/$BRANCH" "$BRANCH"
   ```

### 2. Diagnose & Resolve Remote Connectivity

Check connection before pulling to avoid hangs on restricted networks:

1. Test connection with 5-second timeout:

   ```bash
   timeout 5 git fetch --dry-run origin
   ```

2. **Handle Port 22 SSH Timeout**:
   If fetch hangs or fails with `Connection timed out during banner exchange`:
   - Test GitHub SSH port 443 availability:

     ```bash
     ssh -T -p 443 -o ConnectTimeout=5 git@ssh.github.com 2>&1
     ```

   - If port 443 succeeds, ensure SSH routes over port 443:
     - Preferred system drop-in: `/etc/ssh/ssh_config.d/github.conf`:

       ```ssh
       Host github.com
         Hostname ssh.github.com
         Port 443
         User git
       ```

     - Repository-level fallback:

       ```bash
       git config core.sshCommand "ssh -p 443 -o Hostname=ssh.github.com"
       ```

   - Re-test fetch: `git fetch origin "$BRANCH"`.

### 3. Audit Working Tree & Handle Local Edits

Inspect repository state for uncommitted changes:

```bash
git status --porcelain=v1
```

1. **Clean Working Tree**: Advance to Step 4.
2. **Dirty Working Tree (Tracked Changes)**:
   - **User prefers remote (`--prefer-remote`)**:
     Create safe backup stash without blocking pull:

     ```bash
     git stash push -m "pull-backup-$(date +%s)"
     ```

   - **Preserving local edits (Default)**:
     Stash uncommitted changes:

     ```bash
     git stash push -m "autostash-before-pull-$(date +%s)"
     ```

     Record that stash was created for Step 6 restoration.
3. **Untracked File Conflicts**:
   If incoming commits track a path that currently exists untracked locally:
   - Move or rename untracked conflicting file (e.g. `mv <file> <file>.bak`).

### 4. Fetch & Pull Remote Changes

1. Fetch target remote branch:

   ```bash
   git fetch origin "$BRANCH"
   ```

2. Inspect incoming commits:

   ```bash
   git log --oneline "HEAD..origin/$BRANCH"
   ```

   - If behind count is 0: branch is already up to date. Advance to Step 6.

3. Execute pull or helper script:

   ```bash
   ~/.gemini/config/skills/pull-and-fix/scripts/pull-and-fix.sh --repo "." "$@"
   ```

   Or execute native git pull:
   - If 0 local commits ahead:

     ```bash
     git pull --ff-only origin "$BRANCH"
     ```

   - If local commits exist and `--prefer-remote`:

     ```bash
     git reset --hard "origin/$BRANCH"
     ```

   - If local commits exist and `--rebase`:

     ```bash
     git pull --rebase origin "$BRANCH"
     ```

   - If local commits exist (merge strategy):

     ```bash
     git merge "origin/$BRANCH" -m "Merge branch 'origin/$BRANCH' into $BRANCH"
     ```

### 5. Resolve Merge & Rebase Conflicts

If merge or rebase encounters conflicts:

1. Identify conflicted files:

   ```bash
   git diff --name-only --diff-filter=U
   ```

2. Resolution strategy:
   - **`--prefer-remote`**:

     ```bash
     git checkout --theirs <conflicted_files>
     git add <conflicted_files>
     ```

   - **`--prefer-local`**:

     ```bash
     git checkout --ours <conflicted_files>
     git add <conflicted_files>
     ```

   - **Manual synthesis**:
     Inspect markers (`<<<<<<< HEAD`, `=======`, `>>>>>>>`), merge both changes logically, remove all conflict markers, and validate syntax.
     Stage resolved files: `git add <resolved_files>`.

3. Finalize merge or rebase:
   - For merge: `git commit --no-edit`
   - For rebase: `git rebase --continue`

### 6. Restore Stashed Changes (if applicable)

If local changes were stashed in Step 3 and `--prefer-remote` was not specified:

1. Restore stash:

   ```bash
   git stash pop
   ```

2. If pop encounters conflicts:
   - Identify unmerged files: `git diff --name-only --diff-filter=U`
   - Synthesize conflicts, preserving local edits on top of updated remote base.
   - Stage resolved files: `git add <file>`.

### 7. Sync Submodules & Dependencies

Check if incoming commits modified submodules or dependency manifests:

1. **Submodules**:

   ```bash
   if [ -f .gitmodules ]; then git submodule update --init --recursive; fi
   ```

2. **Package Locks & Tools**:
   - `Taskfile.yaml`: check if stowed packages or tasks changed (`task restow` or `task install`).
   - Python (`uv.lock` / `pyproject.toml`): run `rtk uv sync`.
   - Node (`package-lock.json` / `pnpm-lock.yaml`): run `npm install` or `pnpm install`.
   - Rust (`Cargo.lock`): run `cargo check`.

### 8. Post-Pull Validation & Quality Gates

Run repository-appropriate verification suites:

- **Dotfiles**: `bash tests/verify.sh && bash tests/test_skills_catalog_links.sh`
- **Taskfile repos**: `task test` or `task check` or `task lint`
- **Python repos**: `rtk uv run pytest`
- **Rust repos**: `cargo test`
- **Go repos**: `go test ./...`
- **Node repos**: `npm test`

If validation fails:

- Diagnose failure diagnostics.

- Apply surgical patch to fix regression.

- Stage explicitly and commit fix:

  ```bash
  git commit -m "fix: resolve post-pull regressions in <component>"
  ```

### 9. Terse Status Report

Emit concise confirmation:

- Repo & Branch: `<repo>@<branch>`
- Incoming Commits: `<count>` commits applied (`<old_sha>..<new_sha>`)
- Working Tree: `Clean` (or `Local changes preserved`)
- Issues Resolved: `None` (or list e.g., `SSH port 443 fallback`, `stashed edits restored`, `conflicts resolved in <files>`)
- Quality Gates: `Passed (<checks_run>)`
