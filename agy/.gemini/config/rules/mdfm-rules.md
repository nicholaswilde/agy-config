# Markdown Frontmatter (`mdfm`)

## Rule

Run `mdfm` directly without `rtk` prefix. `rtk` has no `mdfm` filter and falls back to 0% passthrough. Save 89–93% tokens natively with `--output plain` (TSV) or `-l` (`--files-only`) instead of default Unicode `table` output.

## Guidelines

1. **No `rtk` Prefix**: Run `mdfm` directly. `rtk mdfm` hits `rtk fallback` (0% savings); `rtk summary` truncates query payloads.
2. **Skip Default `table` Output**: Pass `--output plain` (compact TSV, ~90% smaller) for `get`, `keys`, `values`, `set`, `del`, `mv`, or `-l`/`--files-only` (~93% smaller) when only matching paths matter. Use `--output json` only when structured parsing is required.
3. **Filter Early (`--where`)**: Narrow matches with `--where` and target subdirs instead of scanning entire trees.
4. **Compact Validation**: Rely on `errors_only = true` in `.mdfm.toml` (or `-q`/`--errors-only`) for `mdfm check` and `--files-only` for `mdfm fmt --check`.
5. **Bulk Queries in `context-mode`**: Run repo-wide queries/aggregations inside `ctx_execute` and print only the derived answer.

## Common Command Reference

- `mdfm --output plain get tags docs/breakfast/` — Compact TSV values (~89% smaller)
- `mdfm --where 'tags contains "must-try"' -l get . docs/` — Matching paths only (~93% smaller)
- `mdfm --output plain keys docs/` — Compact key audit (~90% smaller)
- `mdfm --output plain values tags docs/` — Compact value counts (~92% smaller)
- `mdfm check docs/ cook/` — Schema validation (`errors_only = true` in `.mdfm.toml`)
- `mdfm fmt --check --files-only docs/ cook/` — Silent when formatted; lists unformatted paths only
