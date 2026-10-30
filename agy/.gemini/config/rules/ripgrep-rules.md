# Ripgrep (`rg`) Pattern Searching

## Rule

Always use `rg` (prefixed with `rtk rg` in the shell) for searching file contents, code patterns, strings, and regular expressions across the repository.

**Scope:**

- **Recursive / directory searches → always `rg`**, in native shell AND `ctx_execute` / `ctx_batch_execute` sandbox code, on any path (other repos, `~/.gemini`). Never `grep -r` or `find | xargs grep`. Reason: `rg` skips `.gitignore`d, hidden, and binary files by default, which keeps junk matches out of the output.
- **Named files or piped input → `grep` is fine.** Output is identical; there's no token gain.

## Guidelines

1. **RTK Integration**: Always prefix with `rtk` (e.g., `rtk rg <pattern>`) to compress output and filter noise before it reaches the model context.
   Not needed inside ctx sandbox code: only printed output enters context.
2. **File Type Filtering**: Use `-t` / `--type` to scope searches (e.g., `rtk rg -t py "class Season"`).
3. **Targeted Scoping**: Scope searches to relevant directories (`src/`, `tests/`, `data/`) rather than unconstrained searches across large binary or cache directories.
4. **Files-Only Listing**: When looking for files containing a pattern, use `-l` / `--files-with-matches` to keep output minimal.
5. **Context Control**: Keep context lines small (`-C 1` or `-C 2`) when examining surrounding lines.
6. **File Discovery**: Use `rg --files -g '<glob>'` instead of `find -name`. It applies the same ignore filtering.

## Common Command Reference

- `rtk rg "pattern" src/` — Search within source directory
- `rtk rg -t py "def scrape" src/` — Search Python definitions
- `rtk rg -i "amazing race"` — Case-insensitive search
- `rtk rg -l "Pydantic"` — List files containing pattern
- `rtk rg -w "Season"` — Match whole word only
- `rg -n -i 'pager|PAGER' --glob '!vendor' .` — Recursive search excluding a dir (sandbox form)
- `rg --files -g '*.md' ~/.gemini/config/rules` — List files by glob
