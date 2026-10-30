# Serena Semantic Navigation & LSP Integration

Serena MCP provides Language Server Protocol (LSP) backed semantic coding tools, token-efficient AST symbol search, reference-aware refactoring, and persistent project memories.

## Rule

Always activate and use Serena (`serena`) MCP tools for semantic navigation, AST symbol inspection, LSP diagnostics, and project memory management.

## Initialization

Serena auto-activates from the working directory (`--project-from-cwd`).

1. If Serena returns `No active project`, call `activate_project` with the workspace directory or project name.
2. Call `read_memory` or `list_memories` when task context requires project memories.

## Mandatory Code Update Workflow

When reading or modifying source code files (`.rs`, `.py`, `.go`, `.ts`, `.js`, `.c`, `.cpp`, `.java`):

1. **Map first:** Call `get_symbols_overview` on the target file instead of `read_file` on the whole file.
2. **Read target symbol only:** Call `find_symbol` with `include_body: true` for the specific function, struct, or method being changed.
3. **Check callers when signature/behavior changes:** Call `find_referencing_symbols`.
4. **Edit by symbol:** Use `replace_symbol_body`, `insert_after_symbol`, `insert_before_symbol`, or `rename_symbol` when modifying a whole symbol. Use `edit_file` only for 1–5 line surgical tweaks inside a symbol body already loaded via `find_symbol` or `codegraph_explore`, or for non-code files (configs, docs, tests fixtures).
5. **Verify:** Call `get_diagnostics_for_file` after edits to catch LSP errors before running full builds.

## Tool Mappings & Capabilities

- **Symbol Overview & Definitions:** Do not dump entire source code files into context. Use `get_symbols_overview` for a high-level view of symbols in a file, or `find_symbol` to inspect class/function signatures and bodies.
- **Pattern & Reference Tracking:** Use `search_for_pattern` to locate symbols when the path is unknown, and `find_referencing_symbols` / `find_implementations` to trace symbol usage, callers, and blast radius across the codebase.
- **Atomic Refactoring:** Prefer Serena's reference-aware editing tools (`rename_symbol`, `safe_delete_symbol`, `replace_symbol_body`) over manual regex or line-based text edits for atomic, reference-safe AST refactors across files.
- **LSP Diagnostics:** Use `get_diagnostics_for_file` (e.g. Clangd / Pyright LSP) to verify type consistency and catch compiler/linter warnings and syntax errors on modified files before committing.
- **Project Memories:** Use `read_memory`, `write_memory`, and `list_memories` to access and persist durable project context and conventions in `.serena/memories/` across agent sessions.

## CodeGraph vs. Serena Boundary

- **CodeGraph (`codegraph_explore`):** Use for multi-hop repository architecture, cross-language blast radius, and system-level call paths.
- **Serena (`serena`):** Use for symbol-level semantic navigation, LSP diagnostics, AST-aware refactoring, and durable memories.
