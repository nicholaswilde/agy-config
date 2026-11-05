---
name: setup-fd-rule
description: >-
  Audit, symlink, and configure global fd file discovery rule in repositories.
  Trigger: /setup-fd-rule, /setup-fd, "setup fd rule", "setup fd", "add fd rule", "configure fd rule".
---

# Setup `fd` Rule

Setup and verify global `fd` file discovery rule (`fd-rules.md`) across repositories.

## Overview

Replaces standard `find` with `fd` (or `rtk fd` / `fdfind`). Respects `.gitignore`, skips hidden/build directories, parallelizes traversal, and conserves context tokens.

Global source rule:
`/home/nicholas/git/nicholaswilde/agy-config/agy/.gemini/config/rules/fd-rules.md`

## Protocol

### 1. Target Repository Selection

- Default: current workspace root.
- Optional: explicit repository directory path argument (e.g. `/home/nicholas/git/nicholaswilde/<repo>`).
- Batch mode: iterate multiple target repositories if requested.

### 2. Verify Rule Source

Confirm global rule exists:

```bash
test -f /home/nicholas/git/nicholaswilde/agy-config/agy/.gemini/config/rules/fd-rules.md
```

### 3. Create Rule Symlink

1. Ensure `.agents/rules/` exists:

   ```bash
   mkdir -p <repo>/.agents/rules
   ```

2. Symlink rule:

   ```bash
   ln -sf /home/nicholas/git/nicholaswilde/agy-config/agy/.gemini/config/rules/fd-rules.md <repo>/.agents/rules/fd-rules.md
   ```

3. Verify symlink resolution:

   ```bash
   test -e <repo>/.agents/rules/fd-rules.md
   ```

### 4. Repository Hygiene (`.gitignore`)

Check `<repo>/.gitignore`. Ensure `.agents/rules/` is whitelisted:

```gitignore
.agents/*
!.agents/rules/
```

### 5. Update Documentation (`AGENTS.md`)

If `<repo>/AGENTS.md` exists and contains `<!-- rtk-begin -->`:
Ensure `File & Directory Inspection` lists `rtk fd`:

```markdown
- **File & Directory Inspection**: Use `rtk ls`, `rtk tree`, `rtk find`, `rtk fd`, or `rtk read` when listing or reading files for token-optimized output.
```

### 6. Verify & Test

1. If `fd` installed, test execution:

   ```bash
   rtk fd --max-depth 1
   ```

2. Run repository test suite if applicable (`task test`, `cargo test`, `uv run pytest`).

### 7. Stage & Commit

1. Stage changes explicitly:

   ```bash
   git -C <repo> add .agents/rules/fd-rules.md
   ```

   Stage `AGENTS.md` or `.gitignore` only if modified.

2. Commit using Conventional Commits:

   ```bash
   git -C <repo> commit -m "chore(rules): add fd-rules symlink"
   ```

3. Push if requested or upstream tracking branch configured.

### 8. Batch Mode Helper

Audit and link across all repositories:

```bash
for dir in /home/nicholas/git/nicholaswilde/*/; do
  if [ -d "$dir/.git" ] && [ -d "$dir/.agents/rules" ]; then
    ln -sf /home/nicholas/git/nicholaswilde/agy-config/agy/.gemini/config/rules/fd-rules.md "$dir/.agents/rules/fd-rules.md"
  fi
done
```
