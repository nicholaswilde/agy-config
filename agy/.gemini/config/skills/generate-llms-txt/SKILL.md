---
name: generate-llms-txt
description: >-
  Generate standardized llms.txt and llms-full.txt files per llmstxt.org spec.
  Trigger: /generate-llms-txt, /llms-txt, "create llms.txt", "generate llms.txt", "create llms-full.txt", "generate llms-full.txt", "add llms.txt", "llms.txt".
---

# Generate llms.txt & llms-full.txt Skill

Generate clean, standardized `llms.txt` and `llms-full.txt` files at the root of a repository following the [llmstxt.org](https://llmstxt.org/) specification.

## Core Concepts

- **`llms.txt`**: A concise, structured index / navigation roadmap for LLMs, AI agents, and RAG pipelines. Fits easily inside context windows.
- **`llms-full.txt`**: A companion file containing the compiled, full-text documentation and complete project specifications in clean Markdown.

## `llms.txt` Specification & Required Structure

The file MUST follow this exact order:

1. **H1 Heading (`# <Project/Repo Name>`)**: Exactly one level-one heading. (Required)
2. **Blockquote (`> <Summary>`)**: Immediately follows the H1 heading. A 1-2 sentence summary of what the project does and who it is for.
3. **Preamble / Context Paragraph(s)**: Optional background text, installation notes, or high-level architecture. **No subheadings are allowed in the preamble.**
4. **H2 Sections (`## <Category>`)**: Categorized groupings of resources (e.g. `## Documentation`, `## Core Modules`, `## Usage`, `## CLI Commands`).
   - Every item in a section MUST be a Markdown list item containing a hyperlink:

     ```markdown
     - [Title](URL): Brief description of what this resource covers.
     ```

   - URLs should point directly to relevant files, documentation pages, or repository paths.
5. **Optional Section (`## Optional`)**: A designated section for secondary, low-priority, or supplementary links that LLMs can omit when context is constrained (e.g. license, author profiles, changelogs).

## `llms-full.txt` Structure

Aggregates all key information inline so an agent can ingest the complete repository context without following outbound links:

1. Same H1 heading, summary blockquote, and introductory overview as `llms.txt`.
2. **Table of Contents** linking to major sections.
3. **Comprehensive Inlined Documentation**:
   - Detailed usage & installation guides.
   - Complete lists of modules, commands, API endpoints, or formulas.
   - Per-component specifications (inputs, outputs, supported targets, options).
   - Architecture & directory layout notes.
   - Development, testing, auditing, and maintenance commands.
4. **License & Maintainer info**.

## Workflow Protocol

### Step 1: Repository Exploration

1. Identify the project name and high-level purpose:
   - Check `README.md`, `pyproject.toml`, `Cargo.toml`, `package.json`, or equivalent manifest.
   - Inspect existing documentation in `docs/` or `.agents/`.
2. Catalog primary components:
   - For libraries/tools: key modules, public APIs, CLI binaries.
   - For taps/package managers: available formulas/packages, platforms supported.
   - For web apps: key routes, architecture, deployment options.
3. Identify development workflows:
   - Look for `Taskfile.yml`, `Makefile`, `Justfile`, `scripts/`, or CI workflows.

### Step 2: Generate `llms.txt`

1. Draft the file with:
   - Single H1 heading with project name.
   - Single blockquote summary.
   - Brief 1-paragraph preamble.
   - H2 categories with `- [Title](URL): Description` list items.
   - `## Optional` section at the end.
2. Write to `llms.txt` in the repository root.

### Step 3: Generate `llms-full.txt`

1. Assemble detailed documentation into a single consolidated document.
2. Ensure markdown formatting is clean:
   - No unnecessary raw HTML or boilerplate navigation bars.
   - Clear markdown tables or headings for individual components.
   - Accurate code snippets, CLI examples, and command syntax.
3. Write to `llms-full.txt` in the repository root.

### Step 4: Verification

1. Verify both files exist at the repository root.
2. Check that `llms.txt` strictly adheres to the format:
   - Exactly one `#` header at line 1.
   - Followed by `>` blockquote.
   - Only `##` headers for sections.
   - Proper `- [Label](url): description` format for entries.
