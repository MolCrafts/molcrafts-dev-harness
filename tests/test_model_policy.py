"""
Structural guards for host-owned agent models and the impl speed contract.

Stdlib only: unittest + pathlib + re. Run with:

    python tests/test_model_policy.py
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

AGENTS_DIR = REPO_ROOT / "plugins" / "mol" / "agents"
SKILLS_DIR = REPO_ROOT / "plugins" / "mol" / "skills"
RULES_DIR = REPO_ROOT / "plugins" / "mol" / "rules"

VENDOR_MODEL = re.compile(r"(?i)\bmodel:\s*(opus|sonnet|haiku|inherit)\b")


def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip()
    return fm, m.group(2)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class ModelPolicyTests(unittest.TestCase):
    def test_agents_do_not_pin_a_model(self) -> None:
        agent_files = sorted(AGENTS_DIR.glob("*.md"))
        self.assertTrue(agent_files, f"no agents found under {AGENTS_DIR}")
        self.assertFalse(
            (AGENTS_DIR / "reviewer.md").exists(),
            "reviewer.md is an aggregator; /mol:review renders the verdict",
        )
        for path in agent_files:
            fm, _ = _split_frontmatter(_read(path))
            self.assertNotIn(
                "model",
                fm,
                f"{path.name} pins a model; the host assigns it",
            )

    def test_skills_do_not_dispatch_a_vendor_model(self) -> None:
        for path in SKILLS_DIR.glob("*/SKILL.md"):
            self.assertIsNone(
                VENDOR_MODEL.search(_read(path)),
                f"{path.parent.name} dispatches a vendor model name",
            )

    def test_implementer_agent_contract(self) -> None:
        path = AGENTS_DIR / "implementer.md"
        text = _read(path)
        fm, body = _split_frontmatter(text)
        self.assertEqual(
            fm.get("tools", "").replace(" ", ""),
            "Read,Grep,Glob,Bash,Write,Edit",
        )
        self.assertNotIn("model", fm)
        self.assertIn("RED", body)
        self.assertIn("Never edit test files", body)
        self.assertIn("mode: small", body)
        self.assertIn("no reverts", body.lower())

    def test_orchestration_speed_rules(self) -> None:
        design = _read(RULES_DIR / "agent-design.md")
        for heading in ("## Handoff packet", "## Verification tiers"):
            self.assertIn(heading, design)
        publish = _read(RULES_DIR / "git-publish.md")
        self.assertIn("Re-running after a failed gate", publish)
        implementer = _read(AGENTS_DIR / "implementer.md")
        self.assertIn("## Fix mode", implementer)
        self.assertNotIn(
            "Run `$META.build.check` on touched files",
            implementer,
        )

    def test_model_policy_rules_file(self) -> None:
        text = _read(RULES_DIR / "model-policy.md")
        for token in ("Advisor", "Orchestration", "MUST NOT author production"):
            self.assertIn(token, text)
        self.assertIn("Do not pin", text)
        self.assertIsNone(VENDOR_MODEL.search(text))

    def test_skill_wiring(self) -> None:
        impl = _read(SKILLS_DIR / "impl" / "SKILL.md")
        self.assertIn("`implementer`", impl)
        self.assertIn("mode: small", impl)
        self.assertIn("--chain", impl)
        self.assertIn("test_single", impl)
        self.assertIn("Do not invoke `/mol:simplify`", impl)
        self.assertIn("docs criterion", impl)
        self.assertIn("Do not invoke `/mol:close`", impl)
        self.assertIn("Do not invoke `/mol:perf`", impl)

        debug = _read(SKILLS_DIR / "debug" / "SKILL.md")
        self.assertIn("`implementer`", debug)
        self.assertIn("do **not** re-delegate", debug)
        self.assertIn("--diagnose-only", debug)
        self.assertIn("mode: fix", debug)

        impl_all = _read(SKILLS_DIR / "impl-all" / "SKILL.md")
        self.assertIn("`/mol:commit` once", impl_all)
        self.assertNotIn("model: haiku", impl_all)
        self.assertNotIn("/mol:commit -m", impl_all)
        self.assertNotIn("then `/mol:commit`", impl_all)
        self.assertIn("Do not invoke `/mol:close`", impl_all)

        spec = _read(SKILLS_DIR / "spec" / "SKILL.md")
        self.assertIn("Invoke `/mol:grill`", spec)
        self.assertIn("post-librarian", spec)
        self.assertIn("Do not grill again after persist", spec)
        discuss = _read(SKILLS_DIR / "discuss" / "SKILL.md")
        self.assertIn("Never auto-invoke `/mol:grill`", discuss)

        release = _read(SKILLS_DIR / "release" / "SKILL.md")
        self.assertIn('/mol:commit "release: v', release)
        self.assertNotIn('git commit -m "release:', release)

    def test_no_hardcoded_agent_counts_outside_json(self) -> None:
        pattern = re.compile(r"\b\d+ (?:single-axis )?agents\b")
        for rel in (
            "README.md",
            "plugins/mol/README.md",
            "plugins/mol/rules/agent-design.md",
        ):
            text = _read(REPO_ROOT / rel)
            match = pattern.search(text)
            self.assertIsNone(
                match,
                f"{rel} hardcodes an agent count ({match.group(0) if match else ''})",
            )


if __name__ == "__main__":
    unittest.main()
