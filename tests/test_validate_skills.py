"""Pruebas del validador, sin dependencias de terceros ni red."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_skills.py"
spec = importlib.util.spec_from_file_location("validate_skills", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class ValidateSkillsTests(unittest.TestCase):
    def make_skill(self, parent: Path, name: str = "sample-skill") -> Path:
        skill = parent / name
        skill.mkdir()
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: A usable sample skill.\n---\n\n"
            "# Sample\n[Reference](references/guide.md)\n",
            encoding="utf-8",
        )
        (skill / "references").mkdir()
        (skill / "references" / "guide.md").write_text("# Guide\n", encoding="utf-8")
        return skill

    def test_valid_self_contained_skill(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(validator.validate_skill(self.make_skill(Path(temp))), [])

    def test_reject_wrong_front_matter_name(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = self.make_skill(Path(temp))
            entry = skill / "SKILL.md"
            entry.write_text(entry.read_text().replace("name: sample-skill", "name: other-skill"))
            self.assertTrue(any("name debe coincidir" in e for e in validator.validate_skill(skill)))

    def test_reject_missing_and_outside_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            skill = self.make_skill(parent)
            entry = skill / "SKILL.md"
            entry.write_text(entry.read_text() + "[Missing](references/no.md)\n[Outside](../other.md)\n")
            errors = validator.validate_skill(skill)
            self.assertEqual(len([e for e in errors if "enlace local roto" in e]), 2)


if __name__ == "__main__":
    unittest.main()
