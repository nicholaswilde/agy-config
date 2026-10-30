# Google DESIGN.md Specification for GUI Design

## Rule

When designing, scaffolding, or building GUIs (web frontends, desktop apps, mobile screens, component libraries, dashboards), adhere to Google's [DESIGN.md](https://github.com/google-labs-code/design.md) spec:

1. **Locate or Establish `DESIGN.md`**: Before writing UI components, markup, or CSS/styling, check if `DESIGN.md` exists in project root. If absent and building UI from scratch, create `DESIGN.md`.
2. **Follow Format Specification**: Combine machine-readable design tokens in YAML front matter (`colors`, `typography`, `spacing`, `rounded`, `components`) with Markdown rationale (`Overview`, `Colors`, `Typography`, `Layout`, `Elevation & Depth`, `Shapes`, `Components`, `Do's and Don'ts`).
3. **Normative Tokens**: Treat YAML tokens as single source of truth. Never invent ad-hoc hex values, paddings, or font sizes when tokens exist.
4. **Contrast and Accessibility**: Ensure foreground/background color pairs meet WCAG AA contrast (>= 4.5:1 ratio).
5. **Preferred Theme**: Default to **Catppuccin Mocha** palette unless another brand identity is specified.

## References

- Specification repository: <https://github.com/google-labs-code/design.md>
- Skill documentation: `design-md` (`~/.gemini/config/skills/design-md/SKILL.md`)
