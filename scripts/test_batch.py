#!/usr/bin/env python3
"""Unit tests for scripts/batch.py."""

from __future__ import annotations

import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batch  # noqa: E402


class ResolveReposTests(unittest.TestCase):
  def setUp(self) -> None:
    self.catalog = {
      "settings": {"root": "~/git/nicholaswilde"},
      "actions": {
        "zensical-update": {
          "tags": ["zensical"],
          "include": ["extra-site"],
          "exclude": ["skip-site"],
        }
      },
      "repos": {
        "tfa": {"tags": ["zensical", "rust"]},
        "skip-site": {"tags": ["zensical"]},
        "extra-site": {"tags": ["python"]},
        "off-site": {"tags": ["zensical"], "disabled": True},
        "nicholaswilde.github.io": {"tags": ["python"]},
      },
    }

  def test_action_tags_include_exclude_and_disabled(self) -> None:
    got = [name for name, _ in batch.resolve_repos(self.catalog, action="zensical-update")]
    self.assertEqual(got, ["extra-site", "tfa"])

  def test_only_filter_and_dotted_name(self) -> None:
    got = [
      name
      for name, _ in batch.resolve_repos(
        self.catalog, only=["nicholaswilde.github.io"]
      )
    ]
    self.assertEqual(got, ["nicholaswilde.github.io"])

  def test_unknown_repo_raises(self) -> None:
    with self.assertRaises(ValueError):
      batch.resolve_repos(self.catalog, only=["missing-repo"])


class BumpZensicalSpecTests(unittest.TestCase):
  def test_multiline_dependencies(self) -> None:
    src = (
      '[project]\n'
      'name = "tfa"\n'
      'dependencies = [\n'
      '  "zensical>=0.0.45",\n'
      ']\n'
    )
    out, changed = batch.bump_zensical_spec(src, "0.1.3")
    self.assertTrue(changed)
    self.assertIn('"zensical>=0.1.3"', out)

  def test_inline_dependencies(self) -> None:
    src = '[project]\ndependencies = ["zensical>=0.0.45"]\n'
    out, changed = batch.bump_zensical_spec(src, "0.1.3")
    self.assertTrue(changed)
    self.assertEqual(out, '[project]\ndependencies = ["zensical>=0.1.3"]\n')

  def test_multiple_deps_and_extras_and_name_preserved(self) -> None:
    src = (
      '[project]\n'
      'name = "zensical"\n'
      'description = "zensical site generator"\n'
      'dependencies = [\n'
      '    "jinja2>=3.1.6",\n'
      '    \'zensical[docs]>=0.0.44\',\n'
      ']\n'
    )
    out, changed = batch.bump_zensical_spec(src, "0.1.3")
    self.assertTrue(changed)
    self.assertIn('name = "zensical"', out)
    self.assertIn('description = "zensical site generator"', out)
    self.assertIn("'zensical[docs]>=0.1.3'", out)
    self.assertIn('"jinja2>=3.1.6"', out)


class SyncTests(unittest.TestCase):
  def test_sync_preserves_header_manual_tags_disabled_and_dotted_keys(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
      tmp_path = Path(tmp)
      repos_root = tmp_path / "repos"
      repos_root.mkdir()

      for name, files in (
        ("tfa", ["zensical.toml", "Cargo.toml"]),
        ("nicholaswilde.github.io", ["pyproject.toml"]),
        ("ignored-dir", ["zensical.toml"]),
      ):
        d = repos_root / name
        d.mkdir()
        (d / ".git").mkdir()
        for fname in files:
          (d / fname).write_text("", encoding="utf-8")

      catalog_path = tmp_path / "repos.toml"
      catalog_path.write_text(
        f'[settings]\n'
        f'root = "{repos_root}"\n'
        f'ignore = ["ignored-dir"]\n\n'
        f'[actions.zensical-update]\n'
        f'description = "Update"\n'
        f'tags = ["zensical"]\n\n'
        f'# --- repos ---\n\n'
        f'[repos.tfa]\n'
        f'tags = ["custom-manual", "zensical"]\n'
        f'disabled = true\n',
        encoding="utf-8",
      )

      buf = io.StringIO()
      with redirect_stdout(buf):
        rc = batch.main(["--catalog", str(catalog_path), "sync", "--write"])
      self.assertEqual(rc, 0)

      parsed = batch.load_catalog(catalog_path)
      self.assertEqual(parsed["actions"]["zensical-update"]["tags"], ["zensical"])
      self.assertIn("nicholaswilde.github.io", parsed["repos"])
      self.assertNotIn("ignored-dir", parsed["repos"])
      self.assertTrue(parsed["repos"]["tfa"]["disabled"])
      self.assertEqual(
        parsed["repos"]["tfa"]["tags"],
        ["custom-manual", "rust", "zensical"],
      )
      self.assertIn('[repos."nicholaswilde.github.io"]', catalog_path.read_text())


class ZensicalUpdateTests(unittest.TestCase):
  def _init_repo(self, repo_dir: Path, pyproject: str, dirty: bool = False) -> None:
    repo_dir.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_dir, check=True)
    (repo_dir / "zensical.toml").write_text("", encoding="utf-8")
    (repo_dir / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    (repo_dir / "uv.lock").write_text(
      'version = 1\n\n[[package]]\nname = "zensical"\nversion = "0.0.45"\n',
      encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo_dir, check=True)
    if dirty:
      (repo_dir / "dirty.txt").write_text("dirty\n", encoding="utf-8")

  def test_push_without_commit_rejected(self) -> None:
    err = io.StringIO()
    with redirect_stderr(err):
      rc = batch.main(["zensical-update", "--version", "0.1.3", "--push"])
    self.assertEqual(rc, 2)
    self.assertIn("--push requires --commit", err.getvalue())

  def test_dry_run_and_dirty_skip(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
      tmp_path = Path(tmp)
      root = tmp_path / "repos"
      clean_repo = root / "clean"
      dirty_repo = root / "dirty"
      orig_pyproject = '[project]\ndependencies = ["zensical>=0.0.45"]\n'
      self._init_repo(clean_repo, orig_pyproject, dirty=False)
      self._init_repo(dirty_repo, orig_pyproject, dirty=True)

      catalog = tmp_path / "repos.toml"
      catalog.write_text(
        f'[settings]\nroot = "{root}"\n\n'
        f'[actions.zensical-update]\ntags = ["zensical"]\n\n'
        f'# --- repos ---\n\n'
        f'[repos.clean]\ntags = ["zensical"]\n\n'
        f'[repos.dirty]\ntags = ["zensical"]\n',
        encoding="utf-8",
      )

      out = io.StringIO()
      with redirect_stdout(out):
        rc = batch.main(
          ["--catalog", str(catalog), "zensical-update", "--version", "0.1.3", "--dry-run"]
        )
      self.assertEqual(rc, 0)
      text = out.getvalue()
      self.assertIn("dry-run", text)
      self.assertIn("skipped (dirty)", text)
      self.assertEqual((clean_repo / "pyproject.toml").read_text(), orig_pyproject)

  def test_allow_dirty_updates_with_mocked_uv(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
      tmp_path = Path(tmp)
      root = tmp_path / "repos"
      dirty_repo = root / "dirty"
      self._init_repo(
        dirty_repo, '[project]\ndependencies = ["zensical>=0.0.45"]\n', dirty=True
      )
      catalog = tmp_path / "repos.toml"
      catalog.write_text(
        f'[settings]\nroot = "{root}"\n\n'
        f'[actions.zensical-update]\ntags = ["zensical"]\n\n'
        f'# --- repos ---\n\n'
        f'[repos.dirty]\ntags = ["zensical"]\n',
        encoding="utf-8",
      )

      def fake_run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        if cmd[:2] == ["uv", "lock"]:
          (cwd / "uv.lock").write_text(
            'version = 1\n\n[[package]]\nname = "zensical"\nversion = "0.1.3"\n',
            encoding="utf-8",
          )
        return subprocess.CompletedProcess(cmd, 0, "", "")

      out = io.StringIO()
      with mock.patch.object(batch, "_run_cmd", side_effect=fake_run), redirect_stdout(out):
        rc = batch.main(
          [
            "--catalog",
            str(catalog),
            "zensical-update",
            "--version",
            "0.1.3",
            "--allow-dirty",
          ]
        )
      self.assertEqual(rc, 0)
      self.assertIn("updated", out.getvalue())
      self.assertIn("zensical>=0.1.3", (dirty_repo / "pyproject.toml").read_text())


class SyncAgentsTests(unittest.TestCase):
  def _setup_fixture(self, tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    rules_dir = tmp_path / "global_rules"
    rules_dir.mkdir()
    for fname in (
      *batch.UNIVERSAL_RULES,
      "uv-rules.md",
      "taplo-rules.md",
      "serena.md",
    ):
      (rules_dir / fname).write_text(f"# {fname}\n", encoding="utf-8")

    canonical_agents = tmp_path / "CANONICAL_AGENTS.md"
    blocks = []
    for b in (*batch.UNIVERSAL_AGENTS_BLOCKS, "uv-rules", "taplo-rules", *batch.UPDATE_IF_PRESENT_BLOCKS):
      blocks.append(f"<!-- {b}-begin -->\n## {b}\ncanonical {b}\n<!-- {b}-end -->")
    canonical_agents.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")

    root = tmp_path / "repos"
    repo = root / "demo"
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / "pyproject.toml").write_text('[project]\nname = "demo"\n', encoding="utf-8")
    (repo / "AGENTS.md").write_text(
      "# Demo\n\n"
      "<!-- rtk-begin -->\noutdated rtk\n<!-- rtk-end -->\n\n"
      "<!-- custom-project-begin -->\nkeep me\n<!-- custom-project-end -->\n",
      encoding="utf-8",
    )
    repo_rules = repo / ".agents" / "rules"
    repo_rules.mkdir(parents=True)
    (repo_rules / "antigravity-rtk-rules.md").write_text("old\n", encoding="utf-8")
    (repo_rules / "demo-project.md").write_text("project rule\n", encoding="utf-8")

    skill_a = repo / ".agents" / "skills" / "alpha"
    skill_a.mkdir(parents=True)
    (skill_a / "SKILL.md").write_text(
      "---\nname: alpha\ndescription: Alpha skill\n---\n\n# Alpha\n",
      encoding="utf-8",
    )
    skill_b = repo / ".agents" / "skills" / "beta"
    skill_b.mkdir(parents=True)
    (skill_b / "SKILL.md").write_text(
      f"---\nname: beta\ndescription: {'x' * 390}\n---\n\n# Beta\n",
      encoding="utf-8",
    )
    (repo / ".agents" / "skills_catalog.md").write_text(
      "# Agent Skills Catalog\n\n"
      "| Skill | Description | Task / Command |\n"
      "|---|---|---|\n"
      "| [`alpha`](skills/alpha/SKILL.md) | Curated desc | `task alpha` |\n",
      encoding="utf-8",
    )
    (repo / ".gitignore").write_text(".venv/\n.codegraph\n", encoding="utf-8")

    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)

    catalog = tmp_path / "repos.toml"
    catalog.write_text(
      f'[settings]\nroot = "{root}"\n\n'
      f'[actions.sync-agents]\ntags = ["agents"]\n\n'
      f'# --- repos ---\n\n'
      f'[repos.demo]\ntags = ["agents", "python"]\n',
      encoding="utf-8",
    )
    return catalog, repo, rules_dir, canonical_agents

  def test_push_without_commit_rejected(self) -> None:
    err = io.StringIO()
    with redirect_stderr(err):
      rc = batch.main(["sync-agents", "--push"])
    self.assertEqual(rc, 2)
    self.assertIn("--push requires --commit", err.getvalue())

  def test_dry_run_leaves_repo_untouched(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
      catalog, repo, rules_dir, canonical_agents = self._setup_fixture(Path(tmp))
      orig_agents = (repo / "AGENTS.md").read_text()
      out = io.StringIO()
      with redirect_stdout(out):
        rc = batch.main(
          [
            "--catalog", str(catalog),
            "sync-agents",
            "--dry-run",
            "--rules-dir", str(rules_dir),
            "--canonical-agents", str(canonical_agents),
          ]
        )
      self.assertEqual(rc, 0)
      self.assertIn("dry-run", out.getvalue())
      self.assertEqual((repo / "AGENTS.md").read_text(), orig_agents)
      self.assertTrue((repo / ".agents" / "rules" / "antigravity-rtk-rules.md").exists())

  def test_sync_agents_applies_and_skips_dirty(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
      catalog, repo, rules_dir, canonical_agents = self._setup_fixture(Path(tmp))
      out = io.StringIO()
      with redirect_stdout(out):
        rc = batch.main(
          [
            "--catalog", str(catalog),
            "sync-agents",
            "--rules-dir", str(rules_dir),
            "--canonical-agents", str(canonical_agents),
          ]
        )
      self.assertEqual(rc, 0)
      text = out.getvalue()
      self.assertIn("updated", text)
      self.assertIn("Skill frontmatter warnings:", text)

      agents_text = (repo / "AGENTS.md").read_text()
      self.assertIn("canonical rtk", agents_text)
      self.assertIn("canonical context7", agents_text)
      self.assertIn("canonical uv-rules", agents_text)
      self.assertIn("canonical taplo-rules", agents_text)
      self.assertIn("keep me", agents_text)

      repo_rules = repo / ".agents" / "rules"
      self.assertFalse((repo_rules / "antigravity-rtk-rules.md").exists())
      self.assertTrue((repo_rules / "demo-project.md").is_file())
      self.assertTrue((repo_rules / "uv-rules.md").is_symlink())
      self.assertTrue((repo_rules / "taplo-rules.md").is_symlink())
      self.assertTrue((repo_rules / "serena.md").is_symlink())

      cat_text = (repo / ".agents" / "skills_catalog.md").read_text()
      self.assertIn("Curated desc | `task alpha`", cat_text)
      self.assertIn("skills/beta/SKILL.md", cat_text)

      gi_text = (repo / ".gitignore").read_text()
      self.assertIn("!.agents/skills_catalog.md", gi_text)
      self.assertNotIn(".codegraph/\n", gi_text)

      # Dirty skip check (repo now has uncommitted sync changes)
      out2 = io.StringIO()
      with redirect_stdout(out2):
        rc2 = batch.main(
          [
            "--catalog", str(catalog),
            "sync-agents",
            "--rules-dir", str(rules_dir),
            "--canonical-agents", str(canonical_agents),
          ]
        )
      self.assertEqual(rc2, 0)
      self.assertIn("skipped (dirty)", out2.getvalue())


class RunSkillTests(unittest.TestCase):
  def test_missing_action_requires_selector(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
      catalog = Path(tmp) / "repos.toml"
      catalog.write_text('[settings]\nroot = "."\n\n[actions]\n\n# --- repos ---\n', encoding="utf-8")
      err = io.StringIO()
      with redirect_stderr(err):
        rc = batch.main(["--catalog", str(catalog), "run-skill", "unknown-skill"])
      self.assertEqual(rc, 2)
      self.assertIn("Specify --action, --tag, or --repo", err.getvalue())

  def test_dry_run_and_mocked_agy_invocation(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
      tmp_path = Path(tmp)
      root = tmp_path / "repos"
      repo = root / "tfa"
      repo.mkdir(parents=True)
      subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
      subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
      subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
      (repo / "README.md").write_text("hi\n", encoding="utf-8")
      subprocess.run(["git", "add", "."], cwd=repo, check=True)
      subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)

      catalog = tmp_path / "repos.toml"
      catalog.write_text(
        f'[settings]\nroot = "{root}"\n\n'
        f'[actions.sync-agents]\ntags = ["agents"]\n\n'
        f'# --- repos ---\n\n'
        f'[repos.tfa]\ntags = ["agents"]\n',
        encoding="utf-8",
      )
      log_dir = tmp_path / "logs"

      # Dry run should not call _run_cmd
      out = io.StringIO()
      with mock.patch.object(batch, "_run_cmd") as m_run, redirect_stdout(out):
        rc = batch.main(["--catalog", str(catalog), "run-skill", "sync-agents", "--dry-run"])
      self.assertEqual(rc, 0)
      m_run.assert_not_called()
      self.assertIn("dry-run", out.getvalue())

      # Live mocked invocation
      captured_cmds: list[list[str]] = []

      def fake_run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        captured_cmds.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, "done\n", "")

      out2 = io.StringIO()
      with mock.patch.object(batch, "_run_cmd", side_effect=fake_run), redirect_stdout(out2):
        rc2 = batch.main(
          [
            "--catalog", str(catalog),
            "run-skill",
            "sync-agents",
            "--model", "flash",
            "--log-dir", str(log_dir),
          ]
        )
      self.assertEqual(rc2, 0)
      self.assertEqual(len(captured_cmds), 1)
      cmd = captured_cmds[0]
      self.assertEqual(cmd[:7], ["agy", "-p", "--mode", "auto", "--print-timeout", "300s", "--model"])
      self.assertIn("Do not commit or push changes.", cmd[-1])
      self.assertEqual((log_dir / "tfa.log").read_text(), "done\n")


if __name__ == "__main__":
  unittest.main()
