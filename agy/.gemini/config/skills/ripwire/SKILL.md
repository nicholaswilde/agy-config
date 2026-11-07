---
name: ripwire
description: >-
  Navigate codebases, inspect call graphs, blast radius, and apply AST symbol edits via ripwire CLI.
  Trigger: /ripwire, "ripwire", "codebase map", "call graph", "blast radius", "impact analysis".
---

# Ripwire CLI Codebase Navigation & Analysis

Use `ripwire` CLI to parse codebases, generate deterministic PageRank-ordered symbol maps, inspect call graphs, calculate blast radius, and execute atomic symbol edits.

## Core Rules

- **CLI Execution Only**: Always invoke `ripwire` via command line (`rtk ripwire <dir> [flags]`). Do NOT configure or use ripwire as an MCP server.
- **Map First**: Run `rtk ripwire <dir> --for="<task>"` before searching with grep or reading whole files.
- **Compact Legend**: Append `--legend=compact` on queries to conserve context tokens.

## Primary Workflows

### 1. Orienting Cold on a Codebase or Task

- **Task Lens (Signatures + Bodies)**:

  ```bash
  rtk ripwire <dir> --for="<task in plain words>"
  ```

  Anchors symbol mentions from task description, ranks signatures by PageRank and relevance, returns top symbol bodies inline.

- **All-in-One Task Package**:

  ```bash
  rtk ripwire <dir> --pack-task="<task>" --legend=compact
  ```

- **Architecture Overview**:

  ```bash
  rtk ripwire <dir> --report
  ```

  Outputs module clusters (Louvain partitioning), god-files, dependency cycles, and top PageRank entrypoints.

- **Locate Existing Patterns (Exemplar)**:

  ```bash
  rtk ripwire <dir> --exemplar="<kind of code to implement>" --legend=compact
  ```

### 2. Tracing Call Graphs & Blast Radius

- **Direct Callers (In-Edges)**:

  ```bash
  rtk ripwire <dir> --callers=SYM --legend=compact
  ```

- **Direct Callees (Out-Edges)**:

  ```bash
  rtk ripwire <dir> --callees=SYM --legend=compact
  ```

- **Symbol Uses (Reads, Writes, Imports, Extends)**:

  ```bash
  rtk ripwire <dir> --uses=SYM --legend=compact
  ```

- **Transitive Blast Radius (Reachability)**:

  ```bash
  rtk ripwire <dir> --impact=SYM --legend=compact
  ```

- **Shortest Call Path Between Two Symbols**:

  ```bash
  rtk ripwire <dir> --path=SRC,DST --legend=compact
  ```

### 3. Debugging & Error Mapping

- **Map Stack Trace / Compiler Error**:

  ```bash
  rtk ripwire <dir> --from-trace=<file_or_-> --legend=compact
  ```

  Maps stack frames and compiler error lines onto indexed symbols.

### 4. Quality Gates & PR Verification

- **Quality Delta (Changes Against Baseline)**:

  ```bash
  rtk ripwire <dir> --quality-delta --legend=compact
  ```

  Identifies regressions in complexity, dead code, or clones introduced in working tree or branch.

- **Test Gate**:

  ```bash
  rtk ripwire <dir> --test-gate --legend=compact
  ```

  Identifies affected tests to execute and reports untested blast radius before committing.

### 5. Atomic Symbol Edits

Perform surgical AST edits without opening or re-reading full files:

- **Replace Symbol Body**:

  ```bash
  rtk ripwire <dir> --replace-symbol-body=SYM --edit-payload=<payload_file>
  ```

- **Insert Before / After Symbol**:

  ```bash
  rtk ripwire <dir> --insert-before-symbol=SYM --edit-payload=<payload_file>
  rtk ripwire <dir> --insert-after-symbol=SYM --edit-payload=<payload_file>
  ```
