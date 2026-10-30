---
name: commit-agy-config
description: >-
  Audit, stage, commit, and push Antigravity (agy) skills, rules, and configs in agy-config or .agents/.
  Trigger: "commit agy config", "commit agy changes", "commit agy skills", "commit agy rules", "commit and push agy config", "sync agy config", "push agy config", "/commit-agy-config", "/sync-agy-config".
---

# Commit and Push AGY Config Skill

Workflow for safely auditing, staging, committing, and pushing new or updated Antigravity (agy) skills, rules, and configuration files.

## Protocol

### 1. Identify Changed and Untracked Customizations

Audit git status for modified or newly added agy assets:

- Run `rtk git status --short` (or `git status --porcelain=v1`).
- Target paths:
  - **Skills**: `skills/<name>/` (e.g. `SKILL.md`, `README.md`, scripts, references)
  - **Rules**: `rules/<name>.md`, `AGENTS.md`, `GEMINI.md`
  - **Configs**: `settings.json`, `config.json`, `mcp_config.json`, plugin/hook manifests
  - **Supporting files**: `Taskfile.yml`, `README.md`, `.gitignore`, `systemd/` when modified as part of the customization
- If no target files are dirty or untracked, stop and report: `working tree clean; nothing to commit`.

### 2. Mandatory Secret & Sensitive Data Audit

Strictly enforce secret management guidelines before staging any file:

- **Scan candidate files**: Verify no API tokens, auth credentials, passwords, private keys (`*.pem`, `*.key`, `id_rsa`, `id_ed25519`), or `.env` files are included.
- **Sanitize configs**: Check that configuration files (`settings.json`, `mcp_config.json`, `config.json`) contain no plaintext secrets or personal access tokens.
- **No blanket staging**: NEVER run `git add .` or `git add -A`. All targets must be staged explicitly by path.

### 3. Formatting & Linting Validation

Ensure modified assets pass repository linting standards:

- **Markdown**: Run `task lint:md` (or `rumdl check .`). If violations exist, fix or run `task fmt:md`.
- **YAML**: Run `task lint:yaml` (or `yamllint-rs .`) if YAML files were touched.
- **Skill Frontmatter**: Verify new or updated `SKILL.md` files contain valid YAML frontmatter with `name` and `description`.

### 4. Explicit Staging & Diff Review

Stage target files explicitly:

- Stage candidate paths: `git add <file1> <file2> ...`
- Inspect staged files: `git diff --staged --name-status`
- Review staged diff: `git diff --staged` to confirm only intended changes are included and no secrets or unintended edits exist.

### 5. Conventional Commit Generation

Generate a terse commit message adhering to Conventional Commits:

- **Format**: `<type>(<scope>): <imperative summary>`
- **Types**:
  - `feat`: new skill, rule, or configuration feature
  - `fix`: bug fix or correction in skill, rule, or configuration
  - `chore`: maintenance, dependency bump, routine config sync
  - `docs`: documentation updates
  - `style`: formatting or markdown fixes
- **Scope**:
  - `feat(skill): add <name> skill`
  - `fix(skill): resolve <issue> in <name> skill`
  - `feat(rule): add <name> rule`
  - `chore(config): update mcp_config.json`
  - `feat(agy): add <name> skill and rules`
- **Guidelines**:
  - Subject length ≤ 50 characters, lowercase imperative mood, no trailing period.
  - Body only when context or "why" is non-obvious.
  - Reference issues/PRs if applicable (e.g. `Fixes #...`).
- Execute commit: `git commit -m "<message>"`

### 6. Push to Remote Upstream

Push committed changes to the tracking branch:

- Check upstream branch: `git rev-parse --abbrev-ref @{u} 2>/dev/null`
- If upstream exists: `git push origin <branch>`
- If upstream branch is not set: `git push -u origin <branch>`
- Verify push exit code and confirmation.

### 7. Sync & Stow Verification (for agy-config)

When operating inside the `agy-config` dotfiles repository:

- Ensure new skills and rules are mirrored/symlinked into `~/.gemini/` (e.g., `ln -sf` or `task restow`).
- Verify uncommitted change alerts reset via `task notify:check`.

### 8. Terse Caveman Status Report

Output concise confirmation:

- Staged and committed files
- Commit SHA and subject
- Push status and remote tracking branch
