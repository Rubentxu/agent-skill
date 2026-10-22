"""Regression policy checks for the CogniCode-only investigation skill.

These checks validate the SKILL and derived-workspace boundary. They do NOT
certify a live agent's use of CogniCode; those acceptance cases live in skill-evals.md.
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def source(relative: str) -> str:
    """Read ONLY the skill's own files, never a target repository."""
    path = (ROOT / relative).resolve(strict=True)
    if not path.is_relative_to(ROOT):
        raise AssertionError("test attempted to read outside the skill")
    return path.read_text(encoding="utf-8")


class CogniCodeOnlyContractTests(unittest.TestCase):
    def test_no_other_architecture_authority(self):
        policy = source("SKILL.md")
        contract = source("references/investigation-contract.md")
        for token in ("CogniCode CLI/MCP", "SUBAGENTES", "PROYECTORES",
                      "README", "ADR", "PARTIAL", "UNKNOWN"):
            with self.subTest(token=token):
                self.assertIn(token, policy + "\n" + contract)
        self.assertIn("Única", source("references/scan.md") + contract)

    def test_workspace_resolver_has_no_git_or_subprocess_call(self):
        program = source("scripts/workspace.py")
        tree = ast.parse(program)
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        names = {
            alias.name.split(".")[0]
            for item in imports
            for alias in item.names
        }
        self.assertNotIn("subprocess", names)
        self.assertNotIn("git_repository", program)
        self.assertIn("supplied_repository_root", program)

    def test_every_architecture_lens_inherits_code_only_contract(self):
        c4 = source("references/lenses/c4.md")
        self.assertIn("CogniCode CLI/MCP", c4)
        self.assertIn("No leer directamente", c4)
        for name in ("class", "use-case", "vertical-slice"):
            text = source(f"references/lenses/{name}.md")
            self.assertIn("CogniCode", text)
            self.assertIn("PLANNED", text)

    def test_scope_and_render_are_distinct(self):
        renderer = source("scripts/render_kroki.py")
        self.assertIn('src_rel[3] != "sources"', renderer)
        self.assertIn('dst_rel[3] != "renders"', renderer)
        self.assertIn("derived_root", renderer)
        self.assertIn("source_file", renderer)
        self.assertIn("enlace simbólico", renderer)
        self.assertIn("no recibe el checkout", source("references/projectors/structurizr-local.md"))

    def test_evals_have_all_six_negative_cases(self):
        tests = source("tests/skill-evals.md")
        for claim in ("X1", "X2", "X3", "X4", "X5", "X6"):
            with self.subTest(claim=claim):
                self.assertIn(claim, tests)
        for word in ("detalle", "insuficiente", "contradice", "ausente",
                     "subagentes", "proyector"):
            with self.subTest(word=word):
                self.assertIn(word, tests.lower())

    def test_no_misleading_old_documentary_instructions(self):
        all_guides = "\n".join(
            source(name) for name in (
                "SKILL.md", "references/scan.md", "references/evidence.md",
                "references/lenses/c4.md", "references/validate.md",
                "references/interpret.md", "references/formats/likec4-c4.md"
            )
        )
        for forbidden in (
            "Complementar con manifiestos",
            "inspección de manifiestos e IaC",
            "comparar las afirmaciones con código/manifiestos/docs/tests/trazas",
            "CogniCode y fuentes corroboradas",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, all_guides)


if __name__ == "__main__":
    unittest.main()
