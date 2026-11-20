---
name: context7
description: >-
  Fetch up-to-date, version-specific library docs, code examples, and upgrade guides via ctx7 CLI.
  Trigger: /context7, "context7", "ctx7", "library docs", "up-to-date docs", "SDK docs", "upgrade guide".
---

# Context7 Docs CLI (`ctx7`)

Fetch live, version-specific library documentation, source code, and upgrade guides via `ctx7` CLI instead of relying on stale training data.

## Core Rules

- **CLI Only**: Invoke `ctx7` via CLI (`npx -y ctx7@latest` fallback if `ctx7` not on `PATH`). No MCP server needed.
- **Keep Output Bounded**: Run `ctx7` inside `ctx_execute` (`language: "shell"`) and print only needed snippets/answers when output may be large.
- **Boundary with `context-mode`**: Use `ctx7` for known library/framework/SDK docs and source; use `ctx_fetch_and_index` + `ctx_search` for arbitrary URLs/webpages.
- **No Secrets in Repo**: Works without API key. Optional `ctx7 login` OAuth increases rate limits locally; never commit tokens.

## Primary Workflows

### 1. One-Step Search

```bash
ctx7 search "<query>" --library <name> [--library-version <version>] [--language <lang>]
```

- Repeat `--library` up to 4 times. Accept library name (`Next.js`) or ID (`/vercel/next.js`).

### 2. Resolve ID + Query Docs (Two-Step)

```bash
ctx7 library <name> "<query>"
ctx7 docs <libraryId> "<query>" [--language <lang>]
```

- Run one focused `<query>` per distinct concept.
- Pass `--json` when parsing fields in `ctx_execute`.

### 3. Search Library Source Code

```bash
ctx7 code <libraryId> "<pattern>" [--tag <version_tag>] [--op grep|definition|references|outline|read|list]
```

- Supports `-F` (fixed strings), `-i`, `-g <glob>`, `-C <n>`, `-l`, `--path <path#L10-L40>`.

### 4. Version Upgrade Guide

```bash
ctx7 get-upgrade-guide <libraryId> <fromVersion> [toVersion] [--page <n>]
```

- Fetches breaking changes, codemods, deprecations, and API changes between versions.
