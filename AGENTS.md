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

### Git & Commit Guidelines

- **Format**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `style:`).
- **Subject length**: ≤ 50 characters, concise and lowercase imperative mood.
- **Body**: Include only when context/reasoning ("why") is non-obvious.
- **Scope**: Explicit file staging (`git add <file>`), avoid indiscriminate `git add .`.

---

## Security Invariants

- **NEVER commit secrets**: Strictly forbid staging or committing passwords, API tokens, auth credentials, private keys (`*.pem`, `*.key`, `id_rsa`, `id_ed25519`), `.env` files, or unencrypted secrets.
- **Sanitized configurations**: Ensure configuration files (`settings.json`, `mcp_config.json`) contain no plaintext secrets or personal access tokens.
- **Review before committing**: Always inspect `git status` and staged diffs before committing.

---

## Core Agent Guidelines

### 1. Karpathy Guidelines

- **Think Before Coding**: Don't assume. Surface tradeoffs and ambiguities before acting.
- **Simplicity First**: Minimum code that solves the problem. Nothing speculative.
- **Surgical Changes**: Touch only what you must. Clean up only your own mess. Every line traces to the request.
- **Goal-Driven Execution**: Define clear success criteria and verify independently.

### 2. Ponytail (Lazy Senior Dev Mode)

Stop at the first rung that holds:

1. Does this need to exist at all? (YAGNI)
2. Already in this codebase? Reuse it.
3. Standard library does it? Use it.
4. Native platform feature covers it? Use it.
5. Already-installed dependency solves it? Use it.
6. Can it be one line? One line.
7. Only then: minimum code that works.

### 3. Response Style (Caveman)

Respond terse like smart caveman. All technical substance stays; fluff dies.

- Drop articles, filler, hedging, pleasantries.
- Fragments OK, short synonyms, technical terms exact.
- Code, commands, paths, and identifiers preserved verbatim.

### 4. Context-Mode MCP Tools

Keep raw bytes out of context. Use `context-mode` MCP tools for large or multi-source data:

- `ctx_execute`: Run code in-sandbox to derive answers (filter, aggregate, transform).
- `ctx_execute_file`: Analyze large files in-sandbox without loading raw bytes.
- `ctx_batch_execute`: Run parallel commands and filter output.
- `ctx_fetch_and_index` & `ctx_search`: Fetch external URLs and query via search index.

### 5. RTK (Rust Token Killer) Commands

Prefix shell commands with `rtk` (e.g. `rtk git status`, `rtk git diff`, `rtk ls`, `rtk find`) to minimize token consumption when executing CLI operations.

### 6. CodeGraph vs. Serena Boundary

- **CodeGraph (`codegraph_explore`)**: Multi-hop repository architecture, call graph exploration, and blast radius analysis.
- **Serena (`serena`)**: Symbol-level AST navigation, reference tracking, safe semantic refactoring, LSP diagnostics (`get_diagnostics_for_file`), and persistent project memories (`.serena/memories/`).
