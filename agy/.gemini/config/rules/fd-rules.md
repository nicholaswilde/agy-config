# File Discovery (`fd`)

## Rule

Use `fd` (or `rtk fd` / `fdfind`) instead of `find` for finding files and directories across repositories.

**Scope:**

- **File / Directory Discovery**: Prefer `fd` over `find` in shell and subagents when `fd` is installed. `fd` respects `.gitignore`, skips hidden/build directories (`.git`, `node_modules`, `site`, caches), runs in parallel, and saves context tokens.
- **Fallback**: If `fd` not installed, fall back to `rtk find` or `find`.
- **RTK Integration**: Prefix with `rtk` (e.g. `rtk fd <pattern>`) in native shell. Skip `rtk` inside `ctx_execute` sandbox code.

## Guidelines

1. **Basic Match**: `fd <pattern>` replaces `find . -name "*<pattern>*"`. Case-insensitive by default.
2. **Extension Filter**: Use `-e` / `--extension` (e.g. `fd -e cook` instead of `find . -name "*.cook"`).
3. **Type Filter**: `-t f` for files, `-t d` for directories, `-t l` for symlinks.
4. **Depth Limit**: `--max-depth <N>` or `-d <N>` for shallow scans.
5. **Hidden / Ignored**: Use `-H` (hidden) or `-I` (ignore `.gitignore`) only when explicitly requested.
6. **Path Matching**: Use `-p` / `--full-path` when matching full path strings.

## Common Command Reference

- `rtk fd "pattern"` — Search files/folders matching pattern
- `rtk fd -e md -e cook` — Find files with `.md` or `.cook` extension
- `rtk fd -t d "soup"` — Find directories matching "soup"
- `rtk fd -t f --max-depth 2` — Find files up to depth 2
- `fd -e py . scripts/` — Find Python scripts in `scripts/` (sandbox)
