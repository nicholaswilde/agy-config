---
trigger: always_on
description: "Ripwire CLI codebase navigation, call graphs, and blast radius"
---

# Ripwire CLI Codebase Navigation & Analysis

## Rule

Use `ripwire` CLI binary (prefixed with `rtk ripwire`) for AST codebase mapping, call graphs, blast radius, and structural queries. Never register or invoke ripwire via MCP server.

Reach for `rtk ripwire` before multi-turn grep loops or reading whole files.

## Workflow & Common Commands

| Task | Command |
|---|---|
| Orient on task | `rtk ripwire <dir> --for="<task>"` |
| All-in-one task bundle | `rtk ripwire <dir> --pack-task="<task>" --legend=compact` |
| Stack trace / error | `rtk ripwire <dir> --from-trace=FILE --legend=compact` (`-` for stdin) |
| Direct callers | `rtk ripwire <dir> --callers=SYM --legend=compact` |
| Direct callees | `rtk ripwire <dir> --callees=SYM --legend=compact` |
| References / uses | `rtk ripwire <dir> --uses=SYM --legend=compact` |
| Blast radius (transitive) | `rtk ripwire <dir> --impact=SYM --legend=compact` |
| Architecture summary | `rtk ripwire <dir> --report` |
| Similar existing code | `rtk ripwire <dir> --exemplar="<task|kind>" --legend=compact` |
| Quality delta (pre-PR) | `rtk ripwire <dir> --quality-delta --legend=compact` |
| Untested change gate | `rtk ripwire <dir> --test-gate --legend=compact` |
| Atomic symbol edit | `rtk ripwire <dir> --replace-symbol-body=SYM --edit-payload=FILE\|-` |

## Guidelines

1. **CLI Only**: Run through shell via `rtk ripwire`. MCP server mode disabled.
2. **Compact Legend**: Append `--legend=compact` on queries to save context tokens. Use `--legend=full` only when definitions need explanation.
3. **Targeted Reading**: Avoid whole-file reads. Use `--expand=SYM --legend=compact` for full symbol body with callee signatures.
4. **Symbol Edits**: Use `--replace-symbol-body=SYM`, `--insert-before-symbol=SYM`, or `--insert-after-symbol=SYM` with `--edit-payload` for atomic updates without re-reading whole files.
5. **Counts Are Floors**: Any count flagged `counts_floor` represents lower bound, not total. `0` indicates none found.
