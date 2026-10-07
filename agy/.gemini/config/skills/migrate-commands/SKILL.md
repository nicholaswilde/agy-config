# /migrate commands

Migrates legacy Gemini CLI commands from `<workspace-root>/.gemini/commands/` to Antigravity skills in `<workspace-root>/.agents/skills/` and ensures compatibility.

## Description
This skill automates the migration of legacy Gemini-based command definitions into modern Antigravity skills. It scans the source folder, reads each command file, reviews it for compatibility with the Antigravity persona and toolset, converts Gemini-specific terminology to Antigravity conventions, and writes the updated skill definition to the workspace's `.agents/skills/` directory before removing the legacy command.

## Protocol

1. **Verify Source and Destination Directories:**
   - **Step:** Check if `<workspace-root>/.gemini/commands/` exists and contains files.
   - **Step:** If the source directory does not exist or contains no command files, stop and report: "No legacy Gemini commands found in `<workspace-root>/.gemini/commands/`."
   - **Step:** Check if the destination directory `<workspace-root>/.agents/skills/` exists. If not, create it.

2. **Process Each Command File:**
   - **Step:** For each command file (typically markdown, e.g. `*.md`) in the source directory:
     - **Sub-step:** Read the file content.
     - **Sub-step:** Perform a compatibility review:
       - Update any phrasing referring to "Gemini CLI" or "Gemini command" to "Antigravity CLI" or "Antigravity skill" respectively.
       - Ensure the file layout conforms to standard Antigravity skill structure:
         - Starts with a single H1 header defining the slash command (e.g., `# /my_command <args>`).
         - Followed by a brief description.
         - Followed by a `## Protocol` or `## Description` section containing clear, actionable, numbered steps or bullet points.
       - Verify that any mentioned tools, scripts, or MCP services are present and valid in the environment.
     - **Sub-step:** Write the updated skill content to `<workspace-root>/.agents/skills/<filename>`.
     - **Sub-step:** Delete the original file from `<workspace-root>/.gemini/commands/`.

3. **Report Migration Progress:**
   - **Step:** Print a summary of all migrated skills.
   - **Step:** For each skill, specify the original filename, new filename, and a brief note of any compatibility adjustments made.
