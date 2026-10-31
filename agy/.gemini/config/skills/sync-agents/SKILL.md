---
name: sync-agents
description: >-
  Audit and synchronize repo AGENTS.md, .agents/rules, and .agents/skills with global rules, symlinks, and skills catalog.
  Trigger: /sync-agents, /update-agents, "sync agents", "update agents", "update AGENTS.md", "sync agent rules", "update skills and rules".
---

# Sync Agents Skill

Audit and synchronize a repository's `AGENTS.md`, `.agents/rules/`, and `.agents/skills/` against Antigravity global standards, rule symlinks, and skills catalog requirements.

## Protocol

### 1. AGENTS.md Audit & Alignment

Inspect repository root `AGENTS.md`:

1. **Verify Core Tooling Blocks**:
   Ensure tagged blocks exist with current specifications:
   - `<!-- rtk-begin -->` — RTK command proxy (`rtk git`, `rtk gh ... | cat`, `rtk ls`, `rtk rg`, `rtk test`, `rtk err`; sandbox exception: skip `rtk` inside `ctx_execute` / `ctx_batch_execute`).
   - `<!-- context-mode-begin -->` — In-sandbox derivation (`ctx_execute`, bounded routing via `context-mode_context-mode`). Retain plugin MCP server; do not duplicate in `mcp_config.json`.
   - `<!-- ponytail-begin -->` — YAGNI, 7-rung minimalism, root cause over symptom.
   - `<!-- caveman-begin -->` — Terse communication style.
   - `<!-- codegraph-begin -->` — CodeGraph index check (`.codegraph/`).
   - `<!-- serena-begin -->` — Serena MCP symbol navigation (`get_symbols_overview`, `find_symbol`, `get_diagnostics_for_file`).
   - `<!-- headroom-begin -->` — Headroom MCP context compression (`headroom_compress`).
   - `<!-- ripgrep-guidelines-begin -->` — Pattern search via `rtk rg`.
   - `<!-- taplo-rules-begin -->` — TOML formatting & linting (`taplo fmt`, `taplo lint` for TOML projects).
   - `<!-- sensitive-information-protection-begin -->` — Secret commit prevention, SOPS encryption (`task encrypt`), no blanket staging.
2. **Preserve Project Rules**:
   Retain and update project-specific blocks (APIs, hardware, workflows, TDD, format conventions).
3. **Caveman Style**:
   Keep prose terse; preserve exact code blocks, paths, CLI commands, and comment tags verbatim.
4. **Issue Closing Rule**:
   Ensure GitHub auto-close requirement is documented: commits must contain `Fixes #<number>`.

### 2. Rules Audit & Symlinking (`.agents/rules/`)

Ensure `.agents/rules/` directory exists and aligns with global standards:

1. **Remove Obsolete Rules**:
   Remove deprecated or static copies superseded by global rules (e.g. legacy `antigravity-rtk-rules.md`, `serena-rules.md`, `context-mode-rules.md` — context-mode routing belongs in `AGENTS.md`).
2. **Symlink Relevant Global Rules**:
   Create symbolic links pointing to `/home/nicholas/git/nicholaswilde/agy-config/agy/.gemini/config/rules/<rule>.md`:
   - `rtk-rules.md` (universal)
   - `serena.md` (codebases using AST/LSP)
   - `github-cli-rules.md` (universal)
   - `ripgrep-rules.md` (universal)
   - `no-secrets.md` (universal)
   - `caveman-rules.md` (universal)
   - `uv-rules.md` (Python projects)
   - `taplo-rules.md` (TOML configs present)
   - `design-md-rules.md` (frontend/GUI projects)
3. **Project-Specific Rules**:
   Retain or create dedicated project rule files (e.g. `.agents/rules/<project>-rules.md`).

### 3. Skills Audit & Maintenance (`.agents/skills/`)

Review all skill definitions in `.agents/skills/*/SKILL.md`:

1. **Frontmatter Hygiene**:
   Verify YAML frontmatter contains valid `name:` and `description:` under 380 chars with trigger phrases.
2. **Missing Skills**:
   Audit recent tasks, scripts, or workflows added to the repository. Create missing skills with standard frontmatter, guidelines, and execution examples.
3. **Task & Commit Accuracy**:
   - Ensure skill instructions reference proper Taskfile tasks (`task <name>`).
   - Ensure commit examples use exact auto-closing syntax: `Fixes #<number>`.
   - Add pre-attachment image optimization steps if processing images.

### 4. Skills Catalog Maintenance (`.agents/skills_catalog.md`)

Maintain a comprehensive catalog at `.agents/skills_catalog.md`:

1. Scan all `.agents/skills/*/SKILL.md`.
2. Generate or update Markdown table:
   - Columns: `Skill`, `Description`, `Task / Command`.
   - Link each skill to its relative path: `[`skill-name`](skills/skill-name/SKILL.md)`.

### 5. Repository Hygiene (`.gitignore`)

Verify `.gitignore` rules:

1. Whitelist rules and skills:

   ```gitignore
   .agents/*
   !.agents/skills/
   !.agents/rules/
   !.agents/skills_catalog.md
   ```

2. Whitelist `.rtk` filters:

   ```gitignore
   .rtk/*
   !.rtk/filters.toml
   ```

3. Ensure `.codegraph/` and `.serena/` caches are ignored.

### 6. Verification & Commit

1. Run test suite to verify no regressions (`task test` or `uv run pytest`).
2. Check `rtk git status`.
3. Explicitly stage modified files.
4. Commit using Conventional Commits:

   ```bash
   git commit -m "chore: align .agents/ rules, skills, and AGENTS.md with global standards"
   ```
