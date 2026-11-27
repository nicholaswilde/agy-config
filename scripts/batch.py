#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Catalog-driven batch runner for ~/git/nicholaswilde repositories."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import tomllib
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_CATALOG = Path(__file__).resolve().parent.parent / "repos.toml"
GLOBAL_RULES_DIR = (
  Path(__file__).resolve().parent.parent / "agy" / ".gemini" / "config" / "rules"
)
CANONICAL_AGENTS_MD = Path(__file__).resolve().parent.parent / "AGENTS.md"
SENTINEL = "# --- repos ---"
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[a-zA-Z0-9._-]*)?$")
NAME_LINE_RE = re.compile(r"^\s*name\s*=")
ZENSICAL_SPEC_RE = re.compile(
  r"""(["'])zensical(\[[^\]]+\])?(?:\s*(?:>=|==|~=|<=|>|<|!=)\s*[^"']*)?\1"""
)
BARE_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")
TAGGED_BLOCK_RE = re.compile(
  r"<!-- ([A-Za-z0-9_-]+)-begin -->.*?<!-- \1-end -->",
  re.DOTALL,
)
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
MAX_SKILL_FRONTMATTER_CHARS = 380

OBSOLETE_RULES: tuple[str, ...] = (
  "antigravity-rtk-rules.md",
  "serena-rules.md",
  "context-mode-rules.md",
)
UNIVERSAL_RULES: tuple[str, ...] = (
  "rtk-rules.md",
  "fd-rules.md",
  "github-cli-rules.md",
  "ripgrep-rules.md",
  "ripwire-rules.md",
  "context7-rules.md",
  "no-secrets.md",
  "caveman-rules.md",
)
UNIVERSAL_AGENTS_BLOCKS: tuple[str, ...] = (
  "rtk",
  "context-mode",
  "ponytail",
  "caveman",
  "codegraph",
  "serena",
  "headroom",
  "ripwire",
  "context7",
  "ripgrep-guidelines",
  "fd-rules",
  "sensitive-information-protection",
  "issue-management",
)
UPDATE_IF_PRESENT_BLOCKS: tuple[str, ...] = ("karpathy", "design-md")
REQUIRED_GITIGNORE_LINES: tuple[str, ...] = (
  ".agents/*",
  "!.agents/skills/",
  "!.agents/rules/",
  "!.agents/skills_catalog.md",
  ".rtk/*",
  "!.rtk/filters.toml",
  ".codegraph/",
  ".serena/",
)

AUTO_TAGS: tuple[str, ...] = (
  "agents",
  "gh-actions",
  "llms-txt",
  "lychee",
  "python",
  "rumdl",
  "rust",
  "taplo",
  "taskfile",
  "typos",
  "yamllint",
  "zensical",
)


def load_catalog(path: Path) -> dict[str, Any]:
  """Load and parse the TOML repository catalog."""
  with path.open("rb") as f:
    return tomllib.load(f)


def resolve_repos(
  catalog: dict[str, Any],
  *,
  action: str | None = None,
  tag: str | None = None,
  only: list[str] | None = None,
) -> list[tuple[str, dict[str, Any]]]:
  """Resolve matching active repository entries from the catalog."""
  repos: dict[str, dict[str, Any]] = catalog.get("repos", {})
  if only:
    unknown = [name for name in only if name not in repos]
    if unknown:
      raise ValueError(f"Unknown repo(s): {', '.join(sorted(unknown))}")

  active = {
    name: cfg for name, cfg in repos.items() if not cfg.get("disabled", False)
  }

  if action is not None:
    actions = catalog.get("actions", {})
    if action not in actions:
      raise ValueError(f"Unknown action: {action}")
    act = actions[action]
    req_tags = set(act.get("tags", []))
    include = set(act.get("include", []))
    exclude = set(act.get("exclude", []))
    selected = {
      name
      for name, cfg in active.items()
      if req_tags.issubset(set(cfg.get("tags", [])))
    }
    selected = (selected | (include & active.keys())) - exclude
  else:
    selected = set(active.keys())

  if tag is not None:
    selected = {
      name for name in selected if tag in active[name].get("tags", [])
    }

  if only:
    only_set = set(only)
    selected = {name for name in selected if name in only_set}

  return [(name, active[name]) for name in sorted(selected)]


def detect_traits(repo_dir: Path) -> list[str]:
  """Detect repository traits matching AUTO_TAGS."""
  checks = {
    "agents": (repo_dir / "AGENTS.md").exists() or (repo_dir / ".agents").exists(),
    "gh-actions": (repo_dir / ".github" / "workflows").is_dir(),
    "llms-txt": (repo_dir / "llms.txt").exists()
    or (repo_dir / "docs" / "llms.txt").exists(),
    "lychee": (repo_dir / "lychee.toml").exists(),
    "python": (repo_dir / "pyproject.toml").exists(),
    "rumdl": (repo_dir / ".rumdl.toml").exists()
    or (repo_dir / ".markdownlint.yaml").exists(),
    "rust": (repo_dir / "Cargo.toml").exists(),
    "taplo": (repo_dir / "taplo.toml").exists()
    or (repo_dir / ".taplo.toml").exists(),
    "taskfile": (repo_dir / "Taskfile.yml").exists()
    or (repo_dir / "Taskfile.yaml").exists(),
    "typos": (repo_dir / "_typos.toml").exists()
    or (repo_dir / "dictionary.txt").exists(),
    "yamllint": (repo_dir / ".yamllint").exists()
    or (repo_dir / ".yamllint.yml").exists(),
    "zensical": (repo_dir / "zensical.toml").exists(),
  }
  return sorted(name for name, present in checks.items() if present)


def format_toml_key(name: str) -> str:
  """Quote a TOML table key segment if it contains non-bare characters."""
  return name if BARE_KEY_RE.fullmatch(name) else json.dumps(name)


def _format_toml_value(value: Any) -> str:
  if isinstance(value, bool):
    return "true" if value else "false"
  if isinstance(value, int):
    return str(value)
  if isinstance(value, float):
    return repr(value)
  if isinstance(value, str):
    return json.dumps(value)
  if isinstance(value, list):
    items = ", ".join(_format_toml_value(v) for v in value)
    return f"[{items}]"
  raise TypeError(f"Unsupported TOML value type: {type(value).__name__}")


def render_repos_section(repos: dict[str, dict[str, Any]]) -> str:
  """Render deterministic [repos.*] TOML blocks."""
  blocks: list[str] = []
  for name in sorted(repos):
    cfg = repos[name]
    lines = [f"[repos.{format_toml_key(name)}]"]
    tags = sorted(set(cfg.get("tags", [])))
    lines.append(f"tags = {_format_toml_value(tags)}")
    for key in sorted(k for k in cfg if k != "tags"):
      lines.append(f"{format_toml_key(key)} = {_format_toml_value(cfg[key])}")
    blocks.append("\n".join(lines))
  return "\n\n".join(blocks) + ("\n" if blocks else "")


def fetch_latest_pypi_version(pkg: str = "zensical") -> str:
  """Fetch the latest published package version from PyPI JSON API."""
  url = f"https://pypi.org/pypi/{pkg}/json"
  req = urllib.request.Request(url, headers={"Accept": "application/json"})
  try:
    with urllib.request.urlopen(req, timeout=15) as resp:
      data = json.load(resp)
  except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
    raise RuntimeError(f"Failed to fetch latest {pkg} version from PyPI: {exc}") from exc
  version = data.get("info", {}).get("version")
  if not version:
    raise RuntimeError(f"PyPI response missing info.version for {pkg}")
  return str(version)


def read_zensical_spec(pyproject_text: str) -> str | None:
  """Extract the first zensical dependency specifier from pyproject.toml text."""
  for line in pyproject_text.splitlines():
    if NAME_LINE_RE.match(line):
      continue
    match = ZENSICAL_SPEC_RE.search(line)
    if match:
      return match.group(0)[1:-1]
  return None


def bump_zensical_spec(pyproject_text: str, version: str) -> tuple[str, bool]:
  """Update zensical dependency specifier(s) to >=<version> line-by-line."""
  changed = False
  out_lines: list[str] = []

  def _replace(match: re.Match[str]) -> str:
    nonlocal changed
    quote = match.group(1)
    extras = match.group(2) or ""
    replacement = f"{quote}zensical{extras}>={version}{quote}"
    if replacement != match.group(0):
      changed = True
    return replacement

  for line in pyproject_text.splitlines(keepends=True):
    if NAME_LINE_RE.match(line):
      out_lines.append(line)
      continue
    out_lines.append(ZENSICAL_SPEC_RE.sub(_replace, line))

  return "".join(out_lines), changed


def read_uv_lock_version(lock_path: Path, pkg: str = "zensical") -> str | None:
  """Read locked package version from uv.lock."""
  if not lock_path.is_file():
    return None
  with lock_path.open("rb") as f:
    data = tomllib.load(f)
  for entry in data.get("package", []):
    if entry.get("name") == pkg:
      return entry.get("version")
  return None


def is_git_dirty(repo_dir: Path) -> bool:
  """Return True if git working tree has uncommitted or untracked changes."""
  res = subprocess.run(
    ["git", "-C", str(repo_dir), "status", "--porcelain"],
    capture_output=True,
    text=True,
    check=False,
  )
  return res.returncode != 0 or bool(res.stdout.strip())


def _run_cmd(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
  return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def _repo_path(root: Path, name: str, cfg: dict[str, Any]) -> Path:
  raw = cfg.get("path")
  return Path(raw).expanduser() if raw else root / name


def _short_err(res: subprocess.CompletedProcess[str]) -> str:
  msg = (res.stderr or res.stdout or f"exit {res.returncode}").strip()
  return msg.splitlines()[-1][:80] if msg else f"exit {res.returncode}"


def _print_table(headers: list[str], rows: list[list[str]]) -> None:
  widths = [len(h) for h in headers]
  for row in rows:
    for i, cell in enumerate(row):
      widths[i] = max(widths[i], len(cell))
  fmt = "  ".join(f"{{:<{w}}}" for w in widths)
  print(fmt.format(*headers))
  print(fmt.format(*("-" * w for w in widths)))
  for row in rows:
    print(fmt.format(*row))


def cmd_list(args: argparse.Namespace) -> int:
  catalog = load_catalog(Path(args.catalog))
  if args.action or args.tag:
    entries = resolve_repos(catalog, action=args.action, tag=args.tag)
    root = Path(catalog.get("settings", {}).get("root", "~/git/nicholaswilde")).expanduser()
    if args.json:
      payload = [
        {
          "name": name,
          "path": str(_repo_path(root, name, cfg)),
          "tags": cfg.get("tags", []),
        }
        for name, cfg in entries
      ]
      print(json.dumps(payload, indent=2))
      return 0
    rows = [
      [name, str(_repo_path(root, name, cfg)), ", ".join(cfg.get("tags", []))]
      for name, cfg in entries
    ]
    _print_table(["Repo", "Path", "Tags"], rows)
    return 0

  actions = catalog.get("actions", {})
  if args.json:
    payload = {
      name: {
        "description": cfg.get("description", ""),
        "count": len(resolve_repos(catalog, action=name)),
        "repos": [r for r, _ in resolve_repos(catalog, action=name)],
      }
      for name, cfg in sorted(actions.items())
    }
    print(json.dumps(payload, indent=2))
    return 0

  rows = []
  for name, cfg in sorted(actions.items()):
    matched = [r for r, _ in resolve_repos(catalog, action=name)]
    rows.append([name, str(len(matched)), cfg.get("description", ""), ", ".join(matched)])
  _print_table(["Action", "Count", "Description", "Repos"], rows)
  return 0


def cmd_sync(args: argparse.Namespace) -> int:
  catalog_path = Path(args.catalog)
  catalog = load_catalog(catalog_path)
  settings = catalog.get("settings", {})
  root = Path(settings.get("root", "~/git/nicholaswilde")).expanduser()
  ignore = set(settings.get("ignore", []))
  old_repos: dict[str, dict[str, Any]] = catalog.get("repos", {})

  if not root.is_dir():
    print(f"ERROR: Root directory not found: {root}", file=sys.stderr)
    return 1

  discovered: dict[str, Path] = {
    p.name: p
    for p in sorted(root.iterdir())
    if p.is_dir() and (p / ".git").exists() and p.name not in ignore
  }

  new_repos: dict[str, dict[str, Any]] = {}
  added: list[str] = []
  removed = sorted(set(old_repos) - set(discovered))
  tag_changes: list[tuple[str, list[str], list[str]]] = []
  auto_tag_set = set(AUTO_TAGS)

  for name, repo_dir in discovered.items():
    detected = set(detect_traits(repo_dir))
    existing = old_repos.get(name, {})
    old_tags = sorted(set(existing.get("tags", [])))
    manual_tags = set(old_tags) - auto_tag_set
    merged_tags = sorted(detected | manual_tags)

    entry: dict[str, Any] = {"tags": merged_tags}
    for k, v in existing.items():
      if k != "tags":
        entry[k] = v
    new_repos[name] = entry

    if name not in old_repos:
      added.append(name)
    elif old_tags != merged_tags:
      tag_changes.append((name, old_tags, merged_tags))

  if not added and not removed and not tag_changes:
    print(f"Catalog in sync with {root} ({len(new_repos)} repos).")
    return 0

  if added:
    print(f"Added ({len(added)}): {', '.join(added)}")
  if removed:
    print(f"Removed ({len(removed)}): {', '.join(removed)}")
  for name, old_t, new_t in tag_changes:
    plus = sorted(set(new_t) - set(old_t))
    minus = sorted(set(old_t) - set(new_t))
    parts = [*(f"+{t}" for t in plus), *(f"-{t}" for t in minus)]
    print(f"Changed {name}: {' '.join(parts)}")

  if not args.write:
    print("Run with --write to update repos.toml.")
    return 0

  raw_text = catalog_path.read_text(encoding="utf-8")
  idx = raw_text.find(SENTINEL)
  if idx == -1:
    print(f"ERROR: Sentinel '{SENTINEL}' missing in {catalog_path}", file=sys.stderr)
    return 1

  prefix = raw_text[: idx + len(SENTINEL)].rstrip("\n") + "\n\n"
  catalog_path.write_text(prefix + render_repos_section(new_repos), encoding="utf-8")
  print(f"Updated {catalog_path} ({len(new_repos)} repos).")
  return 0


def cmd_zensical_update(args: argparse.Namespace) -> int:
  if args.push and not args.commit:
    print("ERROR: --push requires --commit", file=sys.stderr)
    return 2
  if args.version and args.latest:
    print("ERROR: --version and --latest are mutually exclusive", file=sys.stderr)
    return 2

  if args.version:
    if not VERSION_RE.match(args.version):
      print(f"ERROR: Invalid version format: {args.version}", file=sys.stderr)
      return 2
    target_ver = args.version
  else:
    target_ver = fetch_latest_pypi_version("zensical")
    print(f"Resolved latest zensical version from PyPI: {target_ver}")

  catalog = load_catalog(Path(args.catalog))
  root = Path(catalog.get("settings", {}).get("root", "~/git/nicholaswilde")).expanduser()
  entries = resolve_repos(catalog, action="zensical-update", only=args.repo)

  rows: list[list[str]] = []
  had_error = False

  for name, cfg in entries:
    repo_dir = _repo_path(root, name, cfg)
    pyproject_path = repo_dir / "pyproject.toml"
    lock_path = repo_dir / "uv.lock"

    if not repo_dir.is_dir() or not pyproject_path.is_file():
      had_error = True
      rows.append([name, "-", "-", "-", "-", "error (missing pyproject.toml)"])
      continue

    if is_git_dirty(repo_dir) and not args.allow_dirty:
      rows.append([name, "-", "-", "-", "dirty", "skipped (dirty)"])
      continue

    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    old_spec = read_zensical_spec(pyproject_text)
    if old_spec is None:
      had_error = True
      rows.append([name, "missing", "-", "-", "-", "error (no zensical dep)"])
      continue

    new_text, spec_changed = bump_zensical_spec(pyproject_text, target_ver)
    new_spec = read_zensical_spec(new_text) or old_spec
    old_lock = read_uv_lock_version(lock_path, "zensical") or "-"

    if not spec_changed and old_lock == target_ver:
      rows.append([name, old_spec, old_lock, "-", "-", "up-to-date"])
      continue

    spec_col = f"{old_spec} -> {new_spec}" if spec_changed else f"{old_spec} (same)"

    if args.dry_run:
      rows.append([name, spec_col, f"{old_lock} -> ?", "skip" if not args.build else "would run", "-", "dry-run"])
      continue

    if spec_changed:
      pyproject_path.write_text(new_text, encoding="utf-8")

    lock_res = _run_cmd(["uv", "lock", "--upgrade-package", "zensical"], repo_dir)
    if lock_res.returncode != 0:
      had_error = True
      rows.append([name, spec_col, old_lock, "-", "-", f"failed ({_short_err(lock_res)})"])
      continue

    new_lock = read_uv_lock_version(lock_path, "zensical") or "-"
    lock_col = f"{old_lock} -> {new_lock}" if old_lock != new_lock else new_lock

    build_col = "-"
    if args.build:
      build_res = _run_cmd(["uv", "run", "zensical", "build"], repo_dir)
      if build_res.returncode != 0:
        had_error = True
        rows.append([name, spec_col, lock_col, "fail", "-", f"build-failed ({_short_err(build_res)})"])
        continue
      build_col = "ok"

    git_col = "-"
    if args.commit:
      stage_files = [f for f in ("pyproject.toml", "uv.lock") if (repo_dir / f).exists()]
      add_res = _run_cmd(["git", "-C", str(repo_dir), "add", *stage_files], repo_dir)
      if add_res.returncode != 0:
        had_error = True
        rows.append([name, spec_col, lock_col, build_col, "add-err", f"failed ({_short_err(add_res)})"])
        continue
      diff_res = _run_cmd(["git", "-C", str(repo_dir), "diff", "--cached", "--quiet"], repo_dir)
      if diff_res.returncode == 0:
        git_col = "no-diff"
      else:
        commit_res = _run_cmd(
          ["git", "-C", str(repo_dir), "commit", "-m", f"chore(deps): bump zensical to {target_ver}"],
          repo_dir,
        )
        if commit_res.returncode != 0:
          had_error = True
          rows.append([name, spec_col, lock_col, build_col, "commit-err", f"failed ({_short_err(commit_res)})"])
          continue
        git_col = "committed"
        if args.push:
          push_res = _run_cmd(["git", "-C", str(repo_dir), "push"], repo_dir)
          if push_res.returncode != 0:
            had_error = True
            rows.append([name, spec_col, lock_col, build_col, "push-err", f"failed ({_short_err(push_res)})"])
            continue
          git_col = "pushed"

    rows.append([name, spec_col, lock_col, build_col, git_col, "updated"])

  _print_table(["Repo", "Spec", "Lock", "Build", "Git", "Status"], rows)
  return 1 if had_error else 0


def extract_tagged_blocks(markdown_text: str) -> dict[str, str]:
  """Extract <!-- <name>-begin -->...<!-- <name>-end --> blocks from Markdown."""
  return {m.group(1): m.group(0) for m in TAGGED_BLOCK_RE.finditer(markdown_text)}


def has_root_toml(repo_dir: Path) -> bool:
  """Return True if any TOML file exists directly in repo_dir."""
  return any(p.is_file() for p in repo_dir.glob("*.toml"))


def sync_agents_md(
  agents_md_path: Path,
  canonical_blocks: dict[str, str],
  *,
  want_uv: bool,
  want_taplo: bool,
  dry_run: bool,
) -> tuple[str, bool]:
  """Synchronize canonical tagged tooling blocks in AGENTS.md."""
  if not agents_md_path.is_file():
    return "missing", False

  text = agents_md_path.read_text(encoding="utf-8")
  required = list(UNIVERSAL_AGENTS_BLOCKS)
  if want_uv:
    required.append("uv-rules")
  if want_taplo:
    required.append("taplo-rules")

  new_text = text
  added = 0
  updated = 0
  seen: set[str] = set()
  for bname in [*required, *UPDATE_IF_PRESENT_BLOCKS]:
    if bname in seen or bname not in canonical_blocks:
      continue
    seen.add(bname)
    canonical = canonical_blocks[bname]
    pat = re.compile(
      rf"<!-- {re.escape(bname)}-begin -->.*?<!-- {re.escape(bname)}-end -->",
      re.DOTALL,
    )
    match = pat.search(new_text)
    if match:
      if match.group(0) != canonical:
        new_text = new_text[: match.start()] + canonical + new_text[match.end() :]
        updated += 1
    elif bname in required:
      new_text = new_text.rstrip("\n") + "\n\n" + canonical + "\n"
      added += 1

  changed = new_text != text
  if changed and not dry_run:
    agents_md_path.write_text(new_text, encoding="utf-8")

  parts = []
  if added:
    parts.append(f"+{added}")
  if updated:
    parts.append(f"~{updated}")
  return (" ".join(parts) if parts else "ok"), changed


def sync_rules_dir(
  repo_dir: Path,
  rules_source_dir: Path,
  *,
  want_uv: bool,
  want_taplo: bool,
  want_serena: bool,
  dry_run: bool,
) -> tuple[str, bool]:
  """Remove obsolete rules and symlink relevant global rules into .agents/rules/."""
  target_dir = repo_dir / ".agents" / "rules"
  desired = list(UNIVERSAL_RULES)
  if want_uv:
    desired.append("uv-rules.md")
  if want_taplo:
    desired.append("taplo-rules.md")
  if want_serena:
    desired.append("serena.md")

  removed = 0
  linked = 0

  if target_dir.is_dir():
    for obs in OBSOLETE_RULES:
      p = target_dir / obs
      if p.is_symlink() or p.exists():
        removed += 1
        if not dry_run:
          p.unlink()

  for fname in desired:
    src = rules_source_dir / fname
    if not src.is_file():
      continue
    dst = target_dir / fname
    valid = dst.is_symlink() and dst.exists() and dst.resolve() == src.resolve()
    if not valid:
      linked += 1
      if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        if dst.is_symlink() or dst.exists():
          dst.unlink()
        dst.symlink_to(src)

  parts = []
  if linked:
    parts.append(f"+{linked}")
  if removed:
    parts.append(f"-{removed}")
  return (" ".join(parts) if parts else "ok"), (linked > 0 or removed > 0)


def _parse_skill_frontmatter(fm_text: str) -> tuple[str | None, str | None]:
  name: str | None = None
  desc: str | None = None
  lines = fm_text.splitlines()
  i = 0
  while i < len(lines):
    line = lines[i]
    if line.startswith("name:"):
      name = line.split(":", 1)[1].strip().strip("\"'")
    elif line.startswith("description:"):
      rest = line.split(":", 1)[1].strip()
      if rest in (">", ">-", "|", "|-"):
        chunks: list[str] = []
        i += 1
        while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
          if lines[i].strip():
            chunks.append(lines[i].strip())
          i += 1
        desc = " ".join(chunks)
        continue
      desc = rest.strip("\"'")
    i += 1
  return name, desc


def audit_and_sync_skills(
  repo_dir: Path,
  repo_name: str,
  *,
  dry_run: bool,
) -> tuple[str, bool, list[str]]:
  """Audit skill frontmatters and create/append .agents/skills_catalog.md."""
  skills_dir = repo_dir / ".agents" / "skills"
  if not skills_dir.is_dir():
    return "-", False, []

  skill_files = sorted(skills_dir.glob("*/SKILL.md"))
  if not skill_files:
    return "-", False, []

  warnings: list[str] = []
  skill_rows: list[tuple[str, str]] = []
  for sf in skill_files:
    dir_name = sf.parent.name
    text = sf.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
      warnings.append(f"{repo_name}/.agents/skills/{dir_name}/SKILL.md: missing YAML frontmatter")
      skill_rows.append((dir_name, f"| [`{dir_name}`](skills/{dir_name}/SKILL.md) | - | `/{dir_name}` |"))
      continue

    fm = m.group(1)
    if "name:" not in fm or "description:" not in fm:
      warnings.append(f"{repo_name}/.agents/skills/{dir_name}/SKILL.md: missing name or description")
    if len(fm) > MAX_SKILL_FRONTMATTER_CHARS:
      warnings.append(
        f"{repo_name}/.agents/skills/{dir_name}/SKILL.md: frontmatter {len(fm)} chars (max {MAX_SKILL_FRONTMATTER_CHARS})"
      )

    parsed_name, parsed_desc = _parse_skill_frontmatter(fm)
    sname = parsed_name or dir_name
    sdesc = (parsed_desc or "-").replace("|", "\\|")
    skill_rows.append((dir_name, f"| [`{sname}`](skills/{dir_name}/SKILL.md) | {sdesc} | `/{sname}` |"))

  catalog_path = repo_dir / ".agents" / "skills_catalog.md"
  if not catalog_path.is_file():
    header = (
      "# Agent Skills Catalog\n\n"
      f"Catalog of custom Antigravity agent skills available in `{repo_name}`.\n\n"
      "| Skill | Description | Task / Command |\n"
      "|---|---|---|\n"
    )
    content = header + "\n".join(row for _, row in skill_rows) + "\n"
    if not dry_run:
      catalog_path.write_text(content, encoding="utf-8")
    return f"new ({len(skill_rows)})", True, warnings

  existing = catalog_path.read_text(encoding="utf-8")
  missing = [row for dir_name, row in skill_rows if f"skills/{dir_name}/SKILL.md" not in existing]
  if not missing:
    return ("warn" if warnings else "ok"), False, warnings

  updated = existing.rstrip("\n") + "\n" + "\n".join(missing) + "\n"
  if not dry_run:
    catalog_path.write_text(updated, encoding="utf-8")
  return f"+{len(missing)}", True, warnings


def sync_gitignore(repo_dir: Path, *, dry_run: bool) -> tuple[str, bool]:
  """Ensure required .agents/, .rtk/, .codegraph/, and .serena/ rules exist in .gitignore."""
  gi_path = repo_dir / ".gitignore"
  if not gi_path.is_file() and not (repo_dir / ".agents").exists():
    return "-", False

  text = gi_path.read_text(encoding="utf-8") if gi_path.is_file() else ""
  existing = {
    line.strip()
    for line in text.splitlines()
    if line.strip() and not line.strip().startswith("#")
  }
  missing: list[str] = []
  for req in REQUIRED_GITIGNORE_LINES:
    if req in existing:
      continue
    if req == ".codegraph/" and ".codegraph" in existing:
      continue
    if req == ".serena/" and ".serena" in existing:
      continue
    missing.append(req)

  if not missing:
    return "ok", False

  if not dry_run:
    prefix = text.rstrip("\n") + "\n\n" if text.strip() else ""
    block = "# Antigravity / agent tooling\n" + "\n".join(missing) + "\n"
    gi_path.write_text(prefix + block, encoding="utf-8")
  return f"+{len(missing)}", True


def _commit_and_push_paths(
  repo_dir: Path,
  rel_paths: list[str],
  message: str,
  *,
  push: bool,
) -> tuple[str, str | None]:
  stage = [p for p in rel_paths if (repo_dir / p).exists()]
  if not stage:
    return "no-files", None
  add_res = _run_cmd(["git", "-C", str(repo_dir), "add", *stage], repo_dir)
  if add_res.returncode != 0:
    return "add-err", _short_err(add_res)
  diff_res = _run_cmd(["git", "-C", str(repo_dir), "diff", "--cached", "--quiet"], repo_dir)
  if diff_res.returncode == 0:
    return "no-diff", None
  commit_res = _run_cmd(["git", "-C", str(repo_dir), "commit", "-m", message], repo_dir)
  if commit_res.returncode != 0:
    return "commit-err", _short_err(commit_res)
  if not push:
    return "committed", None
  push_res = _run_cmd(["git", "-C", str(repo_dir), "push"], repo_dir)
  if push_res.returncode != 0:
    return "push-err", _short_err(push_res)
  return "pushed", None


def cmd_sync_agents(args: argparse.Namespace) -> int:
  if args.push and not args.commit:
    print("ERROR: --push requires --commit", file=sys.stderr)
    return 2

  rules_dir = Path(args.rules_dir).expanduser()
  canonical_path = Path(args.canonical_agents).expanduser()
  if not rules_dir.is_dir():
    print(f"ERROR: Global rules directory not found: {rules_dir}", file=sys.stderr)
    return 1
  if not canonical_path.is_file():
    print(f"ERROR: Canonical AGENTS.md not found: {canonical_path}", file=sys.stderr)
    return 1

  canonical_blocks = extract_tagged_blocks(canonical_path.read_text(encoding="utf-8"))
  catalog = load_catalog(Path(args.catalog))
  root = Path(catalog.get("settings", {}).get("root", "~/git/nicholaswilde")).expanduser()
  entries = resolve_repos(catalog, action="sync-agents", only=args.repo)

  rows: list[list[str]] = []
  all_warnings: list[str] = []
  had_error = False

  for name, cfg in entries:
    repo_dir = _repo_path(root, name, cfg)
    if not repo_dir.is_dir():
      had_error = True
      rows.append([name, "-", "-", "-", "-", "-", "error (missing dir)"])
      continue

    if is_git_dirty(repo_dir) and not args.allow_dirty:
      rows.append([name, "-", "-", "-", "-", "dirty", "skipped (dirty)"])
      continue

    tags = set(cfg.get("tags", []))
    want_uv = "python" in tags or (repo_dir / "pyproject.toml").is_file()
    want_taplo = "taplo" in tags or has_root_toml(repo_dir)
    want_serena = "rust" in tags or "python" in tags or (repo_dir / ".serena").is_dir()

    am_col, am_changed = sync_agents_md(
      repo_dir / "AGENTS.md",
      canonical_blocks,
      want_uv=want_uv,
      want_taplo=want_taplo,
      dry_run=args.dry_run,
    )
    rules_col, rules_changed = sync_rules_dir(
      repo_dir,
      rules_dir,
      want_uv=want_uv,
      want_taplo=want_taplo,
      want_serena=want_serena,
      dry_run=args.dry_run,
    )
    skills_col, skills_changed, warnings = audit_and_sync_skills(
      repo_dir,
      name,
      dry_run=args.dry_run,
    )
    all_warnings.extend(warnings)
    gi_col, gi_changed = sync_gitignore(repo_dir, dry_run=args.dry_run)

    any_changed = am_changed or rules_changed or skills_changed or gi_changed
    if not any_changed:
      status = "up-to-date (warn)" if warnings else "up-to-date"
      rows.append([name, am_col, rules_col, skills_col, gi_col, "-", status])
      continue

    if args.dry_run:
      rows.append([name, am_col, rules_col, skills_col, gi_col, "-", "dry-run"])
      continue

    git_col = "-"
    if args.commit:
      git_col, err = _commit_and_push_paths(
        repo_dir,
        ["AGENTS.md", ".agents/rules", ".agents/skills_catalog.md", ".gitignore"],
        "chore: align .agents/ rules, skills, and AGENTS.md with global standards",
        push=args.push,
      )
      if err:
        had_error = True
        rows.append([name, am_col, rules_col, skills_col, gi_col, git_col, f"failed ({err})"])
        continue

    rows.append([name, am_col, rules_col, skills_col, gi_col, git_col, "updated"])

  _print_table(["Repo", "AGENTS.md", "Rules", "Skills", "Gitignore", "Git", "Status"], rows)
  if all_warnings:
    print("\nSkill frontmatter warnings:")
    for w in all_warnings:
      print(f"  - {w}")
  return 1 if had_error else 0


def cmd_run_skill(args: argparse.Namespace) -> int:
  catalog = load_catalog(Path(args.catalog))
  root = Path(catalog.get("settings", {}).get("root", "~/git/nicholaswilde")).expanduser()

  action = args.action
  if not action and not args.tag and not args.repo:
    if args.skill in catalog.get("actions", {}):
      action = args.skill
    else:
      print(
        f"ERROR: Specify --action, --tag, or --repo (no [actions.{args.skill}] in catalog)",
        file=sys.stderr,
      )
      return 2

  entries = resolve_repos(catalog, action=action, tag=args.tag, only=args.repo)
  prompt = f"/{args.skill}"
  if args.prompt:
    prompt += f" {args.prompt}"
  if not args.allow_commit:
    prompt += " Do not commit or push changes."

  base_cmd = ["agy", "-p", "--mode", args.mode, "--print-timeout", f"{args.timeout}s"]
  if args.model:
    base_cmd.extend(["--model", args.model])
  if args.effort:
    base_cmd.extend(["--effort", args.effort])
  base_cmd.append(prompt)

  log_dir = Path(args.log_dir).expanduser() if args.log_dir else None
  if log_dir and not args.dry_run:
    log_dir.mkdir(parents=True, exist_ok=True)

  rows: list[list[str]] = []
  had_error = False

  for name, cfg in entries:
    repo_dir = _repo_path(root, name, cfg)
    if not repo_dir.is_dir():
      had_error = True
      rows.append([name, "-", "-", "error (missing dir)"])
      continue

    if is_git_dirty(repo_dir) and not args.allow_dirty:
      rows.append([name, "-", "-", "skipped (dirty)"])
      continue

    log_col = str(log_dir / f"{name}.log") if log_dir else "-"
    if args.dry_run:
      rows.append([name, "-", log_col, f"dry-run ({' '.join(base_cmd[:6])} ...)"])
      continue

    started = time.monotonic()
    res = _run_cmd(base_cmd, repo_dir)
    elapsed = f"{time.monotonic() - started:.1f}s"
    if log_dir:
      (log_dir / f"{name}.log").write_text(
        (res.stdout or "") + (f"\n--- STDERR ---\n{res.stderr}" if res.stderr else ""),
        encoding="utf-8",
      )
    if res.returncode != 0:
      had_error = True
      rows.append([name, elapsed, log_col, f"failed ({_short_err(res)})"])
      continue
    rows.append([name, elapsed, log_col, "ok"])

  _print_table(["Repo", "Duration", "Log", "Status"], rows)
  return 1 if had_error else 0


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description="Catalog-driven batch repo tool")
  parser.add_argument(
    "--catalog",
    default=str(DEFAULT_CATALOG),
    help="Path to repos.toml catalog",
  )
  sub = parser.add_subparsers(dest="command", required=True)

  p_list = sub.add_parser("list", help="List catalog actions or matching repos")
  p_list.add_argument("--action", help="Filter repos by action name")
  p_list.add_argument("--tag", help="Filter repos by tag")
  p_list.add_argument("--json", action="store_true", help="Output JSON")
  p_list.set_defaults(func=cmd_list)

  p_sync = sub.add_parser("sync", help="Scan root dir and compare/update repos.toml")
  p_sync.add_argument("--write", action="store_true", help="Write changes to repos.toml")
  p_sync.set_defaults(func=cmd_sync)

  p_z = sub.add_parser("zensical-update", help="Update zensical across cataloged repos")
  p_z.add_argument("--version", help="Target zensical version (e.g. 0.1.3)")
  p_z.add_argument("--latest", action="store_true", help="Resolve latest version from PyPI (default)")
  p_z.add_argument("--repo", action="append", help="Restrict to specific repo name (repeatable)")
  p_z.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
  p_z.add_argument("--build", action="store_true", help="Run uv run zensical build after locking")
  p_z.add_argument("--commit", action="store_true", help="Commit pyproject.toml and uv.lock")
  p_z.add_argument("--push", action="store_true", help="Push commit (requires --commit)")
  p_z.add_argument("--allow-dirty", action="store_true", help="Process repos with uncommitted changes")
  p_z.set_defaults(func=cmd_zensical_update)

  p_sa = sub.add_parser("sync-agents", help="Sync AGENTS.md, .agents/rules, skills catalog, and .gitignore")
  p_sa.add_argument("--repo", action="append", help="Restrict to specific repo name (repeatable)")
  p_sa.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
  p_sa.add_argument("--commit", action="store_true", help="Commit agent config updates")
  p_sa.add_argument("--push", action="store_true", help="Push commit (requires --commit)")
  p_sa.add_argument("--allow-dirty", action="store_true", help="Process repos with uncommitted changes")
  p_sa.add_argument("--rules-dir", default=str(GLOBAL_RULES_DIR), help="Global rules source directory")
  p_sa.add_argument("--canonical-agents", default=str(CANONICAL_AGENTS_MD), help="Canonical AGENTS.md path")
  p_sa.set_defaults(func=cmd_sync_agents)

  p_rs = sub.add_parser("run-skill", help="Run an Antigravity skill via agy -p across repos")
  p_rs.add_argument("skill", help="Skill name without leading slash (e.g. sync-agents)")
  p_rs.add_argument("--action", help="Catalog action to target")
  p_rs.add_argument("--tag", help="Catalog tag to target")
  p_rs.add_argument("--repo", action="append", help="Restrict to specific repo name (repeatable)")
  p_rs.add_argument("--prompt", help="Extra instructions appended after /<skill>")
  p_rs.add_argument("--model", help="Model override passed to agy --model")
  p_rs.add_argument("--effort", choices=("low", "medium", "high", "xhigh", "max"), help="Reasoning effort")
  p_rs.add_argument("--mode", choices=("accept-edits", "auto", "plan"), default="auto", help="agy execution mode")
  p_rs.add_argument("--timeout", type=int, default=300, help="Per-repo print timeout in seconds")
  p_rs.add_argument("--allow-commit", action="store_true", help="Allow skill prompt to commit/push changes")
  p_rs.add_argument("--dry-run", action="store_true", help="Preview agy commands without running")
  p_rs.add_argument("--allow-dirty", action="store_true", help="Process repos with uncommitted changes")
  p_rs.add_argument("--log-dir", help="Directory to write per-repo output logs")
  p_rs.set_defaults(func=cmd_run_skill)

  return parser


def main(argv: list[str] | None = None) -> int:
  parser = build_parser()
  args = parser.parse_args(argv)
  try:
    return args.func(args)
  except ValueError as exc:
    print(f"ERROR: {exc}", file=sys.stderr)
    return 2
  except RuntimeError as exc:
    print(f"ERROR: {exc}", file=sys.stderr)
    return 1


if __name__ == "__main__":
  sys.exit(main())
