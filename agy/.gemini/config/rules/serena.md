# Serena Semantic Navigation & LSP Integration

Serena MCP provides LSP semantic coding tools, AST symbol search, reference-aware refactoring, and persistent project memories.

## Rule

Use Serena (`serena`) MCP tools for semantic navigation, AST symbol inspection, LSP diagnostics, and project memories.

## Initialization

Serena auto-activates from working dir (`--project-from-cwd`).

1. If Serena returns `No active project`, call `activate_project` with workspace dir or project name.
2. Call `read_memory` or `list_memories` when task needs project memories.

## Mandatory Code Update Workflow

When reading or modifying source code files (`.rs`, `.py`, `.go`, `.ts`, `.js`, `.c`, `.cpp`, `.java`):

1. **Map first:** Call `get_symbols_overview` on target file instead of `read_file` on whole file.
2. **Read target symbol only:** Call `find_symbol` with `include_body: true` for target function/struct/method.
3. **Check callers:** Call `find_referencing_symbols` / `find_implementations` when signature or behavior changes.
4. **Edit by symbol:** Use `replace_symbol_body`, `insert_after_symbol`, `insert_before_symbol`, `rename_symbol`, or `safe_delete_symbol`. Use `edit_file` only for 1–5 line tweaks inside a loaded symbol body or non-code files (configs, docs, fixtures).
5. **Verify:** Call `get_diagnostics_for_file` after edits to catch LSP errors before full builds.

## Tool Mappings & Capabilities

- **Pattern Search:** `search_for_pattern` when symbol path is unknown.
- **Project Memories:** `read_memory`, `write_memory`, `list_memories` for durable context in `.serena/memories/`.

## CodeGraph vs. Serena Boundary

- **CodeGraph (`codegraph_explore`):** Multi-hop architecture, cross-language blast radius, system call paths.
- **Serena (`serena`):** Single-symbol AST inspection/editing, LSP diagnostics, durable memories.
