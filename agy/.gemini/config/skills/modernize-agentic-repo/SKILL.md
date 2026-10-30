---
name: modernize-agentic-repo
description: >-
  Verify and modernize repo for agentic tools (serena, rtk, ponytail, codegraph, context-mode, caveman) and .agents/ layout.
  Trigger: /modernize-agentic-repo, /modernize-agents, "modernize agent tooling", "modernize repo", "modernize workspace", "ensure agent tools", "modernize agents".
---

# Modernize Agentic Repository Skill

Use this skill to modernize a repository's workspace and tool configuration for Antigravity's agentic stack (Serena, RTK, Ponytail, CodeGraph, Context-Mode, Caveman) and standardize directory layouts under `.agents/`.

## Protocol

### 1. Stack Health & Tooling Verification

Verify and ensure all 6 agentic tools and MCP servers are functional in the workspace:

1. **Serena MCP (Semantic Coding & LSP)**
   - Call `activate_project` with the current workspace root path.
   - Run `get_current_config` via `call_mcp_tool(ServerName: "serena", ToolName: "get_current_config")` to verify project registration and LSP readiness.
   - Test symbol navigation on a key repo file via `get_symbols_overview`.

2. **RTK (Token-Optimized CLI Proxy)**
   - Check binary presence: `which rtk` or verify `/home/linuxbrew/.linuxbrew/bin/rtk`.
   - Verify version: `rtk --version`.
   - Test proxy output: `rtk git status`.

3. **Ponytail (Minimal Code & YAGNI Discipline)**
   - Confirm global ponytail rule `Build Discipline (ponytail)` is present in session context.
   - Verify ponytail skills are available (`ponytail`, `ponytail-review`, `ponytail-audit`).

4. **CodeGraph (Prebuilt AST Index & Call Graph)**
   - Check if `.codegraph/` exists in repository root. If missing, run `codegraph` CLI to index the project.
   - Verify `codegraph_explore` MCP tool via `call_mcp_tool(ServerName: "codegraph", ToolName: "codegraph_explore", query: "<symbol>")`.
   - Test CLI access: `codegraph explore "<symbol>"`.

5. **Context-Mode (In-Sandbox Execution & Bounded Routing)**
   - Run `ctx_doctor` via `call_mcp_tool(ServerName: "context-mode", ToolName: "ctx_doctor")`.
   - Verify sandbox runtimes and SQLite/FTS5 pass.
   - Confirm command-routing hooks route data-heavy inspections into `ctx_execute`.

6. **Caveman (Compressed Response Style)**
   - Confirm `Response Style (caveman)` is active in session rules.
   - Ensure caveman skills and subagent `cavecrew-builder` are available.

### 2. Repository Hygiene (`.gitignore`)

Inspect repository `.gitignore` and ensure local agent artifacts, caches, and indexes are ignored:

- Add `.codegraph/` (AST index and SQLite database).
- Add `.serena/` (local project cache, local configs, memories).
- Add `.rtk/*` with `!.rtk/filters.toml` whitelist.
- Make surgical edits without disturbing existing project rules.

### 3. Folder Consolidation (`.agents/`)

Consolidate legacy directories into the unified `.agents/` folder:

1. **Merge `.gemini/` into `.agents/`**:
   - Check if `.gemini/` exists in workspace root.
   - If present:
     - Merge subdirectories (e.g. `commands/` -> `.agents/commands/`, `skills/` -> `.agents/skills/`).
     - Remove legacy `.gemini/` directory (`rm -rf .gemini`).
2. **Migrate `conductor/` into `.agents/conductor/`**:
   - Check if root `conductor/` directory exists.
   - If present:
     - If tracked in git: migrate with `git mv conductor .agents/conductor`.
     - If untracked: move with `mv conductor .agents/conductor`.
     - Ensure root `conductor/` is removed.

### 4. Documentation & Reference Updates

Scan and update documentation references pointing to legacy paths:

- Search `AGENTS.md`, `README.md`, and workflow documentation for references to `conductor/` or `.gemini/`.
- Update paths to point to `.agents/conductor/` and `.agents/`.

### 5. Final Verification & Status Report

- Run `rtk git status` (or `git status --short`) to confirm a clean working tree and proper staging of renames.
- Summarize modernized components, changes applied, and current status terse caveman style.
