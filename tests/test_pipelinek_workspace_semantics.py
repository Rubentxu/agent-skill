"""Fitness del contrato RP-034 en la skill pipelinek-local-ci."""
from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "pipelinek-local-ci"


class PipelineKWorkspaceSemanticsTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (SKILL / relative).read_text(encoding="utf-8")

    def test_skill_routes_workspace_reference(self):
        entry = self.read("SKILL.md")
        self.assertIn("09-workspaces-and-execution-location.md", entry)
        self.assertIn("Workspace local-first explícito", entry)

    def test_default_run_is_invocation_directory_first(self):
        loop = self.read("references/02-agentic-loop.md")
        default = loop.split("## Run observable — default local-first", 1)[1]
        default = default.split("## Workspace explícito", 1)[0]
        self.assertIn('cd "$root"', default)
        self.assertIn("pipelinek run", default)
        self.assertNotIn("--workspace", default)

    def test_pipeline_path_is_not_workspace_authority(self):
        contract = self.read("references/09-workspaces-and-execution-location.md")
        self.assertIn("PipelineDefinitionPath != WorkspaceRoot", contract)
        self.assertIn("ownership           = Attached", contract)
        self.assertIn("--isolated", contract)
        self.assertIn("mutuamente excluyentes", contract)

    def test_attached_root_destructive_safety_is_pinned(self):
        contract = self.read("references/09-workspaces-and-execution-location.md")
        self.assertIn("fail closed por defecto", contract)
        self.assertIn("Nunca deduzcas ownership porque exista `.git`", contract)

    def test_evals_cover_workspace_regressions(self):
        evals = self.read("tests/skill-evals.md")
        for case in (
            "Workspace default",
            "Pipeline externo",
            "Workspace override",
            "Isolated",
            "Root cleanup Attached",
            "Control root",
        ):
            self.assertIn(case, evals)


if __name__ == "__main__":
    unittest.main()
