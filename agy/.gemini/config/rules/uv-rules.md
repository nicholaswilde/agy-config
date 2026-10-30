# Python Tooling & Execution with `uv`

## Rule

Always use [`uv`](https://github.com/astral-sh/uv) to manage Python dependencies, run workflows, execute scripts, and invoke CLI tools. Never run bare `pip`, `python`, `pipx`, `virtualenv`, or `poetry`.

## Guidelines

1. **Command & Script Execution**:
   - Run project tools via `uv run <command>` (`uv run pytest`, `uv run ruff check`, `uv run mypy .`).
   - Run scripts via `uv run script.py`.
   - For standalone scripts with deps, use PEP 723 inline metadata or `--with <pkg>`: `uv run --with requests python script.py`.

2. **Dependency Management**:
   - Add: `uv add <package>` (or `uv add --dev <package>`).
   - Remove: `uv remove <package>`.
   - Lock: `uv lock` (or `uv lock --upgrade`).
   - Sync: `uv sync`.
   - Keep metadata in `pyproject.toml` and commit `uv.lock`.

3. **Taskfile & CI Automation**:
   - Prefix Python commands in `Taskfile.yaml` and CI with `uv run`.
   - Install in CI via `uv sync --frozen` or `uv sync --all-extras`.

## Common Command Reference

- `uv run <cmd>` — Run tool in project env
- `uv run script.py` — Run script with project/inline deps
- `uv add <package>` — Add dep to `pyproject.toml` + `uv.lock`
- `uv add --dev <package>` — Add dev dep
- `uv remove <package>` — Remove dep
- `uv sync` — Sync venv with `uv.lock`
- `uv sync --frozen` — Sync without updating lockfile (CI)
- `uv python pin <version>` — Pin Python in `.python-version`
