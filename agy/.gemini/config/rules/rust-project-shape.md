---
trigger: always_on
description: "Rust project workspace layout, formatting, and conventions"
---

# Rust Project Shape Standards

For Rust CLI repos (baseline: `nicholaswilde/tfa`):

1. **Root Config & Metadata**:
   - `build.rs`: Extract git describe version into `PROJECT_VERSION`; set `rerun-if-changed` on `.git/HEAD`, `.git/refs/tags`.
   - `Taskfile.yml`: `tfa` tasks (`check`, `fmt`, `lint`, `test`, `test:ci`, `build:amd64`, `build:arm64`, `build:armv7`, `build:armv6`, `coverage`, `coverage:report`, `release`, `release:summary`).
   - `.rumdl.toml`: rumdl Markdown lint config.
   - `.env.example`: Env template (`COVERALLS_REPO_TOKEN=""`).
   - `.gitignore`: Rust ignores + `.codegraph/`, `.serena/`, `.rtk/*`, `!.rtk/filters.toml`.
   - `llms.txt`, `llms-full.txt`: llmstxt.org context files.

2. **GitHub Actions (`.github/`)**:
   - `.github/workflows/ci.yml`: Matrix (`ubuntu`, `macos`, `windows`, `arm64`, `armv7`, `armv6`), `rustfmt`, `clippy`, `rumdl`, Coveralls.
   - `.github/workflows/release.yml`: Tag trigger, `Cargo.toml` version check, `cross` builds, archives + SHA256 sums, draft release.
   - `.github/CODEOWNERS`, `.github/FUNDING.yml`.

3. **Release Automation (`scripts/`)**:
   - `scripts/release.sh`: Tagging, version bump, branch check, atomic push.
   - `scripts/release_summary.py`: Categorized release notes generator.

4. **Agentic Layout (`.agents/`, `AGENTS.md`)**:
   - `AGENTS.md`: Architecture, goals, stack, ponytail/caveman principles.
   - `.agents/rules/`: Symlinks to global rules (`caveman-rules.md`, `no-secrets.md`, `rtk-rules.md`, `serena.md`, `taplo-rules.md`, `codegraph-rules.md`, `ponytail-rules.md`, etc.) + `<project>-project.md`.
   - `.agents/skills/`: Project skills (`release`, `release-summary`).

5. **Cross-Compiled Integration Tests (`cross`)**:
   - **Child Binary Guard**: `cross` runs tests via QEMU; `Command::new(env!("CARGO_BIN_EXE_<bin>"))` fails without `binfmt_misc`/sysroot. Preflight with `match Command::new(bin).arg("--version").output() { Ok(o) if o.status.success() => o, _ => return }` to skip gracefully.
   - **In-Process Coverage**: Test CLI flags (`Cli::try_parse_from`) in unit tests so assertions run on `cross` targets.
