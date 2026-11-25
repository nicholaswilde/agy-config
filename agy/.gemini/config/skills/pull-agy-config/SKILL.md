---
name: pull-agy-config
description: >-
  Pull remote updates into local agy-config, resolve merge/rebase conflicts, re-apply enstow symlinks, and verify health.
  Trigger: /pull-agy-config, "pull agy config", "pull agy-config", "update agy config", "sync agy config from remote".
---

# Pull and Sync AGY Config Skill

Pull latest remote updates into `~/git/nicholaswilde/agy-config`, safely handle uncommitted local edits, resolve merge or rebase conflicts, re-apply `enstow` symlinks into `~/.gemini/`, and verify repository health.

## Options

- `--prefer-remote`: Prioritize remote incoming changes on dirty tracked files or conflicts (backs up local edits to stash first).
- `--prefer-local`: Prioritize local changes when resolving conflicts.
- `--rebase`: Rebase local commits onto remote instead of merging.

## Protocol

### 1. Resolve Repo & Tracking Branch

1. Navigate to `~/git/nicholaswilde/agy-config` (or current repo if already inside `agy-config`).

2. Verify active branch:

   ```bash
   BRANCH=$(git branch --show-current)
   ```

   If detached HEAD, stop and ask user which branch to check out.

3. Verify upstream tracking (`git rev-parse --abbrev-ref @{u} 2>/dev/null || true`); set `origin/$BRANCH` if unset.

### 2. Check Remote Connectivity

1. Test connectivity: `timeout 5 git fetch --dry-run origin`.
2. If port 22 times out, test port 443 (`ssh -T -p 443 -o ConnectTimeout=5 git@ssh.github.com 2>&1`) and fall back via `git config core.sshCommand "ssh -p 443 -o Hostname=ssh.github.com"`.

### 3. Audit Working Tree & Protect Local Edits

1. Inspect state: `rtk git status --short`.
2. Never stage or commit secrets (`.env`, private keys, plaintext tokens).
3. If tracked files are dirty:
   - Default: `git stash push -m "autostash-before-pull-$(date +%s)"` (mark for Step 6 restore).
   - `--prefer-remote`: `git stash push -m "pull-backup-$(date +%s)"` (keep as backup; do not pop).
4. If an untracked file collides with an incoming tracked path, move it aside (`mv <file> <file>.bak`).

### 4. Fetch & Pull Remote Changes

1. Fetch remote: `git fetch origin "$BRANCH"`.
2. Check incoming commits: `git log --oneline "HEAD..origin/$BRANCH"`.
   - If 0 commits behind, skip to Step 7 to verify `enstow` sync.
3. Pull based on divergence and flags:
   - 0 commits ahead: `git pull --ff-only origin "$BRANCH"`
   - Ahead + `--prefer-remote`: `git reset --hard "origin/$BRANCH"`
   - Ahead + `--rebase`: `git pull --rebase origin "$BRANCH"`
   - Ahead (default): `git merge "origin/$BRANCH" -m "Merge branch 'origin/$BRANCH' into $BRANCH"`

### 5. Resolve Merge or Rebase Conflicts

If conflicts occur:

1. List conflicted files: `git diff --name-only --diff-filter=U`.
2. Resolve per strategy:
   - `--prefer-remote`: `git checkout --theirs <files> && git add <files>`
   - `--prefer-local`: `git checkout --ours <files> && git add <files>`
   - Default (manual synthesis): inspect `<<<<<<<` / `=======` / `>>>>>>>` markers, merge both sides cleanly, remove all conflict markers, and stage explicitly (`git add <files>`).
     - Keep `rules/*.md`, `AGENTS.md`, and `GEMINI.md` caveman-compressed.
     - Keep `SKILL.md` YAML frontmatter under 380 chars.
3. Finalize:
   - Merge: `git commit --no-edit`
   - Rebase: `git rebase --continue`

### 6. Restore Stashed Local Edits

If stashed in Step 3 and `--prefer-remote` was not set:

1. Run `git stash pop`.
2. If pop conflicts, resolve markers cleanly preserving local edits on top of updated remote files.

### 7. Sync `enstow` Symlinks & Verify Quality Gates

Run inside `~/git/nicholaswilde/agy-config`:

1. Apply symlinks (auto-prunes removed skills/rules via `prune = true` in `.enstow.toml`):

   ```bash
   task apply
   ```

2. Verify symlink state and repo health:

   ```bash
   task status -- --check && task doctor
   ```

3. Run lint and token-hygiene checks (especially after conflict resolution):

   ```bash
   task lint:md && task lint:tokens
   ```

4. Reset uncommitted-change alert if working tree is clean:

   ```bash
   task notify:check || true
   ```

### 8. Terse Caveman Status Report

Report concisely:

- Branch and incoming commits applied (`<old_sha>..<new_sha>`)
- Conflicts resolved and stash status
- `task apply`, `task status -- --check`, `task doctor`, and lint results
