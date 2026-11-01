# Antigravity CLI Config (AGENTS.md)

Entry point and operational guidelines for AI agents working in this repository.

---

## Project Overview

`agy-config` is a GNU Stow dotfiles repository managing Google Antigravity CLI (`agy`) configuration, Model Context Protocol (MCP) servers, plugins, global rules, and custom skills symlinked directly into `~/.gemini/`.

### Key Structure & File Locations

```text
.
├── agy/
│   ├── .gemini/
│   │   ├── antigravity-cli/
│   │   │   └── settings.json       # CLI permissions, trusted workspaces, model settings
│   │   └── config/
│   │       ├── config.json         # Plugin configurations
│   │       ├── mcp_config.json     # MCP server registrations (codegraph, serena, etc.)
│   │       ├── rules/              # Behavioral and security rules
│   │       └── skills/             # Custom skills library
│   └── .stow-local-ignore          # Ignores runtime and cache files from Stow
├── .gitignore                      # Git ignore rules
├── Taskfile.yml                    # Stow automation workflows
└── README.md                       # Project documentation
```

---

## Tooling & Common Workflows

This project uses [Task](https://taskfile.dev/) to orchestrate [GNU Stow](https://www.gnu.org/software/stow/) operations.

### Task Commands

- **Dry-run stow**: `task test` (tests `stow -n -S -v -t ~/ agy`)
- **Apply stow**: `task stow`
- **Dry-run restow**: `task restow:test`
- **Re-apply symlinks**: `task restow`
- **Dry-run unstow**: `task del:test`
- **Unstow / Delete symlinks**: `task del`
- **Install plugins**: `task plugins`
- **Check dirty repo**: `task notify:check`
- **Install dirty notify timer**: `task notify:install`
- **Check notify timer status**: `task notify:status`
- **Lint markdown**: `task lint:md` (`rumdl check .`)
- **Format markdown**: `task fmt:md` (`rumdl fmt .`)
- **Lint YAML**: `task lint:yaml` (`yamllint-rs .`)
- **Lint all**: `task lint`

### Git & Commit Guidelines

- **Format**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `style:`).
- **Subject length**: ≤ 50 characters, concise and lowercase imperative mood.
- **Body**: Include only when context/reasoning ("why") is non-obvious.
- **Scope**: Explicit file staging (`git add <file>`), avoid indiscriminate `git add .`.

---

<!-- rtk-begin -->
## RTK Command Guidelines

- **Git Operations**: Prefix `git` commands with `rtk` (e.g., `rtk git status`, `rtk git diff`, `rtk git log`, `rtk git commit`, `rtk git push`).
- **GitHub CLI**: Prefix `gh` commands with `rtk` and pipe to `cat` (e.g., `rtk gh issue list | cat`, `rtk gh pr status | cat`). Always pipe to bypass interactive pagers.
- **File & Directory Inspection**: Use `rtk ls`, `rtk tree`, `rtk find`, or `rtk read` when listing or reading files for token-optimized output.
- **Searching**: Use `rtk rg` or `rg` (ripgrep) for line search pattern matching to save tokens.
- **Build & Test Outputs**: Use `rtk err` or `rtk test` when running build/test commands to filter output to errors/failures only (e.g., `rtk test task test`).
- **Exceptions**: Inside `ctx_execute` / `ctx_batch_execute` sandbox code, skip `rtk` (only printed output enters context). Drop `rtk` when exact raw bytes or patch required (`git diff` patch).
<!-- rtk-end -->

<!-- context-mode-begin -->
## Context-Mode Routing Guidelines

- **Derive, Do Not Dump**: Do NOT use `ctx_execute_file` or `ctx_execute` to dump whole file or full config. Print only specific value, matches, count, or known line range needed.
- **Tool Call Surface**: When using MCP wrappers, call `call_mcp_tool` with `ServerName: "context-mode_context-mode"` (or `"context-mode"`) and `ToolName: "ctx_execute"`, `"ctx_execute_file"`, `"ctx_batch_execute"`, `"ctx_fetch_and_index"`, `"ctx_search"`, or `"ctx_index"`. Retain plugin MCP server; do not duplicate in `mcp_config.json`.
- **Mandatory Routing**:
  - For analyze/count/filter/compare/search/parse/transform tasks, write code with `ctx_execute` and print only final answer.
  - For analyzing/exploring inside file, use `ctx_execute_file`. Use native `read_file` only when editing requires exact bytes or small known range.
  - Use `ctx_batch_execute` for multi-command repository reconnaissance.
  - Use `ctx_execute` for shell commands whose output may exceed short fixed answer.
  - Use `ctx_fetch_and_index` for web content, then `ctx_search` to query it.
  - Return only derived answers, concise summaries, selected snippets, or file paths.
<!-- context-mode-end -->

<!-- ponytail-begin -->
## Ponytail (Lazy Senior Dev Mode) Guidelines

- **Stop at first rung that holds**:
  1. Need to build at all? (YAGNI)
  2. Already in codebase? Reuse existing helpers/utils/patterns.
  3. Stdlib does it? Use it.
  4. Native platform feature covers it? Use it.
  5. Installed dependency solves it? Use it.
  6. Can be one line? One line.
  7. Only then: write minimum working code.
- **Bug fix = root cause, not symptom**: Fix shared function/path rather than individual callers.
- **Rules**:
  - No unrequested abstractions, boilerplate, or avoidable dependencies.
  - Deletion over addition. Boring over clever. Fewest files possible.
  - Shortest working diff wins once problem understood.
  - Mark deliberate simplifications cutting real corner with `ponytail:` comment naming ceiling and upgrade path.
  - Ensure logic leaves behind ONE runnable check (assert-based demo/self-check or small test file). Trivial one-liners need none.
<!-- ponytail-end -->

<!-- caveman-begin -->
## Caveman Guidelines

Respond terse like smart caveman. All technical substance stay. Only fluff die.

Rules:

- Drop: articles (a/an/the), filler (just/really/basically), pleasantries, hedging.
- Fragments OK. Short synonyms. Technical terms exact. Code unchanged.
- Pattern: [thing] [action] [reason]. [next step].
- Not: "Sure! I'd be happy to help you with that."
- Yes: "Bug in auth middleware. Fix:"

Switch level: /caveman lite|full|ultra|wenyan
Stop: "stop caveman" or "normal mode"

Auto-Clarity: drop caveman for security warnings, irreversible actions, user confused. Resume after.

Boundaries: code/commits/PRs written normal.
<!-- caveman-end -->

<!-- codegraph-begin -->
## CodeGraph

In repositories indexed by CodeGraph (`.codegraph/` directory exists at repo root), reach for it BEFORE grep/find or reading files when exploring code:

- **MCP tool**: `codegraph_explore` answers source + call path + blast radius in one call. Dynamic-dispatch hops included. Name file or symbol in query to read current line-numbered source.
- **Shell**: `codegraph explore "<symbol names or question>"`.

If no `.codegraph/` directory exists, skip CodeGraph entirely.
<!-- codegraph-end -->

<!-- serena-begin -->
## Serena Semantic Navigation & LSP Integration

Use Serena (`serena`) MCP tools for semantic navigation, AST symbol inspection, LSP diagnostics, and project memories:

1. **Map first**: Call `get_symbols_overview` on target file instead of reading entire file.
2. **Read target symbol only**: Call `find_symbol` with `include_body: true` for target function/class/method.
3. **Check callers**: Call `find_referencing_symbols` or `find_implementations` before signature or behavior changes.
4. **Edit by symbol**: Use `replace_symbol_body`, `insert_after_symbol`, `insert_before_symbol`, or `rename_symbol`. Use standard edit for small tweaks or non-code files.
5. **Verify diagnostics**: Call `get_diagnostics_for_file` after edits to catch LSP errors before full test run.
<!-- serena-end -->

<!-- headroom-begin -->
## Headroom MCP (Context Window Compression)

Use Headroom (`headroom`) MCP tools to manage context window consumption on large payloads:

- `headroom_compress`: Shrink large tool outputs or raw data.
- `headroom_retrieve`: Retrieve original content by hash if specific details needed.
- `headroom_stats`: Monitor headroom cache usage.
<!-- headroom-end -->

<!-- ripgrep-guidelines-begin -->
## Ripgrep Guidelines

- **Pattern Searching**: Always use `rg` (ripgrep) or `rtk rg` instead of standard `grep` to search text inside files quickly and save token output.
- **Scope**: Keep context small (`-C 1`), use `-l` for file listing.
<!-- ripgrep-guidelines-end -->

<!-- taplo-rules-begin -->
## Taplo TOML Rules

- **Format**: Run `taplo fmt` to format TOML files in-place (`.rumdl.toml`).
- **Validation**: Run `taplo lint` to validate TOML syntax and schema.
<!-- taplo-rules-end -->

<!-- sensitive-information-protection-begin -->
## Sensitive Information & Secrets Protection

NEVER commit or stage sensitive personal, financial, or security data to repository:

1. **Secrets & Credentials**: Strictly forbid staging or committing passwords, API tokens, auth credentials, private keys (`*.pem`, `*.key`, `id_rsa`, `id_ed25519`), `.env` files, or unencrypted secrets.
2. **Sanitized Configurations**: Ensure configuration files (`settings.json`, `mcp_config.json`) contain no plaintext secrets or personal access tokens.
3. **SOPS Encryption**: Use `sops` (`task encrypt` / `task decrypt`) for encrypted secret storage.
4. **Explicit Staging**: Never use `git add .` when untracked secret files exist; stage explicitly by name.
5. **Review Before Committing**: Always inspect `git status` and staged diffs before committing.
<!-- sensitive-information-protection-end -->

<!-- issue-management-begin -->
## GitHub Issue Management

- **Commit Closing**: GitHub issues only close automatically when commits containing `Fixes #<number>` are pushed to remote repository.
<!-- issue-management-end -->

<!-- karpathy-begin -->
## Karpathy Guidelines

- **Think Before Coding**: Don't assume. Surface tradeoffs and ambiguities before acting.
- **Simplicity First**: Minimum code that solves the problem. Nothing speculative.
- **Surgical Changes**: Touch only what you must. Clean up only your own mess. Every line traces to the request.
- **Goal-Driven Execution**: Define clear success criteria and verify independently.
<!-- karpathy-end -->

<!-- design-md-begin -->
## Google DESIGN.md Specification for GUIs

When designing, scaffolding, or styling GUIs (web apps, desktop UIs, mobile apps, or component libraries), adhere to Google's [DESIGN.md](https://github.com/google-labs-code/design.md) specification:

- Check for or establish `DESIGN.md` in repository root.
- Pair machine-readable design tokens in YAML front matter (`colors`, `typography`, `spacing`, `rounded`, `components`) with human-readable rationale in Markdown body.
- Treat tokens as normative values (no arbitrary ad-hoc inline styles).
- Default to **Catppuccin Mocha** palette for color tokens unless another brand identity is requested.
- Ensure WCAG AA contrast compliance (≥ 4.5:1 ratio).
<!-- design-md-end -->
