---
trigger: always_on
description: "Clear shell command hash table after removing Homebrew packages"
---

# Homebrew (`brew`) Rules

## Rule

After uninstalling or removing Homebrew formulas (`brew uninstall` / `brew remove`), run `hash -r` in the same shell check before verifying fallback binaries:

```bash
brew uninstall <pkg>
hash -r
```

## Guidelines

1. **Refresh Subshell Path Cache**: Bash caches resolved binary paths; `hash -r` forces fresh `PATH` lookup (e.g., `/home/linuxbrew/.linuxbrew/bin` -> `~/.local/bin`).
2. **Interactive Terminal Note**: Tool subshells do not alter user's open terminal hash table; remind user to run `hash -r` in active interactive shell when a replacement binary remains on `PATH`.
