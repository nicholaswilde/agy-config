# Taplo TOML Linting and Formatting

## Rule

Use `taplo` (`taplo-cli`) to lint, validate, and format TOML files (`*.toml`).

## Guidelines

1. **Format In-Place**: Run `taplo fmt` or `task fmt:toml`.
2. **Lint & Validation**: Run `taplo lint` (or `taplo check`) to validate syntax and schemas.
3. **CI Quality Gates**: Run `taplo fmt --check` and `taplo lint` in CI.
4. **Configuration File**: Place rules in root `taplo.toml` or `.taplo.toml`.
5. **Taskfile Tasks**: Standardize on `task fmt:toml` and `task lint:toml` in `Taskfile.yaml`.

## Common Command Reference

- `taplo fmt` — Format TOML files in-place
- `taplo fmt --check` — Dry-run format check
- `taplo lint` — Lint and validate TOML + schemas
- `taplo fmt Cargo.toml` — Format single file
- `taplo check Cargo.toml` — Check single file syntax/schema
