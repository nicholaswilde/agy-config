---
name: commit-and-push
description: >-
  Audit, stage, commit with caveman-commit message, and push current repo or target repo argument.
  Trigger: /commit-and-push, /commit-push, /cp, "commit and push", "git commit and push", "commit and push <repo>".
---

# Commit and Push Skill

Stage, commit (using `caveman-commit` compression rules), and push changes in the current workspace repository, or in a target repository when an argument is provided.

## Protocol

### 1. Resolve Target Repository

1. **No argument passed**: Use current workspace working directory (`pwd`).
2. **Repo argument passed** (`<repo_path_or_name>`):
   - If absolute or relative path exists (`<arg>`), use it.
   - If repo name passed (e.g. `agy-config`, `tfa`), resolve under `/home/nicholas/git/nicholaswilde/<arg>` or via `readlink -f` if targeting symlinked dotfiles (`~/.gemini/config`).
   - If `agy-config` is resolved, follow `commit-agy-config` checks (`task lint`, `task restow`, `task notify:check`).
3. Verify git root: `git -C <repo> rev-parse --show-toplevel`.

### 2. Inspect Status & Secret Hygiene

1. Run `git -C <repo> status --short` and `git -C <repo> diff --stat`.
2. If working tree and index are clean, stop and report: `working tree clean; nothing to commit`.
3. **Secret Audit**:
   - Never stage or commit `.env`, `*.pem`, `*.key`, `id_rsa`, `id_ed25519`, `credentials*`, or files containing plaintext secrets/tokens/passwords.
   - Never run blind `git add .` or `git add -A` when untracked files exist; stage explicit file paths (`git -C <repo> add <files...>`). If changes are already staged in the index, respect the staged set unless user asked to commit all modified files.

### 3. Generate Message via `caveman-commit` Rules

Apply `caveman-commit` formatting to the staged diff (`git -C <repo> diff --staged`):

- **Format**: Conventional Commits (`<type>[optional (<scope>)]: <subject>`).
- **Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `style`, `perf`, `ci`, `build`.
- **Subject**:
  - `<= 50` chars total.
  - Imperative mood, lowercase after `: `.
  - No trailing period.
  - Terse caveman compression: drop articles (`a`, `an`, `the`) and filler.
- **Body**:
  - Omit unless "why" is not obvious from subject.
  - Focus on *why* over *what*.
  - Include `Fixes #<id>` if closing a GitHub issue.

### 4. Commit & Push

1. Commit staged changes:

   ```bash
   git -C <repo> commit -m "<caveman_commit_message>"
   ```

2. Push to remote tracking branch:
   - Check upstream: `git -C <repo> rev-parse --abbrev-ref @{u} 2>/dev/null`
   - If upstream exists: `git -C <repo> push`
   - If no upstream: `git -C <repo> push -u origin "$(git -C <repo> branch --show-current)"`

### 5. Post-Push Hook (if `agy-config`)

If target repository is `agy-config`:

- Run `task restow` if new files were added under `agy/`.
- Run `task notify:check` to reset dirty notification state.

### 6. Terse Report

Output 1-3 lines:

- Repo + branch (`<repo>@<branch>`)
- Commit SHA + `caveman-commit` message
- Files changed + push status
