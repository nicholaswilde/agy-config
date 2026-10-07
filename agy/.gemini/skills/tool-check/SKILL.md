---
name: tool-check
description: >
  Test and verify that rtk, caveman, context-mode, ponytail, and codegraph are working
  on the system and in this repository.
  Trigger: /tool-check, "check tools", "verify tools", "tool check", "test tools".
---

# Tool Check Procedure

Run tests to verify that all 5 critical environment tools and plugins are functional on this system and in this repository.

## 1. rtk (Token-saving CLI wrapper)
- Exec: `rtk --version` via `run_command`
- Verify: Exit code 0, returns valid `rtk x.y.z` version number.

## 2. caveman (Ultra-compressed response mode)
- Check: Verify `Response Style (caveman)` in `RULE[user_global]` or `.agents/skills/caveman/SKILL.md` exists.
- Verify: AI response format complies with caveman rules (terse, no fluff, technical accuracy preserved).

## 3. context-mode (In-sandbox analysis & indexing)
- Exec: `ctx_doctor` MCP tool via `call_mcp_tool` (ServerName: `context-mode`, ToolName: `ctx_doctor`)
- Verify: Returns status report with `[OK] Server test: PASS` and `[OK] FTS5 / SQLite: PASS`.

## 4. ponytail (YAGNI & lazy architecture enforcement)
- Check: Verify `Build Discipline (ponytail)` in `RULE[user_global]` or `.agents/skills/ponytail/` skill files.
- Verify: Principles of minimal additions, stdlib reuse, and zero unnecessary abstractions enforced.

## 5. codegraph (Prebuilt code AST index & explore tool)
- Check: Verify `.codegraph/` directory exists at root of repository.
- Exec: `codegraph_explore` MCP tool via `call_mcp_tool` (ServerName: `codegraph`, ToolName: `codegraph_explore`, query: `LVGLManager`)
- Verify: Returns AST source and symbol definitions without errors.

## Summary Output
Report status for each component:
- `rtk`: [OK / FAIL]
- `caveman`: [OK / FAIL]
- `context-mode`: [OK / FAIL]
- `ponytail`: [OK / FAIL]
- `codegraph`: [OK / FAIL]
