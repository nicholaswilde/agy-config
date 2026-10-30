# Ripgrep (`rg`) Pattern Searching

## Rule

Always use `rg` (prefixed with `rtk rg` in shell) to search file contents, code patterns, strings, and regexes across repo.

**Scope:**

- **Recursive / directory searches → always `rg`**, in native shell AND `ctx_execute` / `ctx_batch_execute` sandbox code, on any path (other repos, `~/.gemini`). Never `grep -r` or `find | xargs grep`. `rg` skips `.gitignore`d, hidden, and binary files by default, keeping junk matches out.
- **Named files or piped input → `grep` is fine.** Identical output; zero token difference.

## Guidelines

1. **RTK Integration**: Prefix with `rtk` (e.g., `rtk rg <pattern>`) in native shell. Skip `rtk` inside ctx sandbox code (only printed output enters context).
2. **File Type Filtering**: Use `-t` / `--type` to scope searches (e.g., `rtk rg -t py "class Season"`).
3. **Targeted Scoping**: Scope to relevant dirs (`src/`, `tests/`, `data/`) instead of full-repo scans.
4. **Files-Only Listing**: Use `-l` / `--files-with-matches` when listing matching files.
5. **Context Control**: Keep context small (`-C 1` or `-C 2`).
6. **File Discovery**: Use `rg --files -g '<glob>'` instead of `find -name`.

## Common Command Reference

- `rtk rg "pattern" src/` — Search within source dir
- `rtk rg -t py "def scrape" src/` — Search Python defs
- `rtk rg -i "amazing race"` — Case-insensitive search
- `rtk rg -l "Pydantic"` — List files with pattern
- `rtk rg -w "Season"` — Whole word match
- `rg -n -i 'pager|PAGER' --glob '!vendor' .` — Recursive search excluding dir (sandbox)
- `rg --files -g '*.md' ~/.gemini/config/rules` — List files by glob
