# Secret Management & Commit Prevention

Strict guidelines to prevent accidental leakage of credentials, tokens, keys, and sensitive configurations.

## Guidelines

- **Never Commit Secrets**: Never commit, stage, or push credentials, API tokens, passwords, private keys (`*.pem`, `*.key`, `id_rsa`, `id_ed25519`), `.env` files (`.env`, `.env.*`), or unencrypted secrets.
- **Sensitive Config Protection**: Never commit configuration or settings files that contain credentials, auth tokens, or passwords (e.g., `mcp_config.json`, `settings.json`, `*credentials*.json`). Provide sanitized `.example` or template files instead.
- **Explicit Git Staging**: Never use blanket staging commands (`git add .` or `git add -A`) when sensitive or untracked configuration files are present. Stage files explicitly by name and review staged changes (`git diff --staged`) before committing.
- **Enforce Git Ignore**: Ensure environment files, local secrets, and credentials directories are listed in `.gitignore`.
- **Approved Secret Management**: Use encryption tooling (`sops`) or password managers (`pass`, secure environment variables, vault/secret managers) rather than plaintext files. Never hardcode plaintext secrets in source code, Docker compose files, or scripts.
- **Immediate Remediation**: If sensitive files or secrets are staged, unstage immediately (`git restore --staged <file>`) or remove from index (`git rm --cached <file>`). Never commit or push them.
