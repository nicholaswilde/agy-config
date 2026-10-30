#!/usr/bin/env python3
"""Lint Antigravity rules and skills for token budget and frontmatter hygiene."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "agy" / ".gemini" / "config" / "rules"
SKILLS_DIR = ROOT / "agy" / ".gemini" / "config" / "skills"

MAX_RULE_BYTES = 2400
MAX_FRONTMATTER_CHARS = 380
FILLER_PATTERNS = [
    r"\bin order to\b",
    r"\bmake sure to\b",
    r"\byou should always\b",
    r"\bit is important to\b",
    r"\bthe reason is because\b",
]

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
errors = []

for rule in sorted(RULES_DIR.glob("*.md")):
    text = rule.read_text(encoding="utf-8")
    size = len(text.encode("utf-8"))
    if size > MAX_RULE_BYTES:
        errors.append(
            f"{rule.relative_to(ROOT)}: {size}B exceeds {MAX_RULE_BYTES}B cap (caveman-compress prose)"
        )
    prose = re.sub(r"```[\s\S]*?```", "", text)
    for pat in FILLER_PATTERNS:
        if re.search(pat, prose, re.IGNORECASE):
            errors.append(
                f"{rule.relative_to(ROOT)}: contains filler phrase matching '{pat}' (caveman-compress)"
            )

for skill in sorted(SKILLS_DIR.glob("*/SKILL.md")):
    text = skill.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        errors.append(f"{skill.relative_to(ROOT)}: missing YAML frontmatter (name/description)")
        continue
    fm = m.group(1)
    if "name:" not in fm or "description:" not in fm:
        errors.append(f"{skill.relative_to(ROOT)}: frontmatter must include 'name:' and 'description:'")
    if len(fm) > MAX_FRONTMATTER_CHARS:
        errors.append(
            f"{skill.relative_to(ROOT)}: frontmatter is {len(fm)} chars (max {MAX_FRONTMATTER_CHARS}; tighten description)"
        )

if errors:
    for err in errors:
        print(f"ERROR: {err}", file=sys.stderr)
    sys.exit(1)

print("Success: All rules and skill frontmatters pass token hygiene checks")
