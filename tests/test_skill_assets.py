"""Skill asset regression tests."""

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_skill_markdown_has_discoverable_frontmatter():
    """SKILL.md should be discoverable as a Codex-style skill."""
    content = _read("SKILL.md")

    assert content.startswith("---\n")
    _, frontmatter, body = content.split("---", 2)
    metadata = yaml.safe_load(frontmatter)

    assert metadata["name"] == "papercarator"
    assert "math-modeling" in metadata["description"]
    assert "paper generation" in metadata["description"]
    assert "Verification checklist" in body


def test_skill_docs_keep_analyze_first_protocol():
    """Agent-facing docs should keep the classify-then-run workflow visible."""
    skill_doc = _read("SKILL.md")
    claude_doc = _read("CLAUDE.md")
    integration_doc = _read("docs/skill_integration.md")

    assert "papercarator.cli analyze" in skill_doc
    assert "papercarator.cli analyze" in claude_doc
    assert "papercarator.cli analyze" in integration_doc
    assert "--no-github --no-vscode" in skill_doc
    assert "--no-github --no-vscode" in claude_doc


def test_skill_presets_disable_external_side_effects():
    """Skill presets should default to local artifact generation."""
    for config_path in ["configs/skill_codex.yaml", "configs/skill_claude.yaml"]:
        config = yaml.safe_load((ROOT / config_path).read_text(encoding="utf-8"))

        assert config["github_publisher"]["enabled"] is False
        assert config["vscode"]["enabled"] is False
        assert config["matlab"]["enabled"] is False
        assert config["solidworks"]["enabled"] is False
