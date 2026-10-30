# Python Tooling & Execution with `uv`

## Rule

Always use [`uv`](https://github.com/astral-sh/uv) to manage Python dependencies, run pipeline workflows, execute Python scripts, and invoke CLI tools in Python projects.

Never invoke bare `pip`, `python`, `pipx`, `virtualenv`, or `poetry` directly for project-level workflows.

## Guidelines

1. **Command & Script Execution**:
   - Use `uv run <command>` (e.g. `uv run pytest`, `uv run ruff check`, `uv run mypy .`) to execute tools within the project virtual environment.
   - Use `uv run script.py` for Python scripts.
   - For standalone scripts with dependencies, declare PEP 723 inline metadata or pass `--with <pkg>`:
     `uv run --with requests python script.py`.

2. **Dependency Management**:
   - Add packages: `uv add <package>` (or `uv add --dev <package>`).
   - Remove packages: `uv remove <package>`.
   - Update / lock packages: `uv lock` (or `uv lock --upgrade`).
   - Sync environment: `uv sync`.
   - Project metadata strictly belongs in `pyproject.toml` with `uv.lock` checked into version control.

3. **Taskfile & CI Automation**:
   - Prefix all Python test, lint, and run commands in `Taskfile.yaml` and CI workflows with `uv run`.
   - Install dependencies in CI using `uv sync --frozen` or `uv sync --all-extras`.

## Common Command Reference

- `uv run <cmd>` — Run command or tool inside project environment
- `uv run script.py` — Run script using project dependencies or inline metadata
- `uv add <package>` — Add dependency to `pyproject.toml` and update `uv.lock`
- `uv add --dev <package>` — Add development dependency
- `uv remove <package>` — Remove dependency
- `uv sync` — Sync virtual environment with `uv.lock`
- `uv sync --frozen` — Sync without updating lockfile (ideal for CI)
- `uv python pin <version>` — Pin Python version in `.python-version`
