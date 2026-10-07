# Core Stack & Workflow Standards

You are assisting with repositories that strictly adhere to the following technology stack.
Whenever you write code, generate configuration files, or suggest shell commands, you must
default to these tools and conventions.

---

## 1. Task Management — `go-task`

* **NEVER** generate or suggest `Makefile`, `package.json` scripts, or standalone bash scripts for build/run steps.
* **ALWAYS** default to [`go-task`](https://taskfile.dev) (Taskfile v3).
* Generate and update `Taskfile.yaml` for all routine actions: build, test, lint, deploy, encrypt/decrypt.
* Use `task -a` (default task) to list all available tasks.
* Pass file arguments with `FILES=` or `FILE=` vars (`task commit FILES="path/to/file"`).
* Use `shellQuote` to safely quote arguments: `{{shellQuote .FILE}}`.
* Use `sh: git rev-parse --show-toplevel` to resolve `ROOT_DIR` dynamically.

## 2. Binary Executables — Rust

* All new standalone binaries, daemons, or heavy CLI tools must be written in Rust.
* Standard Cargo layout: `src/main.rs`, `Cargo.toml`.
* Always include `cargo clippy -- -D warnings` in build/test steps.

## 3. Python Tooling — `uv`

* Use [`uv`](https://github.com/astral-sh/uv) for all Python dependency management (never `pip` directly at the project level).
* Install deps with `uv pip install <package>`.
* Project metadata lives in `pyproject.toml` with `requires-python` pinned.
* Lock file: `uv.lock`.

## 4. YAML Linting — `yamllint-rs`

* When verifying, formatting, or creating YAML files (CI/CD, Docker, Taskfiles), assume `yamllint-rs` is the global linter.
* Config file: `.yamllint` at repo root.
* Run via task: `task yamllint` → `yamllint-rs .`
* Canonical config:
  ```yaml
  extends: default
  ignore: |
    **/.github/**
  rules:
    indentation: disable
    line-length:
      max: 120
      level: warning
    truthy:
      allowed-values: ['true', 'false', 'yes', 'no']
  ```

## 5. Markdown Linting — `rumdl`

* Use [`rumdl`](https://github.com/nicholaswilde/rumdl) for markdown linting (not `markdownlint-cli`).
* Config file: `.markdownlint.yaml` at repo root.
* Run via task: `task markdownlint` → `rumdl check .`
* Auto-fix: `task markdownlint-fix` → `rumdl check --fix .`
* Canonical config:
  ```yaml
  MD007:
    indent: 4
  MD013:
    line_length: 120
    code_blocks: false
    tables: false
  MD024:
    allow_different_nesting: true
    siblings_only: true
  MD046: false
  ```

## 6. Spellcheck — `typos`

* Use [`typos-cli`](https://github.com/crate-ci/typos) for spellchecking.
* Config file: `_typos.toml` (auto-generated; do NOT hand-edit).
* Custom dictionary: `dictionary.txt` (one word per line, sorted alphabetically).
* Always regenerate config before running: `python3 scripts/generate_typos_config.py && typos`.
* Use focused checks: `task spellcheck-file FILE=path/to/file` rather than global `task spellcheck`.
* Sort dictionary after additions: `task sort` → `sort dictionary.txt -u -o dictionary.txt`.
* CI uses [`crate-ci/typos@v1`](https://github.com/crate-ci/typos) GitHub Action.

## 7. Link Checking — `lychee`

* Use [`lychee`](https://github.com/lycheeverse/lychee) for dead link detection.
* Config file: `lychee.toml` at repo root.
* Run via task: `task linkcheck` (online), `task linkcheck-offline`, or `task linkcheck-file FILE=path`.
* Accept 403/429/520 status codes as valid (anti-scraper/rate-limit false positives).
* CI uses [`lycheeverse/lychee-action@v2`](https://github.com/lycheeverse/lychee-action) on a daily cron schedule.
* Canonical config keys:
  ```toml
  timeout = 5
  max_retries = 2
  max_concurrency = 20
  accept = [200, 201, 202, 204, 206, 403, 405, 429, 520]
  exclude_all_private = true
  ```

## 8. Secrets Encryption — `sops`

* Use [`sops`](https://github.com/mozilla/sops) to encrypt sensitive files (MCP config, `.env`, etc.).
* Config file: `.sops.yaml` at repo root — specifies PGP + age keys.
* **NEVER commit** `.env`, `mcp_config.json`, `settings.json`, or any file with secrets/passwords unencrypted.
* Encrypt: `task encrypt` / Decrypt: `task decrypt`.
* Encrypted files use `.enc` suffix (e.g. `mcp_config.json.enc`).
* Canonical `.sops.yaml`:
  ```yaml
  creation_rules:
    - filename_regex: (\.ya?ml|\.db|\.env|\.json|\.ini|\.toml)$
      pgp: '<PGP_FINGERPRINT>'
      age: '<AGE_PUBLIC_KEY>'
  ```

## 9. YAML Processing — `yq`

* Use [`yq`](https://github.com/mikefarah/yq) for reading/writing YAML (including front matter in markdown).
* For front-matter in markdown: `yq --front-matter="process" '.key = "value"' file.md`
* For in-place edits: `yq -i` flag.
* For sorted keys: `yq -i 'sort_keys(.)'`.

## 10. GitHub CLI — `gh`

* **Always** use `gh` when interacting with the remote repository (e.g., cloning, managing issues/PRs, monitoring workflows).
* **Always** pipe all `gh` commands to `cat` to bypass interactive paging, prompts, and other user interactions: `gh <command> | cat`
* Key commands:
  ```bash
  gh repo clone <owner>/<repo> | cat    # clone a remote repository
  gh pr list | cat                      # list pull requests
  gh pr create | cat                    # create a pull request without interactive prompt
  gh run list --limit 10 | cat          # recent workflow runs
  gh run view <run-id> | cat            # details of a specific run
  gh run view --log --job=<job-id> | cat  # full logs for a failed job
  gh issue list | cat                   # open issues
  gh issue close <number>               # close an issue
  ```
* GitHub issues **only close automatically** when commits containing `Fixes #<number>` are pushed to the remote.

## 11. Conventional Commits

* All commits follow [Conventional Commits](https://www.conventionalcommits.org/) format:
  ```
  <type>: <description>. Fixes #<issue>
  ```
* Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `ci`, `style`.
* Use `git filter-branch` or interactive `git rebase -i` to rewrite generic messages (e.g. "update") to descriptive ones.

## 12. GitHub Actions Patterns

* Workflows live in `.github/workflows/`.
* Always pin action versions (e.g. `actions/checkout@v6`).
* Use `concurrency` groups with `cancel-in-progress: true` on PR/push workflows.
* Use `workflow_dispatch` to allow manual re-runs.
* Use path-filtered triggers (`paths:`) to avoid unnecessary runs.
* Scheduled maintenance workflows (e.g. weekly image optimization via Jules) use cron expressions.

## 13. Agent Skills — `.agents/`

* Project-specific agent skills live in `.agents/skills/<skill-name>.md`.
* Global/reusable skills live in `~/.gemini/antigravity-cli/skills/`.
* **Skills Catalog**: Every repository with custom agent skills should maintain a `.agents/skills_catalog.md` detailing the commands, their usage syntax, dependencies, and behavior. This catalog must be linked in the project context index (e.g., `conductor/index.md`) to make it easily discoverable.
* Skill files must start with a YAML front-matter block (optional) or an H1 heading.
* Skill sections: `## Description`, `## Protocol` (numbered steps), `## Examples`.
* Consult `.agents/skills/scripts-registry.md` or the skills catalog before writing new automation — prefer existing scripts and custom commands.

## 14. Document Parsing — LiteParse

* For parsing unstructured files (PDF, DOCX, PPTX, XLSX, images) locally, use the `liteparse` skill.
* Install: `npm i -g @llamaindex/liteparse`; CLI: `lit parse <file>`.
* No cloud dependencies or LLM required.
* See `.agents/skills/liteparse.md` for full options reference.

## 15. Documentation Site — `zensical`

* Use [`zensical`](https://github.com/nicholaswilde/zensical) as the static site generator (a MkDocs/Material wrapper).
* Config file: `zensical.toml` at repo root (replaces `mkdocs.yml`).
* Build: `uvx zensical build` or `task build`.
* Serve locally: `uvx zensical serve --dev-addr 0.0.0.0:8000` or `task serve` / `task up`.
* Install/update via `uv`: `uv pip install zensical` / `uv pip install --upgrade zensical`.
* Nav is declared as `[[project.nav]]` TOML array-of-tables in `zensical.toml`; auto-generate with `task generate-docs-nav`.
* CI deploys via `actions/deploy-pages@v4` on push to `main`/`master`.
* Canonical config keys: `[project]` (site_name, site_url, repo_url, extra_css), `[project.theme]` (name, features, palette), `[project.plugins]` (search, tags, minify), `[project.markdown_extensions]`.

## 16. Container Runtime — Docker Compose

* All self-hosted apps run as Docker Compose stacks under `docker/<app>/compose.yaml`.
* New apps: copy `docker/.template` directory; fill `.env.tmpl`, update `compose.yaml`, then remove `.j2` extensions after Jinja2 substitution.
* Never hardcode secrets in `compose.yaml`; always source from `.env` (which is git-ignored).
* Compose files use the service name as the container name; image tags must be pinned (no `latest`).

## 17. File-to-Markdown Conversion — `markitdown`

* Use the `markitdown` CLI to convert any file (PDF, DOCX, XLSX, PPTX, images, etc.) to Markdown.
* Install: `uv pip install markitdown` (or `pip install markitdown`).
* Usage: `markitdown <file>` → outputs Markdown to stdout.
* Prefer over manual copy-paste when ingesting external documents into docs.

## 18. Comment-Preserving YAML — `ruamel.yaml`

* When Python scripts must **read and write** YAML while preserving comments and formatting, use `ruamel.yaml` (listed in `pyproject.toml`).
* For simple YAML reads or writes without comment preservation, `yq` (§9) is preferred.
* Install: `uv pip install ruamel-yaml`.
* Usage pattern:
  ```python
  from ruamel.yaml import YAML
  yaml = YAML()
  yaml.preserve_quotes = True
  with open("file.yaml") as f:
      data = yaml.load(f)
  # ... mutate data ...
  with open("file.yaml", "w") as f:
      yaml.dump(data, f)
  ```

## 19. Bash Scripting Standards — shuck + Conventions

* All Bash scripts **must** pass [`shuck`](https://github.com/ewhauser/shuck) with no warnings.
* Required header block (Name, Description, Author, Date, Version) at the top of every script.
* Shebang: `#!/usr/bin/env bash`.
* Error handling: `set -e` and `set -o pipefail` at the top.
* Constants: UPPER_CASE. Functions: snake_case. 2-space indentation.
* Wrap all logic in a `main "$@"` function called at the bottom.
* Logging: use a `log "INFO|WARN|ERRO|DEBU" "message"` function with **Catppuccin Mocha** ANSI colors.
* Paths must be set as variables after option parsing — no bare hardcoded strings in logic.
* CI: run `shuck scripts/*.sh` before committing.

## 20. Proxmox LXC Scaffolding

* New LXC containers: copy `lxc/.template` to `lxc/<app_name>`; fill in `Taskfile.yml` vars (SERVICE_NAME, INSTALL_DIR, CONFIG_DIR).
* Before creating, search [community-scripts](https://github.com/community-scripts/ProxmoxVE/tree/main/install) for an existing install script.
* Template: `debian-trixie`; use `list_templates` to find it.
* Create with: `--unprivileged 0 --net0 name=eth0,bridge=vmbr0,ip=dhcp,ip6=slaac --features nesting=1`.
* Password: `--password $(pass show default-lxc-password)` — never hardcode.
* Post-setup always includes: install `openssh-server` + `syncthing`, purge `cloud-init`, set `PermitRootLogin yes`, enable `syncthing@root` service.
* Networking: add Traefik conf in `pve/traefik/conf.d/`, AdGuard DNS rewrite, then run `/homepage update`, `/traefik update`, `/gatus update`.

## 21. Password Management — `pass`

* Use [`pass`](https://www.passwordstore.org/) (the standard Unix password manager) for retrieving secrets in scripts and commands.
* Retrieve a secret: `pass show <path/to/secret>`.
* Common usage: `--password $(pass show default-lxc-password)` when creating Proxmox LXC containers.
* Never substitute `pass` output directly into compose files or config files that are tracked in git.

## 22. Docker-Based Linting (Repo-Local Override)

* In this repo the root `Taskfile.yml` runs linters via Docker instead of native binaries:
  * **Markdownlint:** `docker run --rm -it -v ${PWD}:/markdown:ro 06kellyjac/markdownlint-cli .`
  * **Yamllint:** `docker run --rm -it -v ${PWD}:${PWD} -w ${PWD} programmerassistant/yamllint yamllint .`
* This takes precedence over the native `rumdl`/`yamllint-rs` pattern (§4, §5) for this repo specifically.
* Use the Docker variants when the repo's `task markdownlint` / `task yamllint` tasks are defined this way.

## 23. Docs Navigation Auto-Generation — `generate_mkdocs_nav.py`

* When adding new docs pages, run `task generate-docs-nav` to regenerate the nav in `zensical.toml`.
* Script: `scripts/generate_mkdocs_nav.py` — invoked via `uv run python scripts/generate_mkdocs_nav.py`.
* Do **not** hand-edit the `[[project.nav]]` blocks in `zensical.toml` for bulk changes; let the script handle it.
* Run after adding or removing any `.md` file under `docs/`.

## 24. Automated Task-List Export — `task-export` Workflow

* A weekly cron GitHub Actions workflow (`.github/workflows/task-export.yml`, cron `0 2 * * 0`) auto-exports task lists.
* Script: `scripts/run_task_export.sh` — makes the script executable then runs it.
* Commits changed `**/task-list.txt` files with message `chore(tasks): update task exports`.
* Trigger manually via `workflow_dispatch` for on-demand exports.
* Pattern to replicate for any repo needing periodic auto-generated output committed back to the repo.

## 25. Cross-Compilation — `cross`

* Containerized cross-compilation tool for Rust projects, allowing target compilation (e.g. ARMv6, ARMv7, ARM64) on host development machines without local toolchains.
* Requires a running container runtime (Docker or Podman) and a local `Cross.toml` for target image configurations if necessary.
* Command examples:
  * Install: `cargo install cross --git https://github.com/cross-rs/cross`
  * Compile: `cross build --target arm-unknown-linux-gnueabihf --release`
  * Run tests: `cross test --target arm-unknown-linux-gnueabihf`

## 26. Debian Packaging — `cargo-deb`

* Generates Debian `.deb` packages directly from Cargo metadata, automating system user creation, directory permissions, and systemd service generation.
* Configuration is declared directly in `Cargo.toml` under `[package.metadata.deb]`.
* Canonical config snippet:
  ```toml
  [package.metadata.deb]
  extended-description = "Description..."
  maintainer = "Author Name <email>"
  section = "utils"
  depends = "sudo, systemd"
  maintainer-scripts = "deployment"
  assets = [
      ["target/release/app", "usr/bin/app", "755"],
      ["app.toml.example", "etc/app/app.toml.example", "644"]
  ]
  ```
* Command examples:
  * Build package: `cargo deb --no-build --target arm-unknown-linux-gnueabihf`

## 27. RPM Packaging — `cargo-generate-rpm`

* Generates RedHat `.rpm` packages directly from Cargo metadata, utilizing custom post-install and pre-uninstall hooks.
* Configuration is declared in `Cargo.toml` under `[package.metadata.generate-rpm]`.
* Canonical config snippet:
  ```toml
  [package.metadata.generate-rpm]
  group = "Applications/System"
  release = "1"
  post_install_script = "deployment/post_install.sh"
  pre_uninstall_script = "deployment/pre_uninstall.sh"

  [package.metadata.generate-rpm.requires]
  systemd = "*"

  [[package.metadata.generate-rpm.assets]]
  source = "target/release/app"
  dest = "/usr/bin/app"
  mode = "0755"
  ```
* Command examples:
  * Build package: `cargo generate-rpm --target arm-unknown-linux-gnueabihf`

## 28. Binary Installer — `cargo-binstall`

* Installs pre-compiled Rust binaries directly from GitHub releases or crates.io, bypassing compilation overhead.
* Prefer in CI pipelines or deployment scripts where building packaging/compilation dependencies would slow down the run.
* Command examples:
  * Install binstall: `curl -L --proto '=https' --tlsv1.2 -sSf https://raw.githubusercontent.com/cargo-bins/cargo-binstall/main/install-from-binstall-release.sh | bash`
  * Install tools: `cargo binstall -y cargo-deb cargo-generate-rpm`

## 29. Code Coverage — `cargo-llvm-cov`

* Source-based code coverage tool for Rust with minimal overhead, supporting LCOV, HTML, and JSON reports.
* Prefer when establishing strict coverage gates (e.g. 90% line gate) in local development and CI pipelines.
* Command examples:
  * Run tests and fail under line gate: `cargo llvm-cov --all-features --fail-under-lines 90 -- --test-threads=1`
  * Generate coverage reports: `cargo llvm-cov --all-features --lcov --output-path lcov.info`

## 30. Coverage Reporting — `coveralls`

* Uploads generated coverage reports (e.g. `lcov.info`) to Coveralls.io to track and monitor test coverage trends over time.
* Command examples:
  * CLI upload: `coveralls report lcov.info -n -r $COVERALLS_REPO_TOKEN`
  * GitHub Action integration:
    ```yaml
    - name: Coveralls
      uses: coverallsapp/github-action@v2
      with:
        files: lcov.info
        github-token: ${{ secrets.GITHUB_TOKEN }}
    ```

## 31. Integration Test Containers — `testcontainers`

* Programmatic orchestration of transient Docker containers inside Rust unit or integration tests.
* Prefer when integration testing has dependencies on third-party services (like MQTT brokers, databases) and you want automated setup/cleanup per test.
* Canonical config snippet (in `Cargo.toml`):
  ```toml
  [dev-dependencies]
  testcontainers = "0.23"
  ```
* Command examples:
  * Run container-backed tests: `RUN_DOCKER_TESTS=1 cargo test -- --test-threads=1`

## 32. GitHub Profile Metrics — `lowlighter/metrics`

* Use [`lowlighter/metrics`](https://github.com/lowlighter/metrics) to automatically generate high-resolution SVG infographics showcasing contribution history, coding habits, WakaTime metrics, and achievements.
* Prefer using this action in a dedicated GitHub Actions workflow file (e.g. `.github/workflows/metrics.yml`) running on a regular cron schedule to keep profile assets up-to-date.
* Always store sensitive keys, such as `METRICS_SECRET` (GitHub Personal Access Token) and `WAKATIME_API_KEY`, as GitHub Repository Secrets.
* Canonical GitHub Actions job snippet:
  ```yaml
  name: Metrics
  on:
    schedule: [{cron: "0 * * * *"}]
    workflow_dispatch:
    push: {branches: ["main"]}
  jobs:
    github-metrics:
      runs-on: ubuntu-latest
      steps:
        - uses: lowlighter/metrics@latest
          with:
            filename: images/header.svg
            token: ${{ secrets.METRICS_SECRET }}
            committer_token: ${{ secrets.GITHUB_TOKEN }}
            user: nicholaswilde
            template: classic
            base: header
  ```
