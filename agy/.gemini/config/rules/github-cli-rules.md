# GitHub CLI (`gh`) Non-Interactive Execution

## Rule

Always pipe GitHub CLI (`gh`) commands to `cat` to bypass interactive prompts and pagers:

```bash
rtk gh <command> | cat
```

## Guidelines

1. **Never Run Bare `gh` Interactively**: Without pipe, `gh` may invoke pager (`less`) or wait on prompts, hanging execution.
2. **Combine with RTK**: Prefix with `rtk` while piping to `cat` (e.g., `rtk gh issue list | cat`).
3. **Explicit Non-Interactive Flags**: Pass required args (`--title`, `--body`, `--label`, `--non-interactive`) so `gh` never prompts.

## Examples

- `rtk gh issue list | cat`
- `rtk gh issue view 12 | cat`
- `rtk gh pr list | cat`
- `rtk gh pr diff 4 | cat`
- `rtk gh run list | cat`
