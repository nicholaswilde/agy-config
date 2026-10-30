# Secret Management & Commit Prevention

Strict guidelines preventing leakage of credentials, tokens, keys, and sensitive configs.

## Guidelines

- **Never Commit Secrets**: Never commit, stage, or push credentials, API tokens, passwords, private keys (`*.pem`, `*.key`, `id_rsa`, `id_ed25519`), `.env` files (`.env`, `.env.*`), or unencrypted secrets.
- **Sensitive Config Protection**: Never commit config/settings files containing credentials, auth tokens, or passwords (`mcp_config.json`, `settings.json`, `*credentials*.json`). Provide sanitized `.example` or template files instead.
- **Explicit Git Staging**: Never use blanket staging (`git add .` or `git add -A`) when sensitive/untracked configs exist. Stage files explicitly by name and review `git diff --staged` before commit.
- **Enforce Git Ignore**: List env files, local secrets, and credentials dirs in `.gitignore`.
- **Approved Secret Management**: Use encryption (`sops`) or secret managers (`pass`, env vars, vault) instead of plaintext files. Never hardcode secrets in source code, compose files, or scripts.
- **Immediate Remediation**: If secrets are staged, unstage immediately (`git restore --staged <file>`) or remove from index (`git rm --cached <file>`). Never commit or push.
