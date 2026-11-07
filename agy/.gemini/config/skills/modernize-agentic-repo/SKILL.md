---
name: modernize-agentic-repo
description: >-
  Verify and modernize repo for agentic tools (serena, rtk, ponytail, codegraph, context-mode, caveman, headroom, ripwire), rules, and .agents/ layout.
  Trigger: /modernize-agentic-repo, /modernize-agents, "modernize agent tooling", "modernize repo", "modernize workspace", "ensure agent tools", "modernize agents".
---

# Modernize Agentic Repository Skill

Use this skill to modernize a repository's workspace and tool configuration for Antigravity's agentic stack (Serena, RTK, Ponytail, CodeGraph, Context-Mode, Caveman, Headroom, Ripwire), configure agentic rules (including `uv-rules.md`, `ripwire-rules.md`), and standardize directory layouts under `.agents/`.

## Protocol

### 1. Stack Health & Tooling Verification

Verify and ensure all 8 agentic tools are functional in the workspace:

1. **Serena MCP (Semantic Coding & LSP)**
   - Automatically execute the `/setup-serena` workflow:
     - Check project status via `get_current_config`.
     - Call `activate_project` with current workspace root path if not active or pointing elsewhere.
     - Inspect memories with `list_memories`. If onboarding memories are missing, call `onboarding` and populate baseline durable memories (`mem:core`, `mem:tech_stack`, `mem:suggested_commands`, `mem:conventions`, `mem:task_completion`) via `write_memory`.
     - Test symbol navigation on a key repo file via `get_symbols_overview` and verify diagnostics with `get_diagnostics_for_file`.

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
   - Run `ctx_doctor` via `call_mcp_tool(ServerName: "context-mode_context-mode", ToolName: "ctx_doctor")` (fallback `"context-mode"`).
   - Ensure plugin MCP server is used; remove any duplicate `context-mode` from `~/.gemini/config/mcp_config.json`.
   - Verify sandbox runtimes and SQLite/FTS5 pass.
   - Confirm command-routing hooks route data-heavy inspections into `ctx_execute`.

6. **Caveman (Compressed Response Style)**
   - Confirm `Response Style (caveman)` is active in session rules.
   - Ensure caveman skills and subagent `cavecrew-builder` are available.

7. **Headroom MCP (Context Window Compression)**
   - Run `headroom_stats` via `call_mcp_tool(ServerName: "headroom", ToolName: "headroom_stats")` to verify MCP server readiness.
   - Confirm `headroom_compress` and `headroom_retrieve` tools are available for shrinking large tool outputs and retrieving by hash.

8. **Ripwire CLI (Codebase Map, AST Navigation, Blast Radius)**
   - Automatically execute the `/setup-ripwire` workflow:
     - Verify binary availability via `which ripwire`.
     - Run health check via `rtk ripwire . --doctor`.
     - Ensure global rule is symlinked: `.agents/rules/ripwire-rules.md`.
     - Ensure `AGENTS.md` contains `<!-- ripwire-begin -->` and `rtk ripwire` in `<!-- rtk-begin -->`.
     - Test and warm cache via `rtk ripwire . --top-k=5` and `rtk ripwire . --report`.

### 2. Repository Hygiene (`.gitignore`)

Inspect repository `.gitignore` and ensure local agent artifacts, caches, and indexes are ignored:

- Add `.codegraph/` (AST index and SQLite database).
- Add `.serena/` (local project cache, local configs, memories).
- Add `.rtk/*` with `!.rtk/filters.toml` whitelist.
- If Python files, scripts, or package definitions are present, ensure Python caches and environments are ignored (`.venv/`, `__pycache__/`, `*.pyc`).
- Whitelist `.agents/` assets:

  ```gitignore
  .agents/*
  !.agents/skills/
  !.agents/rules/
  !.agents/skills_catalog.md
  ```

- Make surgical edits without disturbing existing project rules.

### 3. Folder Consolidation & Rules Setup (`.agents/`)

Consolidate legacy directories and set up agentic rules under `.agents/`:

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
3. **Setup Rules (`.agents/rules/`)**:
   - Ensure `.agents/rules/` directory exists (`mkdir -p .agents/rules`).
   - Symlink universal rules pointing to `/home/nicholas/git/nicholaswilde/agy-config/agy/.gemini/config/rules/<rule>.md`:
     - `caveman-rules.md`
     - `fd-rules.md`
     - `github-cli-rules.md`
     - `no-secrets.md`
     - `ripgrep-rules.md`
     - `rtk-rules.md`
     - `ripwire-rules.md`
     - `serena.md`
     - `taplo-rules.md` (when TOML files exist)
   - **Setup `uv-rules.md`**:
     - Check if repo uses Python (`pyproject.toml`, `requirements*.txt`, `setup.py`, `scripts/*.py`, `.python-version`, or Python code).
     - If Python is present:
       - Create symlink: `ln -sf /home/nicholas/git/nicholaswilde/agy-config/agy/.gemini/config/rules/uv-rules.md .agents/rules/uv-rules.md`.
       - Verify symlink resolution (`test -e .agents/rules/uv-rules.md`).
       - Ensure `AGENTS.md` contains `<!-- uv-rules-begin -->` section enforcing prefixing Python scripts/commands with `uv` and keeping `uv.lock` and `pyproject.toml` synchronized.

### 4. Documentation & Reference Updates

Scan and update documentation references pointing to legacy paths and core rules:

- Search `AGENTS.md`, `README.md`, and workflow documentation for references to `conductor/` or `.gemini/`.
- Update paths to point to `.agents/conductor/` and `.agents/`.
- If Python is present, ensure `AGENTS.md` documents `uv` command prefixing and lockfile synchronization (`uv.lock` and `pyproject.toml`).

### 5. Final Verification & Status Report

- Run `rtk git status` (or `git status --short`) to confirm a clean working tree and proper staging of renames.
- Summarize modernized components, changes applied, and current status terse caveman style.
