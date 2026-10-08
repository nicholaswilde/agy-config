# Serena Semantic Navigation & LSP Integration

Serena MCP provides Language Server Protocol (LSP) backed semantic coding tools, token-efficient AST symbol search, reference-aware refactoring, and persistent project memories.

## Rule

Always activate and use Serena (`serena`) MCP tools for semantic navigation, AST symbol inspection, LSP diagnostics, and project memory management.

## Initialization

Before modifying or analyzing code, ensure the project is active:

1. Call `activate_project` with the current workspace directory or project name if not already activated (or when Serena returns `No active project`).
2. Call `read_memory` (e.g. `critical_info`) or `list_memories` to load essential project constraints.

## Tool Mappings & Capabilities

- **Symbol Overview & Definitions:** Do not dump entire source code files into context. Use `get_symbols_overview` for a high-level view of symbols in a file, or `find_symbol` to inspect class/function signatures and bodies.
- **Pattern & Reference Tracking:** Use `search_for_pattern` to locate symbols when the path is unknown, and `find_referencing_symbols` / `find_implementations` to trace symbol usage, callers, and blast radius across the codebase.
- **Atomic Refactoring:** Prefer Serena's reference-aware editing tools (`rename_symbol`, `safe_delete_symbol`, `replace_symbol_body`) over manual regex or line-based text edits for atomic, reference-safe AST refactors across files.
- **LSP Diagnostics:** Use `get_diagnostics_for_file` (e.g. Clangd / Pyright LSP) to verify type consistency and catch compiler/linter warnings and syntax errors on modified files before committing.
- **Project Memories:** Use `read_memory`, `write_memory`, and `list_memories` to access and persist durable project context and conventions in `.serena/memories/` across agent sessions.

## CodeGraph vs. Serena Boundary

- **CodeGraph (`codegraph_explore`):** Use for multi-hop repository architecture, cross-language blast radius, and system-level call paths.
- **Serena (`serena`):** Use for symbol-level semantic navigation, LSP diagnostics, AST-aware refactoring, and durable memories.
