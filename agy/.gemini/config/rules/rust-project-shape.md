# Rust Project Shape Standards

When initializing, modernizing, or structuring Rust CLI repositories (baseline: `nicholaswilde/tfa`):

1. **Root Configuration & Metadata**:
   - `build.rs`: Extracts git describe version into `PROJECT_VERSION` env and configures `rerun-if-changed` on `.git/HEAD` & `.git/refs/tags`.
   - `Taskfile.yml`: Follows `tfa` task standards (`check`, `fmt`, `lint`, `test`, `test:ci`, `build:amd64`, `build:arm64`, `build:armv7`, `build:armv6`, `coverage`, `coverage:report`, `release`, `release:summary`).
   - `.rumdl.toml`: rumdl Markdown linter configuration.
   - `.env.example`: Standard env file template (e.g. `COVERALLS_REPO_TOKEN=""`).
   - `.gitignore`: Standard Rust ignores + agent artifacts (`.codegraph/`, `.serena/`, `.rtk/*`, `!.rtk/filters.toml`).
   - `llms.txt` and `llms-full.txt`: Spec-compliant LLM context files.

2. **GitHub Actions (`.github/`)**:
   - `.github/workflows/ci.yml`: Multi-OS/cross matrix (`ubuntu`, `macos`, `windows`, `arm64`, `armv7`, `armv6`), `rustfmt`, `clippy`, `rumdl` markdownlint, Coveralls.
   - `.github/workflows/release.yml`: Release tag trigger, version match verification against `Cargo.toml`, multi-platform build via `cross`, binary archives with SHA256 sums, draft release publication.
   - `.github/CODEOWNERS` and `.github/FUNDING.yml`.

3. **Release Automation (`scripts/`)**:
   - `scripts/release.sh`: Tagging, version bumping, branch verification, atomic push.
   - `scripts/release_summary.py`: Categorized GitHub release notes generator.

4. **Agentic Layout (`.agents/` & `AGENTS.md`)**:
   - `AGENTS.md`: Architecture overview, goals, technology stack, and ponytail/caveman development principles.
   - `.agents/rules/`: Symlinks to global `agy-config` rules (`caveman-rules.md`, `no-secrets.md`, `rtk-rules.md`, `serena.md`, `taplo-rules.md`, `codegraph-rules.md`, `ponytail-rules.md`, etc.) + `<project>-project.md`.
   - `.agents/skills/`: Project-specific skills (`release`, `release-summary`).
