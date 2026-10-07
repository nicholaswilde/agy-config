# :gear: Antigravity CLI Config :robot:

[![task](https://img.shields.io/badge/Task-Enabled-brightgreen?style=for-the-badge&logo=task&logoColor=white)](https://taskfile.dev/#/)
[![license](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge)](LICENSE)

GNU Stow dotfiles package for managing Google Antigravity CLI (`agy`) configuration, MCP servers, plugins, global rules, and custom skills.

---

## :sparkles: Features

- **Dotfiles Management via GNU Stow**: Clean symlinking directly into `~/.gemini/`.
- **MCP Server Configurations**: Preconfigured integration for `codegraph`, `docker-hub`, `context-mode`, and `serena`.
- **Curated Skills Library**: Bundled custom skills including `caveman`, `cavecrew`, `core-stack`, `setup-serena`, and network diagnostics.
- **Rule Enforcement**: Built-in rules for secret management, credential leak prevention, and semantic coding.
- **Automated Workflows**: Streamlined `Taskfile` commands for safe dry-runs, stowing, restowing, and removal.

---

## :package: Installation

### Prerequisites

- [GNU Stow](https://www.gnu.org/software/stow/)
- [Task](https://taskfile.dev/)

### Setup

Clone the repository:

```bash
git clone git@github.com:nicholaswilde/agy-config.git ~/git/nicholaswilde/agy-config
cd ~/git/nicholaswilde/agy-config
```

---

## :rocket: Usage

Run stow operations using [Task](https://taskfile.dev/):

### Dry Run (Test)

Test stowing without making actual filesystem changes:

```bash
task test
```

### Stow Configuration

Symlink the `agy` package into `~/`:

```bash
task stow
```

### Restow Configuration

Re-link and refresh existing symlinks:

```bash
task restow
```

To test restowing first:

```bash
task restow:test
```

### Remove Symlinks

Unstow and remove created symlinks:

```bash
task del
```

To test removal first:

```bash
task del:test
```

### Install Plugins

Install bundled Gemini / Antigravity plugins (`ponytail`, `caveman`, and `context-mode`):

```bash
task plugins
```

---

## :file_folder: Repository Structure

```text
.
├── agy/
│   ├── .gemini/
│   │   ├── antigravity-cli/
│   │   │   └── settings.json       # Permissions, trusted workspaces, and model settings
│   │   ├── config/
│   │   │   ├── config.json         # Plugin configurations
│   │   │   └── mcp_config.json     # Model Context Protocol (MCP) server definitions
│   │   ├── rules/                  # Behavioral and security rules
│   │   └── skills/                 # Custom skills library
│   └── .stow-local-ignore          # Ignores runtime and cache directories from Stow
├── .gitignore                      # Git ignore patterns
├── LICENSE                         # Apache 2.0 License
├── README.md                       # Project documentation
└── Taskfile.yml                    # Task automation definitions
```

---

## :balance_scale: License

​[Apache License 2.0](LICENSE)

---

## :writing_hand: Author

​This project was started in 2026 by [Nicholas Wilde][2].

[2]: <https://github.com/nicholaswilde/>
