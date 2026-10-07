# Enforce Taskfile and Scripts Automation

Global behavioral constraint forcing the agent to check for predefined tasks and scripts before executing raw shell commands.

## Description
This skill establishes a strict execution hierarchy for system operations, repository management, and environment orchestration. Agents must never default to raw multi-line shell executions or ad-hoc commands if an established automation pathway exists within `Taskfile.yaml` or the `scripts/` directory.

## Protocol

1. **Analyze User Intent:**
   - Determine the requested operation (e.g., building, testing, linting, deploying, or stowing).

2. **Audit Local Automation Pathways:**
   - **Step:** Inspect `Taskfile.yaml` at the root of the repository to check for existing tasks matching or related to the user intent.
   - **Step:** Scan the `scripts/` directory for executable shell scripts that handle the target workflow.

3. **Execution Hierarchy Selection:**
   - **Priority 1 (Taskfile):** If a relevant task exists in `Taskfile.yaml` (e.g., `task check-secrets`), execute that task directly using `go-task`.
   - **Priority 2 (Dedicated Scripts):** If no matching task exists but a dedicated script is present in `scripts/` (e.g., `scripts/check-secrets.sh`), invoke the script rather than duplicating its logic into a raw command.
   - **Priority 3 (Raw Commands):** Only utilize raw shell commands if no pre-existing task or script covers the required functionality.

4. **Automation Alignment Protocol:**
   - If a repetitive or multi-step operation is required but no task or script exists, prefer recommending or creating an entry in `Taskfile.yaml` or a script under `scripts/` using 2-space indentation guidelines before executing, keeping the codebase consistent and maintainable.
