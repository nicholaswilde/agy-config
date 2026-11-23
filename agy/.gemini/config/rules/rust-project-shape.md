---
trigger: always_on
description: "Rust project workspace layout, formatting, and conventions"
---

# Rust Project Shape Standards

For Rust CLI repos (baseline: `nicholaswilde/tfa`):

1. **Root Config & Metadata**:
   - `build.rs`: Git describe -> `PROJECT_VERSION`; `rerun-if-changed` on `.git/HEAD`, `.git/refs/tags`.
   - `Taskfile.yml`: `tfa` tasks (`check`, `fmt`, `lint`, `test`, `test:ci`, `build:{amd64,arm64,armv7,armv6}`, `coverage{,:report}`, `release{,:summary}`).
   - `.rumdl.toml`: Markdown lint config.
   - `.env.example`: `COVERALLS_REPO_TOKEN=""`.
   - `.gitignore`: Rust ignores + `.codegraph/`, `.serena/`, `.rtk/*`, `!.rtk/filters.toml`.
   - `llms.txt`, `llms-full.txt`: llmstxt.org files.

2. **GitHub Actions (`.github/`)**:
   - `.github/workflows/ci.yml`: Matrix (`ubuntu`, `macos`, `windows`, `arm64`, `armv7`, `armv6`), `rustfmt`, `clippy`, `rumdl`, Coveralls.
   - `.github/workflows/release.yml`: Tag trigger, `Cargo.toml` check, `cross` builds, archives + SHA256, draft -> `publish-release` (`gh release edit ${{ github.ref_name }} --draft=false --prerelease=false --repo ${{ github.repository }}`) after `build-release`; `update-homebrew-tap`/`update-scoop-bucket` MUST need `['create-release', 'publish-release']` (drafts 404 on `/releases/tags/{tag}`).
   - `.github/CODEOWNERS`, `.github/FUNDING.yml`.

3. **Release Automation (`scripts/`)**:
   - `scripts/release.sh`: Tag, version bump, branch check, atomic push.
   - `scripts/release_summary.py`: Categorized notes; edit in-place without forcing `--draft` (`--draft`/`--prerelease` opt-in so published releases stay published).

4. **Agentic Layout (`.agents/`, `AGENTS.md`)**:
   - `AGENTS.md`: Architecture, goals, stack, ponytail/caveman.
   - `.agents/rules/`: Global rule symlinks (`caveman-rules`, `no-secrets`, `rtk-rules`, `serena`, `taplo-rules`, `codegraph-rules`, `ponytail-rules`, etc.) + `<project>-project.md`.
   - `.agents/skills/`: `release`, `release-summary`.

5. **Cross-Compiled Integration Tests (`cross`)**:
   - **Child Binary Guard**: `cross`/QEMU fails `Command::new(env!("CARGO_BIN_EXE_<bin>"))` without `binfmt_misc`/sysroot; preflight `match Command::new(bin).arg("--version").output() { Ok(o) if o.status.success() => o, _ => return }`.
   - **In-Process Coverage**: Test CLI flags (`Cli::try_parse_from`) in unit tests for `cross` targets.
