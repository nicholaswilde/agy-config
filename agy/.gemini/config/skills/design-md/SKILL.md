---
name: design-md
description: >
  Enforces Google's DESIGN.md format specification when building, designing, or styling GUIs, web apps, desktop interfaces, and design systems.
---

# Google DESIGN.md Specification

A format specification developed by Google Labs for describing visual identities and design systems to coding agents. It gives agents a persistent, structured understanding of a design system.

- Repository: <https://github.com/google-labs-code/design.md>

## Format Structure

A `DESIGN.md` file combines:

1. **YAML Front Matter**: Machine-readable design tokens delimited by `---` at the top of the file.
2. **Markdown Body**: Human-readable design rationale organized into standard sections.

Tokens provide exact normative values. Prose tells agents *why* those values exist and how to apply them.

## Token Schema (YAML Front Matter)

```yaml
---
version: alpha
name: Brand or App Name
description: Optional summary of visual identity
omitted:
  - spacing
  - section: rounded
    reason: "No rounded corners defined in brand guidelines"
colors:
  primary: "#1A1C1E"
  secondary: "#6C7278"
  tertiary: "#B8422E"
  neutral: "#F7F5F2"
typography:
  h1:
    fontFamily: Public Sans
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -0.02em
  body-md:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
rounded:
  sm: 4px
  md: 8px
  lg: 16px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  button:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
    borderRadius: "{rounded.md}"
---
```

### Schema Rules & Value Types

- **Colors**: Valid CSS color strings (`#RRGGBB`, `rgb()`, `hsl()`, `oklch()`). Hex notation is default.
- **Typography**: Requires `fontFamily`, `fontSize` (Dimension: `px`, `rem`, `em`), `fontWeight` (numeric, e.g. `400`, `600`), `lineHeight` (Dimension or unitless number multiplier).
- **Dimensions**: Numeric values with unit suffix: `px`, `em`, `rem`.
- **References**: Wrapped in curly braces using object path: `"{colors.primary}"`, `"{rounded.md}"`.
- **Omitted**: Explicitly lists sections intentionally omitted to suppress validation warnings.

## Canonical Markdown Body Sections

The markdown body must follow this canonical section ordering:

1. `## Overview` (or `## Brand & Style`): Holistic description of personality, tone, emotional response, and density.
2. `## Colors`: Color palettes and semantic roles (`primary`, `secondary`, `tertiary`, `neutral`).
3. `## Typography`: Narrative and technical font choices, scales, and usage rules.
4. `## Layout` (or `## Layout & Spacing`): Grid systems, container widths, whitespace rhythm.
5. `## Elevation & Depth`: Shadow tiers, z-index strategy, layering.
6. `## Shapes`: Border radii, corner treatments, borders.
7. `## Components`: Common reusable patterns (buttons, cards, inputs, dialogs).
8. `## Do's and Don'ts`: Actionable design rules and common anti-patterns.

## Agent Workflow

When building or styling any GUI:

1. **Check for `DESIGN.md`**: Look for `DESIGN.md` in repository root.
2. **If missing**: If scaffolding a new GUI or design system, create `DESIGN.md` establishing tokens and rationale before writing UI code.
3. **Reference Tokens**: Use CSS custom properties or framework theme bindings derived from tokens (e.g. Tailwind `theme.extend`, CSS `:root`).
4. **Enforce WCAG AA**: Ensure component `backgroundColor` and `textColor` meet minimum 4.5:1 contrast ratio.
5. **No Magic Values**: Avoid arbitrary inline hex codes or pixel dimensions that bypass `DESIGN.md`.
