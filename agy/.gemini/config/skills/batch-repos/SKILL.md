---
name: batch-repos
description: >-
  Run catalog-driven batch operations across ~/git/nicholaswilde repos using repos.toml and scripts/batch.py.
  Trigger: /batch-repos, /update-zensical, "batch repos", "update zensical", "batch sync-agents", "run skill across repos", "sync repo catalog".
---

# Batch Repos Skill

Run batch operations across `~/git/nicholaswilde` from catalog `/home/nicholas/git/nicholaswilde/agy-config/repos.toml`. Never scan `~/git/nicholaswilde` during normal batch runs.

## Protocol

1. **Inspect Targets**:
   - Actions: `rtk uv run /home/nicholas/git/nicholaswilde/agy-config/scripts/batch.py list`
   - Action targets: `rtk uv run /home/nicholas/git/nicholaswilde/agy-config/scripts/batch.py list --action <name>`
2. **Preview First**:
   - Zensical: `rtk uv run /home/nicholas/git/nicholaswilde/agy-config/scripts/batch.py zensical-update --dry-run`
   - Sync agents: `rtk uv run /home/nicholas/git/nicholaswilde/agy-config/scripts/batch.py sync-agents --dry-run`
   - Headless skill: `rtk uv run /home/nicholas/git/nicholaswilde/agy-config/scripts/batch.py run-skill <skill> --dry-run`
3. **Apply Changes**:
   - Edit-only default (skips dirty repos):
     - `rtk uv run /home/nicholas/git/nicholaswilde/agy-config/scripts/batch.py zensical-update [--version <ver>] [--build]`
     - `rtk uv run /home/nicholas/git/nicholaswilde/agy-config/scripts/batch.py sync-agents` (fast deterministic sync)
     - `rtk uv run /home/nicholas/git/nicholaswilde/agy-config/scripts/batch.py run-skill sync-agents` (full AI `agy -p` skill run)
   - Filter subset with repeatable `--repo <name>`.
   - Pass `--commit` / `--push` only when user explicitly asks to commit or push.
4. **Sync Catalog (On Demand)**:
   - Diff only: `rtk uv run /home/nicholas/git/nicholaswilde/agy-config/scripts/batch.py sync`
   - Write updates: `rtk uv run /home/nicholas/git/nicholaswilde/agy-config/scripts/batch.py sync --write`
5. **Add New Batch Action**:
   - Add `[actions.<name>]` (`description`, `tags`, optional `include`/`exclude`) to `repos.toml`.
   - Add subcommand to `scripts/batch.py` + test in `scripts/test_batch.py` + task in `Taskfile.yml`.
