# commit-agy-config

Create git commits and pushes for new or updated Antigravity skills, rules, and configs.

## What it does

- Audits repository status for modified or untracked skills, rules, and configs.
- Enforces secret prevention rules (no API keys, tokens, `.env` files).
- Lints Markdown (`rumdl`) and YAML (`yamllint`).
- Stages files explicitly by name (never `git add .`).
- Generates terse Conventional Commit messages (≤50 chars).
- Commits and pushes to remote upstream.
- Verifies symlinks and Stow status for `~/.gemini/`.

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
