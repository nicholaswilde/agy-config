# RTK (`rtk`) Command Proxy

## Rule

Prefix raw shell commands with `rtk` whenever subcommand exists. `rtk` filters and compresses output before model context.

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

1. **ctx sandbox**: inside `ctx_execute` / `ctx_batch_execute`, skip `rtk`; only printed output enters context.
2. **Exact output needed**: drop `rtk` when raw bytes matter (`git diff` patch, verbatim file edit).
3. **No subcommand**: run commands without `rtk` subcommand raw (`mkdir`, `mv`, `rm`).
4. **Unknown**: check `rtk --help` before assuming subcommand exists.
