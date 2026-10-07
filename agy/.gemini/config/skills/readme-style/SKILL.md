# /readme-style-guide

Applies or verifies strict README styling, structure, and formatting guidelines based on the repository's native standard conventions.

## Description
This skill enforces a consistent, visually polished README structure and design system based on the native conventions of this repository. It defines standard conventions for badge styling, document hierarchy, task and CLI usage presentation, callout formatting, and tables.

## Protocol

1. **Badge Styling:**
   - Badges must be placed immediately beneath the main H1 header.
   - Use the [shields.io](https://shields.io) service with the `style=for-the-badge` query parameter for all badges.
   - Example Badge Snippets:
     ```markdown
     [![Coveralls](https://img.shields.io/coveralls/github/nicholaswilde/adguardhome-mcp-rs/main?style=for-the-badge&logo=coveralls)](https://coveralls.io/github/nicholaswilde/adguardhome-mcp-rs?branch=main)
     [![task](https://img.shields.io/badge/Task-Enabled-brightgreen?style=for-the-badge&logo=task&logoColor=white)](https://taskfile.dev/#/)
     [![ci](https://img.shields.io/github/actions/workflow/status/nicholaswilde/adguardhome-mcp-rs/ci.yml?label=ci&style=for-the-badge&branch=main&logo=github-actions)](https://github.com/nicholaswilde/adguardhome-mcp-rs/actions/workflows/ci.yml)
     ```
   - Color palette theme: Use `brightgreen` for the task-enabled badge.

2. **Document Structure & Heading Hierarchy:**
   - **Main Heading (H1):** Must use the format `# :shield: <App Name> (Rust) :robot:`
     ```markdown
     # :shield: AdGuard Home MCP Server (Rust) :robot:
     ```
   - **Section Headers (H2/H3/H4) and Emoji Prefixes:** Each major section must use a specific emoji and hierarchy:
     - Features: `## :sparkles: Features`
     - Installation: `## :package: Installation`
       - Subsection: `### Homebrew`
     - Build: `## :hammer_and_wrench: Build`
       - Subsections: `### Local Build`, `### Cross-Compilation`
     - Usage: `## :rocket: Usage`
       - Subsection: `### :keyboard: Command Line Interface`
         - H4 Heading: `#### Available Arguments`
       - Subsection: `### :file_folder: Configuration File`
         - H4 Heading: `#### Multi-Instance Configuration`
         - H4 Heading: `#### Environment Variables for Multiple Instances`
       - Subsection: `### :robot: Configuration Example (Claude Desktop)`
     - Testing: `## :test_tube: Testing`
       - Subsection: `### :bar_chart: Coverage`
     - Contributing: `## :handshake: Contributing`
     - License: `## :balance_scale: License`
     - Author: `## :writing_hand: Author`
   - **Standard Ordering & Wording (License & Author):** The final sections must follow the exact ordering of: Contributing, License, and Author.
     - License and Author sections must use the format:
       ```markdown
       ## :balance_scale: License

       ​[Apache License 2.0](LICENSE)

       ## :writing_hand: Author

       ​This project was started in 2026 by [Nicholas Wilde][2].

       [2]: <https://github.com/nicholaswilde/>
       ```
       *Note:* A zero-width space (`\u200b`) must precede the text `[Apache License 2.0]` and `This project was started...`.

3. **Tooling & Usage Presentation:**
   - **Task runner commands:** Must always be presented in code blocks with `bash` highlighting and use `task <task_name>`:
     ```bash
     task test
     ```
   - **CLI Usage:** Binary execution syntax should use raw target executions:
     ```bash
     ./target/release/adguardhome-mcp-rs --flag value
     ```
   - **Syntax Highlighting:** Every code block must use its specific language identifier: `bash`, `toml`, `json`, `yaml`.

4. **Formatting Quirks & Conventions:**
   - **Callout Blocks:** Warnings, notes, and tips must use GitHub-style blockquotes:
     ```markdown
     > [!WARNING]
     > This project is currently in active development (vX.Y.Z) and is **not production-ready**. ...
     ```
   - **Tables:** CLI arguments tables must use left-aligned columns:
     ```markdown
     | Argument | Environment Variable | Description | Default |
     | :--- | :--- | :--- | :--- |
     ```
   - **Inline Code:** File names, command flags, and configuration keys must be enclosed in backticks (e.g. `` `config.toml` ``, `` `--config` ``).
   - **Zero-Width Spaces:** Ensure zero-width spaces (`\u200b`) are preserved before major paragraphs in the bottom sections (License, Author).

## Examples

### Complete Top Section Mockup
```markdown
# :shield: myapp (Rust) :robot:

[![Coveralls](https://img.shields.io/coveralls/github/owner/myapp/main?style=for-the-badge&logo=coveralls)](https://coveralls.io/github/owner/myapp?branch=main)
[![task](https://img.shields.io/badge/Task-Enabled-brightgreen?style=for-the-badge&logo=task&logoColor=white)](https://taskfile.dev/#/)

> [!WARNING]
> This project is currently in active development (v0.1.0) and is **not production-ready**. Use at your own risk.

`myapp` is a lightweight daemon...
```

### Complete Bottom Section Mockup
```markdown
## :balance_scale: License

​[Apache License 2.0](LICENSE)

## :writing_hand: Author

​This project was started in 2026 by [Nicholas Wilde][2].

[2]: <https://github.com/nicholaswilde/>
```
