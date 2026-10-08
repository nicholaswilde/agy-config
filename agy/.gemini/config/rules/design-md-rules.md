# Google DESIGN.md Specification for GUI Design

## Rule

When designing, scaffolding, or implementing graphical user interfaces (web frontends, desktop applications, mobile screens, component libraries, or dashboards), agents must consult and adhere to Google's [DESIGN.md](https://github.com/google-labs-code/design.md) specification:

1. **Locate or Establish `DESIGN.md`**: Before writing UI components, markup, or CSS/styling code, check if `DESIGN.md` exists in the project root. If absent and a UI is being built from scratch, establish a `DESIGN.md` specification file.
2. **Follow Format Specification**: Combine machine-readable design tokens in YAML front matter (`colors`, `typography`, `spacing`, `rounded`, `components`) with human-readable rationale in Markdown body (`Overview`, `Colors`, `Typography`, `Layout`, `Elevation & Depth`, `Shapes`, `Components`, `Do's and Don'ts`).
3. **Normative Tokens**: Treat YAML tokens as the single source of truth for design values. Never invent arbitrary ad-hoc hex values, paddings, or font sizes in code when tokens exist.
4. **Contrast and Accessibility**: Ensure all foreground/background color combinations satisfy WCAG AA contrast standards (minimum 4.5:1 ratio).
5. **Preferred Theme**: Default to the **Catppuccin Mocha** palette for color tokens unless another brand identity is explicitly specified.

## References

- Specification repository: <https://github.com/google-labs-code/design.md>
- Skill documentation: `design-md` (`~/.gemini/config/skills/design-md/SKILL.md`)
