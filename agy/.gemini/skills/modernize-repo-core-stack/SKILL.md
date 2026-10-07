# Modernize Repo to Core Stack Skill

Scan the current repository for tools, conventions, and configuration files, compare them against the standards in `~/.gemini/antigravity-cli/skills/core_stack.md`, and recommend/apply updates to use modern tools (e.g., converting `shellcheck` to `shuck`, `make` to `go-task`, etc.).

---

## Prompt

Use this verbatim (or paste into chat) to audit and modernize an existing repository:

```
Analyze this repository's tooling, scripts, and CI/CD workflows, then compare them against the core stack standards in `~/.gemini/antigravity-cli/skills/core_stack.md`.

Provide a detailed modernization report and recommendations, specifically looking for:
1. Legacy build tools (Makefile, package.json scripts) to convert to `go-task`.
2. Bash scripts and shell linters (converting `shellcheck` or unlinted scripts to `shuck` and standard Bash boilerplate).
3. Dependency management (converting legacy tools to `uv` for Python).
4. Linters and formatting (converting markdown/yaml linters to `rumdl` and `yamllint-rs`).
5. Other tooling (typos, lychee, sops, zensical).

For each modernization finding, suggest the exact changes needed (CI workflows, configs, scripts) and offer to apply them.
```

---

## Protocol (agent self-execution steps)

1. **Load core stack standards** — Read `~/.gemini/antigravity-cli/skills/core_stack.md` to get the list of active tool standards and configurations.
2. **Inventory the repository** — Scan the repository root files, `.github/workflows/`, `scripts/`, `bin/`, dotfiles, and main configuration files.
3. **Audit and Compare**:
   - **Task Management**: Look for `Makefile`, `Justfile`, or `package.json` scripts. Recommend converting to `Taskfile.yaml`.
   - **Bash Scripting**:
     - Look for shell scripts (`*.sh`).
     - Check if `shellcheck` is used in GitHub Actions workflows or local lint scripts.
     - Recommend replacing `shellcheck` with `shuck`.
     - Recommend updating shell scripts to use the standard header, `set -e`, `set -o pipefail`, `main "$@"` wrapper, and Catppuccin color logging.
   - **Python Tooling**: Look for `requirements.txt`, `Pipfile`, or `poetry.lock`. Recommend `uv`.
   - **Linters**:
     - Check for `markdownlint-cli` or similar and recommend `rumdl`.
     - Check for `yamllint` and recommend `yamllint-rs`.
   - **CI/CD**: Scan `.github/workflows/*.yaml` for outdated GitHub Action versions or tasks that should run through `go-task`.
4. **Generate Report** — Write a markdown artifact `modernization_report.md` detailing:
   - **Identified Legacy Tools**: Current tool setup.
   - **Recommended Core Stack Replacement**: The modern alternative from `core_stack.md`.
   - **Required Configuration Files**: e.g., `.yamllint`, `.markdownlint.yaml`, `_typos.toml`, `Taskfile.yaml`.
   - **Action Plan**: Detailed step-by-step conversion tasks.
5. **Apply Conversions** — Upon user approval, implement the configuration files, rewrite scripts, and update the CI/CD workflows.
