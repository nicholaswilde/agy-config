---
trigger: always_on
description: "Python tooling & execution with uv"
---

# Python Tooling & Execution with `uv`

## Rule

Always use [`uv`](https://github.com/astral-sh/uv) to manage Python dependencies, run workflows, execute scripts, and invoke CLI tools. Always prefix `uv` commands with `rtk` (e.g. `rtk uv run ...`). Never run bare `pip`, `python`, `python3`, `pipx`, `virtualenv`, `poetry`, or bare `uv`.

## Guidelines

1. **Command & Script Execution**:
   - Run project tools via `rtk uv run <command>` (`rtk uv run pytest`, `rtk uv run ruff check`, `rtk uv run mypy .`).
   - Run scripts via `rtk uv run python3 <script>` or `rtk uv run <script>`. Never invoke bare `python3 <script>` or bare `uv run <script>`.
   - For standalone scripts with deps, use PEP 723 inline metadata or `--with <pkg>`: `rtk uv run --with requests python script.py`.

2. **Dependency Management**:
   - Add: `rtk uv add <package>` (or `rtk uv add --dev <package>`).
   - Remove: `rtk uv remove <package>`.
   - Lock: `rtk uv lock` (or `rtk uv lock --upgrade`).
   - Sync: `rtk uv sync`.
   - Keep metadata in `pyproject.toml` and commit `uv.lock`.

3. **Taskfile & CI Automation**:
   - Prefix Python commands in `Taskfile.yaml` and CI with `uv run`.
   - Install in CI via `uv sync --frozen` or `uv sync --all-extras`.

## Common Command Reference

- `rtk uv run <cmd>` — Run tool in project env
- `rtk uv run script.py` — Run script with project/inline deps
- `rtk uv add <package>` — Add dep to `pyproject.toml` + `uv.lock`
- `rtk uv add --dev <package>` — Add dev dep
- `rtk uv remove <package>` — Remove dep
- `rtk uv sync` — Sync venv with `uv.lock`
- `rtk uv sync --frozen` — Sync without updating lockfile (CI)
- `rtk uv python pin <version>` — Pin Python in `.python-version`
