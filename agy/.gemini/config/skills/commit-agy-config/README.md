# commit-agy-config

Create git commits and pushes for new or updated Antigravity skills, rules, and configs.

## What it does

- Audits repository status for modified or untracked skills, rules, and configs.
- Enforces secret prevention rules via `enstow doctor --staged` (`task check-secrets`) and explicit staging (never `git add .`).
- Lints Markdown (`rumdl`), YAML (`yamllint`), and token budgets (`lint-tokens.py`).
- Generates terse Conventional Commit messages (≤50 chars).
- Commits and pushes to remote upstream.
- Syncs symlinks (`task apply`) and verifies `task status -- --check` and `task doctor` for `~/.gemini/`.

## How to invoke

```text
/commit-agy-config
```

Also triggers on:

- "commit agy config"
- "commit agy skills"
- "commit agy rules"
- "commit and push agy config"
- "sync agy config"

## See also

- [`SKILL.md`](./SKILL.md) — full LLM-facing instructions
