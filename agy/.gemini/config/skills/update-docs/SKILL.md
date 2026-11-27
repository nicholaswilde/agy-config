---
name: update-docs
description: >-
  Audit and update all repository documentation: README.md, docs/ (Zensical/MkDocs if used), llms.txt, llms-full.txt, completions, and man pages.
  Trigger: /update-docs, /docs, "update docs", "update documentation", "sync docs", "update all docs", "refresh docs".
---

# Update Documentation Skill

Audit and synchronize all repository documentation surfaces so prose, examples, navigation, LLM indexes, and generated CLI docs match the current codebase.

## Protocol

### 1. Discover Documentation & Source of Truth

Inspect what exists in the repository before editing:

- **Doc files**: `README.md`, `docs/README.md`, `docs/*.md`, `zensical.toml`, `mkdocs.yml`, `llms.txt`, `llms-full.txt`, `AGENTS.md`, `assets/config.example.toml`, `completions/`, `assets/*.1`.
- **Source of truth**: Inspect manifests (`Cargo.toml`, `pyproject.toml`, `package.json`, `go.mod`), `Taskfile.yml`, recent `rtk git log -n 10 --oneline`, and `rtk git status --short`. For CLI tools, inspect live `--help` output for top-level and subcommands. Never guess or fabricate flags, env vars, or commands.

### 2. Update `README.md` & `docs/` (Zensical / MkDocs / Static Sites)

Update only the documentation surfaces present in the repo while preserving each format's syntax boundary:

- **GitHub-Flavored Markdown** (`README.md`, `docs/README.md`): Follow `readme-style` conventions where applicable (`> [!WARNING]`, `> [!NOTE]`, shields.io badges).
- **Zensical / MkDocs Markdown** (`docs/*.md` when `zensical.toml` or `mkdocs.yml` is present): Preserve admonitions (`!!! note`, `!!! warning`), tabs (`=== "Label"`), and emoji shortcodes.
- **Pages to audit**: `README.md`, `docs/index.md`, `docs/usage.md`, `docs/about.md`, `docs/configuration.md`, `docs/security.md`, `docs/installation.md`, `docs/CONTRIBUTING.md`.
- **Site navigation**: Verify `zensical.toml` or `mkdocs.yml` `nav` entries match existing `docs/` files.

### 3. Regenerate `llms.txt` & `llms-full.txt`

When `llms.txt` or `llms-full.txt` exist (or are requested), regenerate them per the `generate-llms-txt` (`llmstxt.org`) specification:

- **`llms.txt`**:
  - Single `# <Project>` H1 on line 1, immediate `>` summary blockquote, concise preamble paragraph (no subheadings).
  - `##` category sections using `- [Title](path): Description` items only (no `###+` headings; verify every relative path exists on disk).
  - End with `## Optional`.
- **`llms-full.txt`**:
  - Self-contained Markdown reference with TOC, installation, global options, full CLI/API reference, configuration/security, architecture layout, dev/test workflows, and license/maintainer info.

### 4. Sync Generated Artifacts & `AGENTS.md`

- **CLI Completions & Man Page**: When CLI flags or subcommands changed and `Taskfile.yml` defines `completions` / `man`, run `task completions && task man`.
- **`AGENTS.md`**: Update stale module lists, commands, or quality-gate descriptions in caveman-compressed style.

### 5. Verify Documentation Gates

Run applicable checks in one pass:

1. **Markdown lint**: `task lint:md` (or `rtk rumdl check .`) — 0 issues.
2. **Static site build** (if `zensical.toml` / `mkdocs.yml` exists): `task docs:build` (or `rtk uv run zensical build --clean`) — 0 errors; confirm `site/` remains gitignored.
3. **Config lint** (if TOML/YAML touched): `rtk taplo fmt --check`, `rtk taplo lint`, `yamllint-rs`.
4. **`llms.txt` validation**: Confirm single H1, immediate blockquote, no `###+` headings, valid `- [Title](path): Description` links pointing to existing files, and `## Optional` last.
5. **Working tree check**: `rtk git status --short` — confirm only expected documentation/generated files changed and no secrets or stray build outputs exist.

### 6. Guardrails

- Do **not** commit or push changes unless the user explicitly asks.
