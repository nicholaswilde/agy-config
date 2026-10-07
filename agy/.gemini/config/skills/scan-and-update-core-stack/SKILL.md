# Scan & Update Core Stack Skill

Scan the current repository for tools, conventions, and patterns, then merge any new findings
into `~/.gemini/antigravity-cli/skills/core_stack.md`.

---

## Prompt

Use this verbatim (or paste into chat) when starting a new repo:

```
Scan this repository for tools, conventions, and patterns used across the project.
Look at (at minimum):

- Taskfile.yaml / Makefile / package.json scripts
- .github/workflows/*.yaml (CI tools, linters, actions used)
- pyproject.toml / Cargo.toml / go.mod / package.json (language runtimes and deps)
- dotfiles: .markdownlint*, .yamllint*, .eslintrc*, .prettierrc*, .editorconfig, etc.
- Config files: lychee.toml, _typos.toml, .sops.yaml, lefthook.yml, etc.
- .agents/skills/ (existing project skills)
- scripts/ or bin/ directories
- README or docs referencing tooling

Then:
1. Read the existing `~/.gemini/antigravity-cli/skills/core_stack.md`.
2. Identify any tools or conventions in this repo that are NOT already documented there.
3. For each new finding, add a new numbered section following the existing format:
   - Section heading: `## N. Tool Name — \`command\``
   - Bullet: what it does, when to prefer it
   - Canonical config snippet (if applicable)
   - Task/command examples
4. Do NOT duplicate or overwrite existing sections — only append or enrich them.
5. Write the updated file back to `~/.gemini/antigravity-cli/skills/core_stack.md`.
6. Report a summary table of what was added vs. what was already present.
```

---

## Protocol (agent self-execution steps)

1. **Inventory the repo** — list root files, `.github/workflows/`, `scripts/`, `docs/`, `.agents/skills/`.
2. **Read key config files** — Taskfile, pyproject.toml/Cargo.toml/go.mod, all dotfiles and linter configs.
3. **Read existing core_stack.md** — note which tools are already documented.
4. **Diff** — identify net-new tools or patterns not yet in `core_stack.md`.
5. **Write** — append new sections to `core_stack.md` following the established format. Never remove or overwrite existing sections without explicit user instruction.
6. **Report** — output a two-column summary: `Added` vs `Already Present`.
