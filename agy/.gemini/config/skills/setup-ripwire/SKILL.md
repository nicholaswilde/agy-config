---
name: setup-ripwire
description: >-
  Audit, symlink rules, and configure Ripwire CLI in a repository.
  Triggers on "setup ripwire", "configure ripwire", "initialize ripwire",
  "activate ripwire", "/setup-ripwire", or when enabling Ripwire CLI tools in a codebase.
---

# Setup Ripwire CLI

Configure, audit, and initialize **Ripwire CLI** codebase analysis and AST navigation in a target repository.

## Overview

Ripwire parses codebases into deterministic PageRank-ordered symbol maps, extracts call graphs, computes blast radius, and executes atomic AST symbol replacements.

Uses the `ripwire` CLI directly via `rtk ripwire`. Never register or invoke Ripwire through MCP servers.

Global rule source:
`/home/nicholas/git/nicholaswilde/agy-config/agy/.gemini/config/rules/ripwire-rules.md`

## Workflow

### 1. Verify Binary & Environment Health

Check `ripwire` binary is available on PATH:

```bash
which ripwire
```

Run Ripwire doctor check on target repository:

```bash
rtk ripwire <repo> --doctor
```

Verify `checks` match `passed` and all core language grammars load.

### 2. Verify Rule Source

Ensure global rule exists:

```bash
test -f /home/nicholas/git/nicholaswilde/agy-config/agy/.gemini/config/rules/ripwire-rules.md
```

### 3. Symlink Rule into Repository

1. Ensure `.agents/rules/` directory exists:

   ```bash
   mkdir -p <repo>/.agents/rules
   ```

2. Symlink global rule:

   ```bash
   ln -sf /home/nicholas/git/nicholaswilde/agy-config/agy/.gemini/config/rules/ripwire-rules.md <repo>/.agents/rules/ripwire-rules.md
   ```

3. Verify link resolves:

   ```bash
   test -e <repo>/.agents/rules/ripwire-rules.md
   ```

### 4. Update Repository `AGENTS.md`

If `<repo>/AGENTS.md` exists:

1. Under `<!-- rtk-begin -->` (RTK Command Guidelines), add:

   ```markdown
   - **Ripwire Operations**: Prefix `ripwire` commands with `rtk` (e.g., `rtk ripwire <dir> --for="<task>"`). Always invoke via CLI, never register or use MCP.
   ```

2. Add `<!-- ripwire-begin -->` block:

   ```markdown
   <!-- ripwire-begin -->
   ## Ripwire CLI Guidelines

   Use `ripwire` CLI (prefixed with `rtk ripwire`) for AST codebase mapping, call graphs, blast radius, and structural queries:

   - **CLI First**: Always invoke `rtk ripwire <dir> [flags]` via CLI; do NOT use MCP server.
   - **Task Orientation**: `rtk ripwire <dir> --for="<task>"` for ranked signatures and bodies.
   - **Task Bundle**: `rtk ripwire <dir> --pack-task="<task>" --legend=compact`.
   - **Stack Trace / Error**: `rtk ripwire <dir> --from-trace=FILE --legend=compact` (`-` for stdin).
   - **Call Graph**: `rtk ripwire <dir> --callers=SYM`, `--callees=SYM`, `--uses=SYM`.
   - **Blast Radius**: `rtk ripwire <dir> --impact=SYM --legend=compact` before changing shared code.
   - **Quality Delta & Gate**: `rtk ripwire <dir> --quality-delta --legend=compact` and `--test-gate --legend=compact`.
   - **Atomic Edits**: `rtk ripwire <dir> --replace-symbol-body=SYM --edit-payload=FILE` without whole-file re-reading.
   <!-- ripwire-end -->
   ```

### 5. Repository Hygiene (`.gitignore`)

Verify `<repo>/.gitignore` whitelists `.agents/rules/`:

```gitignore
.agents/*
!.agents/rules/
```

### 6. Warm Index & Validate Execution

Test and warm the symbol cache:

1. Test ranked symbol map:

   ```bash
   rtk ripwire <repo> --top-k=5
   ```

2. Test architecture report:

   ```bash
   rtk ripwire <repo> --report
   ```

Verify output completes without error.

### 7. Stage & Commit

1. Explicitly stage changed files:

   ```bash
   git -C <repo> add .agents/rules/ripwire-rules.md AGENTS.md
   ```

2. Commit using Conventional Commits:

   ```bash
   git -C <repo> commit -m "chore(agents): setup ripwire CLI integration"
   ```

3. Push if upstream configured:

   ```bash
   git -C <repo> push
   ```

### 8. Batch Audit Helper

Audit and link across all repositories:

```bash
for dir in /home/nicholas/git/nicholaswilde/*/; do
  if [ -d "$dir/.git" ] && [ -d "$dir/.agents/rules" ]; then
    ln -sf /home/nicholas/git/nicholaswilde/agy-config/agy/.gemini/config/rules/ripwire-rules.md "$dir/.agents/rules/ripwire-rules.md"
  fi
done
```
