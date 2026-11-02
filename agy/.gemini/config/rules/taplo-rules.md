# Taplo TOML Linting and Formatting

## Rule

Use `taplo` (`taplo-cli`) to lint, validate, and format TOML files (`*.toml`), always prefixed with `rtk` in interactive shells.

## Guidelines

1. **Format In-Place**: Run `rtk taplo fmt` or `task fmt:toml`.
2. **Lint & Validation**: Run `rtk taplo lint` (or `rtk taplo check`) to validate syntax and schemas.
3. **CI Quality Gates**: Run `taplo fmt --check` and `taplo lint` in CI.
4. **Configuration File**: Place rules in root `taplo.toml` or `.taplo.toml`.
5. **Taskfile Tasks**: Standardize on `task fmt:toml` and `task lint:toml` in `Taskfile.yaml`.

## Common Command Reference

- `rtk taplo fmt` — Format TOML files in-place
- `rtk taplo fmt --check` — Dry-run format check
- `rtk taplo lint` — Lint and validate TOML + schemas
- `rtk taplo fmt Cargo.toml` — Format single file
- `rtk taplo check Cargo.toml` — Check single file syntax/schema
