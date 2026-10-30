# RTK (`rtk`) Command Proxy

## Rule

Prefix raw shell commands with `rtk` whenever a subcommand exists. `rtk` filters and compresses output before it reaches model context.

## Command Map

| Raw | Use |
|---|---|
| `git <cmd>` | `rtk git <cmd>` |
| `gh <cmd>` | `rtk gh <cmd> \| cat` (see `github-cli-rules.md`) |
| `rg` / `grep` | `rtk rg` / `rtk grep` (see `ripgrep-rules.md`) |
| `ls` / `tree` / `find` | `rtk ls` / `rtk tree` / `rtk find` |
| `cat <file>` (to inspect) | `rtk read <file>` |
| `diff` | `rtk diff` |
| `wc` | `rtk wc` |
| `docker` / `kubectl` | `rtk docker` / `rtk kubectl` |
| `wget` | `rtk wget` |
| tests (`cargo test`, `task test`, `pytest`) | `rtk test <cmd>` |
| build/lint (`cargo build`, `task lint`, `cargo clippy`) | `rtk err <cmd>` |
| long logs | `rtk log` |
| other noisy commands | `rtk summary <cmd>` |

## Exceptions

1. **ctx sandbox**: inside `ctx_execute` / `ctx_batch_execute` code, `rtk` isn't needed; only printed output enters context.
2. **Exact output needed**: drop `rtk` when the exact raw bytes matter (e.g., `git diff` to apply as a patch, or file content to edit verbatim).
3. **No subcommand**: commands without an `rtk` subcommand run raw (e.g., `mkdir`, `mv`, `rm`).
4. **Unknown**: check `rtk --help` before assuming a subcommand exists.
