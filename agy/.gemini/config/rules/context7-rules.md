---
trigger: always_on
description: "Use ctx7 CLI first for live, version-specific library and project documentation"
---

# Context7 Live Docs CLI (`ctx7`)

## Rule

Use `ctx7` CLI inside `ctx_execute` (`language: "shell"`) FIRST when looking up library, framework, SDK, CLI, or GitHub-indexed project docs, API specs, source code, or upgrade guides before falling back to `search_web`. Never register or use Context7 as an MCP server.

## Workflow & Common Commands

| Task | Command |
|---|---|
| One-step doc search | `ctx7 search "<query>" --library <name> [--library-version <ver>]` |
| Resolve library ID | `ctx7 library <name> "<query>"` |
| Query docs by ID | `ctx7 docs <libraryId> "<query>" [--language <lang>]` |
| Search library source | `ctx7 code <libraryId> "<pattern>" [--op grep\|definition\|references\|outline\|read]` |
| Upgrade guide | `ctx7 get-upgrade-guide <libraryId> <fromVersion> [toVersion]` |

## Guidelines

1. **CLI Only**: Invoke `ctx7` directly (`npx -y ctx7@latest` fallback if not on `PATH`). Skip `rtk` inside `ctx_execute`.
2. **Bounded Output**: Run inside `ctx_execute` and print only needed snippets/answers. Pass `--json` when parsing fields.
3. **Tool Boundary**: Use `ctx7` for indexed libraries/projects; `ctx_fetch_and_index` + `ctx_search` for arbitrary URLs; `search_web` only when `ctx7` has no match or for non-library web queries.
4. **No Secrets**: Works unauthenticated; optional `ctx7 login` stays local only. Never commit tokens.
