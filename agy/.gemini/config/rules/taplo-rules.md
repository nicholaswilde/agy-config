# Taplo TOML Linting and Formatting

## Rule

Always use `taplo` (`taplo-cli`) as the standard tool for linting, validating, and formatting TOML documents (`*.toml`) across repositories.

## Guidelines

1. **Format In-Place**: Run `taplo fmt` or `task fmt:toml` to format all TOML files according to the project's formatting standard.
2. **Lint & Validation**: Run `taplo lint` (or `taplo check`) to validate TOML syntax and verify schema definitions.
3. **CI Quality Gates**: Run `taplo fmt --check` and `taplo lint` in continuous integration to catch formatting and syntax issues without modifying files.
4. **Configuration File**: Place repository formatting rules in `taplo.toml` or `.taplo.toml` at the repository root.
5. **Taskfile Tasks**: Standardize on `task fmt:toml` and `task lint:toml` in `Taskfile.yaml`.

## Common Command Reference

- `taplo fmt` — Format all included TOML files in-place
- `taplo fmt --check` — Dry-run check for unformatted files (fails if formatting needed)
- `taplo lint` — Lint and validate TOML files and schemas
- `taplo fmt Cargo.toml` — Format a specific file
- `taplo check Cargo.toml` — Check a specific file for syntax or schema errors
