# :gear: Antigravity CLI Config :robot:

[![task](https://img.shields.io/badge/Task-Enabled-brightgreen?style=for-the-badge&logo=task&logoColor=white)](https://taskfile.dev/#/)
[![ci](https://img.shields.io/github/actions/workflow/status/nicholaswilde/agy-config/ci.yml?label=ci&style=for-the-badge&branch=main&logo=github-actions)](https://github.com/nicholaswilde/agy-config/actions/workflows/ci.yml)
[![license](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge)](LICENSE)

[enstow](https://github.com/nicholaswilde/enstow) dotfiles package for managing Google Antigravity CLI (`agy`) configuration, MCP servers, plugins, global rules, and custom skills.

---

## :sparkles: Features

- **Dotfiles Management via enstow**: Per-file symlinking directly into `~/.gemini/` with built-in `age` secret support, drift status, and health diagnostics.
- **MCP Server Configurations**: Preconfigured integration for `codegraph`, `docker-hub`, `context-mode`, and `serena`.
- **Curated Skills Library**: Bundled custom skills including `caveman`, `cavecrew`, `core-stack`, `design-md`, `setup-serena`, and network diagnostics.
- **Rule Enforcement**: Built-in rules for secret management, credential leak prevention, Google `DESIGN.md` GUI standards, and semantic coding.
- **Automated Workflows & CI**: Streamlined `Taskfile` commands for safe dry-runs, applying, restowing, diagnostics (`status`, `diff`, `doctor`), and linting (`rumdl`, `yamllint`) backed by GitHub Actions CI.
- **Design & Theming Standards**: Native Catppuccin Mocha theme defaults and 2-space indentation standards across all tools.
- **Dirty Repo Notifications**: systemd user timer alerts via [Mailrise](https://github.com/YoRyan/mailrise) when config changes are uncommitted or unpushed.

---

## :package: Installation

### Prerequisites

- [enstow](https://github.com/nicholaswilde/enstow)
- [Task](https://taskfile.dev/)

### Setup

Clone the repository and verify `enstow`:

```bash
git clone git@github.com:nicholaswilde/agy-config.git ~/git/nicholaswilde/agy-config
cd ~/git/nicholaswilde/agy-config
task deps
```

---

## :rocket: Usage

> [!NOTE]
> Migrating a host previously stowed with GNU Stow? `enstow apply --backup` (via `task apply -- --backup`) automatically unfolds legacy folded directory symlinks, prunes stale links, and backs up conflicting targets to `~/.enstow-backup/<timestamp>`.

Run operations using [Task](https://taskfile.dev/) (or invoke `enstow` directly from repository root, where [`.enstow.toml`](./.enstow.toml) is auto-discovered with `prune = true` and `mask_secrets = true`):

### Dry Run (Test)

Preview applying `agy` without making filesystem changes:

```bash
task test
```

### Apply Configuration

Symlink the `agy` package into `~/` (aliases: `task stow`, `task install`):

```bash
task apply
```

### Restow Configuration

Prune stale symlinks and re-apply the `agy` package:

```bash
task restow
```

To preview restowing first:

```bash
task restow:test
```

### Remove Symlinks

Unstow and remove managed symlinks (aliases: `task del`, `task delete`):

```bash
task unstow
```

To preview removal first (alias: `task del:test`):

```bash
task unstow:test
```

### Status, Diff & Doctor

Inspect symlink state (`-- --check` exits non-zero on drift), view masked diffs, audit symlink/secret hygiene, and guard staged commits:

```bash
task status
task status -- --check
task diff
task doctor
task check-secrets
task install-hooks
```

### Install Plugins

Install bundled Gemini / Antigravity plugins (`ponytail`, `caveman`, and `context-mode`):

```bash
task plugins
```

### Lint Markdown

Lint repository Markdown files with [rumdl](https://github.com/rvben/rumdl):

```bash
task lint:md
```

### Format Markdown

Auto-format repository Markdown files and fix lint violations:

```bash
task fmt:md
```

### Lint YAML

Lint repository YAML files with [yamllint-rs](https://github.com/kaleidawave/yamllint-rs):

```bash
task lint:yaml
```

### Lint All

Run both Markdown and YAML linting checks:

```bash
task lint
```

### Dirty Repo Notifications

Periodic uncommitted change detection via systemd user timer with [Mailrise](https://github.com/YoRyan/mailrise) alerts.
[`notify-dirty.sh`](scripts/notify-dirty.sh) sends an SMTP email to Mailrise (via `curl`), which forwards it to any
[Apprise](https://github.com/caronc/apprise) target (Gotify, ntfy, Discord, etc.).

- Detects uncommitted/untracked changes to skills, rules, and config files, plus unpushed commits.
- Notifies once per dirty period; state resets when repo is clean and synced with upstream.

1. Copy `.env.example` to `.env` (git-ignored) and adjust configuration (e.g. `NOTIFY_MODE=dirty`, `both`, or `disabled`):

   ```bash
   cp .env.example .env
   ```

2. Run dirty check manually:

   ```bash
   task notify:check
   ```

   Send a test notification regardless of repo state:

   ```bash
   task notify:check -- --force
   ```

3. Install and activate user timer (every 15 minutes):

   ```bash
   task notify:install
   ```

4. Check timer and service status:

   ```bash
   task notify:status
   ```

5. Remove timer and service:

   ```bash
   task notify:uninstall
   ```

#### Configuration

| Variable            | Default                                                   | Description                                        |
|---------------------|-----------------------------------------------------------|----------------------------------------------------|
| `MAILRISE_URL`      | `smtp://smtp.l.nicholaswilde.io:8025`                     | Mailrise SMTP endpoint                             |
| `MAILRISE_TO`       | `all@mailrise.xyz`                                        | Mailrise target (defined in `mailrise.yaml`)       |
| `MAILRISE_FROM`     | `agy-config@<hostname>`                                   | Sender address                                     |
| `MAILRISE_USER`     | _(empty)_                                                 | Optional SMTP username                             |
| `MAILRISE_PASSWORD` | _(empty)_                                                 | Optional SMTP password (keep in `.env` only)       |
| `NOTIFY_MODE`       | `dirty`                                                   | `dirty`, `both` (also notify when clean), `disabled` |
| `CHECK_ALL_FILES`   | `false`                                                   | `true` alerts on any uncommitted file              |
| `TARGET_REGEX`      | `skills/\|rules/\|settings\.json\|config\.json\|mcp_config\.json` | Paths watched when `CHECK_ALL_FILES=false` |
| `STATE_FILE`        | `$XDG_STATE_HOME/agy-config/dirty.state`                  | Tracks whether notification was already sent       |

Precedence: caller environment > `.env` > script default.

---

## :file_folder: Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI workflow
├── agy/
│   ├── .gemini/
│   │   ├── antigravity-cli/
│   │   │   └── settings.json   # Permissions, trusted workspaces, and model settings
│   │   └── config/
│   │       ├── config.json     # Plugin configurations
│   │       ├── mcp_config.json # Model Context Protocol (MCP) server definitions
│   │       ├── rules/          # Behavioral and security rules
│   │       └── skills/         # Custom skills library
│   └── .enstowignore           # Git-style ignore patterns for enstow
├── scripts/
│   └── notify-dirty.sh         # Dirty check & Mailrise notification script
├── systemd/
│   ├── agy-dirty-notify.service # systemd user service definition
│   └── agy-dirty-notify.timer   # systemd user timer definition (15m interval)
├── .enstow.toml                # enstow package registry and recipients config
├── .env.example                # Notification and Mailrise environment template
├── .gitignore                  # Git ignore patterns
├── .rumdl.toml                 # Markdown linter and formatter configuration
├── .yamllint                   # YAML linter configuration
├── AGENTS.md                   # Operational guidelines for AI coding agents
├── LICENSE                     # Apache 2.0 License
├── README.md                   # Project documentation
└── Taskfile.yml                # Task automation definitions
```

---

## :balance_scale: License

​[Apache License 2.0](LICENSE)

---

## :writing_hand: Author

​This project was started in 2026 by [Nicholas Wilde][2].

[2]: <https://github.com/nicholaswilde/>
