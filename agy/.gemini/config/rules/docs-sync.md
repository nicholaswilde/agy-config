# Documentation Sync (`docs/`)

## Rule

Whenever adding, updating, or removing features, CLI flags, config keys, APIs, templates, or behavior in repository with `docs/`, audit and update all affected documentation before finishing task.

## Guidelines

1. **Audit Full `docs/` Tree**: Update primary reference pages (`usage.md`, `configuration.md`, `templates.md`, etc.) plus overview pages (`README.md`, `index.md`, `about.md`), config examples, and sample outputs.
2. **Sync Generated CLI Artifacts**: When CLI flags or subcommands change, regenerate bundled examples, shell completions, and man pages if repo ships them.
3. **Verify Docs Gates**: Run repo Markdown linter (`rtk rumdl check .` / `task lint:md`), spellchecker (`rtk typos --format brief` / `task spellcheck`), and static site build (e.g., `rtk uv run zensical build --clean` when `zensical.toml` exists; remove temporary `site/` if untracked).
