---
name: setup-serena
description: >-
  Set up, activate, and onboard the Serena MCP semantic coding server in a project.
  Triggers on "setup serena", "initialize serena", "configure serena", "activate serena",
  or when enabling Serena's LSP and symbolic tools in a codebase.
---

# Setup Serena MCP

Use this skill to configure, activate, and initialize the **Serena MCP** semantic coding server for the current workspace or target repository.

## Overview

Serena provides Language Server Protocol (LSP) backed semantic coding tools, token-efficient AST symbol search, reference-aware refactoring, and persistent project memories. Before Serena tools can be used in a project, the project directory must be registered and activated.

## Prerequisites

Serena MCP server must be registered in the agent's MCP configuration (`serena`). Available tools can be called directly or via `call_mcp_tool` with `ServerName: "serena"`.

Key Serena tools:
- `get_current_config`: Inspect active project, modes, and LSP status.
- `activate_project`: Register and switch active project to a specified directory path.
- `onboarding`: Retrieve project onboarding guidelines and memory schemas.
- `write_memory` / `read_memory` / `list_memories`: Manage durable project facts.
- `get_symbols_overview` / `find_symbol`: AST-level symbol inspection.
- `get_diagnostics_for_file`: File diagnostics and lint errors from LSP.

## Workflow

### 1. Check Serena Configuration

Check current configuration and determine if a project is already active:

```json
ToolName: "get_current_config"
Arguments: {}
```

- If an active project is already set and matches the target workspace, proceed to **Step 4 (Validation)**.
- If it returns `No active project` or points to an unrelated repository, proceed to **Step 2 (Activation)**.

### 2. Activate Workspace Project

Call `activate_project` with the absolute path of the target repository:

```json
ToolName: "activate_project"
Arguments: {
  "project": "/path/to/project"
}
```

Serena will initialize the project, detect the language server, and report language server status.

### 3. Onboarding & Project Memories (Recommended)

When initializing Serena on a project for the first time, establish persistent project memories so future agents have immediate context.

1. Call `onboarding` to inspect standard memory requirements:
   ```json
   ToolName: "onboarding"
   Arguments: {}
   ```

2. Check existing memories using `list_memories`:
   ```json
   ToolName: "list_memories"
   Arguments: {}
   ```

3. Populate baseline durable memories using `write_memory`:
   - `mem:core`: High-level architecture, module organization, entrypoints, and core invariants.
   - `mem:tech_stack`: Primary languages, frameworks, runtime versions, package managers, and build tools.
   - `mem:suggested_commands`: Common workflows (build, test, lint, dev serve, formatting).
   - `mem:conventions`: Code formatting, style rules, naming conventions, docstrings, type annotations.
   - `mem:task_completion`: Mandatory validation commands before considering any task complete.

   Example call:
   ```json
   ToolName: "write_memory"
   Arguments: {
     "memory_name": "tech_stack",
     "content": "Python 3.11+, Taskfile for task automation, uv for dependency management, MkDocs/Zensical for site build."
   }
   ```

### 4. Verify & Validate Serena Operation

Run diagnostic checks to ensure the LSP and AST parsers are fully functional:

1. **Verify Config:**
   ```json
   ToolName: "get_current_config"
   ```
   Ensure `Language server status: ready` and `Active project` points to the correct project.

2. **Test Symbol Overview:**
   Pick a representative source code file and test AST extraction:
   ```json
   ToolName: "get_symbols_overview"
   Arguments: {
     "relative_path": "path/to/code_file.ext"
   }
   ```
   Verify that top-level symbols (functions, classes, methods) are returned without error.

3. **Test Diagnostics (LSP):**
   ```json
   ToolName: "get_diagnostics_for_file"
   Arguments: {
     "relative_path": "path/to/code_file.ext"
   }
   ```

## Best Practices

- **Token Efficiency:** Prefer Serena's `get_symbols_overview`, `find_symbol`, and `search_for_pattern` over dumping entire files into context.
- **Reference-Aware Refactoring:** Use `rename_symbol` and `safe_delete_symbol` for symbol changes across the codebase instead of regex or manual edits.
- **Project Switching:** When switching working repositories in a multi-repo environment, always invoke `activate_project` for the target path before running semantic queries.
