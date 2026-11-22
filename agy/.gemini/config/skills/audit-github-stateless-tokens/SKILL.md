---
name: audit-github-stateless-tokens
description: >-
  Audit and harden repo workflows and code for GitHub stateless ghs_ App tokens (~520-char JWTs).
  Trigger: /audit-github-stateless-tokens, "audit stateless tokens", "check workflows for stateless tokens", "check ghs_ token compatibility".
---

# Audit GitHub Stateless Tokens Skill

Audit a repository's GitHub Actions workflows, scripts, and source code for compatibility with GitHub's stateless App installation token rollout (`ghs_*`, including Actions `GITHUB_TOKEN`), and apply release workflow hardening.

## Background

- **Reference:** <https://github.blog/changelog/2026-05-15-github-app-installation-tokens-per-request-override-header/>
- **Format Change:** `ghs_` installation tokens changed from ~40-char opaque strings (`ghs_[A-Za-z0-9]{36}`) to ~520-char stateless JWTs (`ghs_<app-id>_<jwt>`) containing `.`, `_`, and `-`.
- **Timeline:** Rollout completed Oct 2, 2026; temporary `X-GitHub-Stateless-S2S-Token` test header deprecates Nov 30, 2026.

## Protocol

### 1. Scan Workflows, Scripts, and Source

Run a targeted ripgrep scan (excluding lockfiles and build dirs):

```bash
rtk rg -n -i "X-GitHub-Stateless-S2S-Token|ghs_|access_tokens|create-github-app-token|Authorization:\s*token|vnd\.github\.v3\+json|actions/checkout@v[1-5]" \
  --glob "!Cargo.lock" --glob "!uv.lock" --glob "!site" --glob "!target" --glob "!.venv" .
```

Inspect every match and every `.github/workflows/*.{yml,yaml}` file for:

1. **Deprecated override header:** Any `X-GitHub-Stateless-S2S-Token` header on `POST /app/installations/:id/access_tokens` — remove once validated.
2. **Strict `ghs_` regex / length checks:** Patterns like `ghs_[A-Za-z0-9]{36}` or column/buffer caps `< 1000` chars (replace regex with `ghs_[A-Za-z0-9._-]{36,}`; treat tokens as opaque strings).
3. **Legacy REST auth headers in `curl` / HTTP calls:** Replace `-H "Authorization: token ${TOKEN}"` and `-H "Accept: application/vnd.github.v3+json"` with `-H "Authorization: Bearer ${TOKEN}"` and `-H "Accept: application/vnd.github+json"` (compatible with both PATs and stateless `ghs_` App tokens, e.g. `homebrew-tap` / `scoop-bucket` dispatch steps in `release.yaml`).
4. **Outdated `actions/checkout` or token-validating setup actions:** Align stale `actions/checkout@v4` (or older) with the repo's current major (`@v6`/`@v7`); verify third-party actions (e.g. `setup-php`/Composer CVE-2026-45793, secret scanners) are patched.

### 2. Verify Live CI / Release Runs

Check recent runs to confirm workflows already pass under live stateless `GITHUB_TOKEN`s (post-Oct 2, 2026):

```bash
rtk gh run list --limit 10 | cat
```

### 3. Harden & Validate

- Apply surgical edits only to affected workflow/code lines.
- Validate YAML and repo lint gates (`yamllint-rs .` or `task lint`).
- Report:
  1. Breaking risks found (or confirmed clean).
  2. Live CI/release run proof (run IDs + dates).
  3. Hardening changes applied (or skipped if already compliant).
