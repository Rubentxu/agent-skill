"""Navigation is context-sensitive; skill names cannot fabricate installation."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("backlog_specialist_handoff_router",
                                            ROOT / "scripts/affordances.py")
router = importlib.util.module_from_spec(sp)
sys.modules[sp.name] = router
sp.loader.exec_module(router)


def session(intent, skills=()):
    return {"intent": intent, "mode": "read", "basis": "observed",
            "cli": "available", "project": "initialized",
            "available_skills": list(skills),
            "task": {"id": "TASK-10", "isReady": True, "archived": False,
                     "acceptanceCriteriaCount": 1, "acceptanceCriteriaCompleted": 1,
                     "definitionOfDoneCount": 1, "definitionOfDoneCompleted": 1}}


class HandoffTests(unittest.TestCase):
    def test_git_hygiene_can_run_without_backlog_cli(self):
        state = {"intent": "git-hygiene", "mode": "propose", "basis": "observed",
                 "cli": "missing", "project": "absent"}
        result = router.affordances(state)
        self.assertEqual(result["decision"], "PROPOSE_ONLY")
        self.assertEqual(result["lenses"], ["git-artifact-hygiene"])
        self.assertIn("audit-git-index", [x["rel"] for x in result["_links"]])
        self.assertEqual(result["suggested_reads"], [])

    def test_commit_trace_without_cli(self):
        result = router.affordances({"intent": "trace", "basis": "observed",
                                     "cli": "missing", "project": "absent"})
        self.assertEqual(result["lenses"], ["commit-traceability"])
        self.assertIn("inspect-commit-trailers", [x["rel"] for x in result["_links"]])

    def test_all_four_specialists_are_discovered_when_available(self):
        keys = ["delivery-first-testing", "pipelinek-local-ci",
                "pure-functional-design", "agent-secretless"]
        result = router.affordances(session("execute", keys))
        found = {x["skill_id"] for x in result["_links"] if x["rel"] == "delegate-skill"}
        self.assertEqual(found, set(keys))

    def test_no_installed_specialists_no_delegations(self):
        result = router.affordances(session("execute"))
        self.assertFalse([x for x in result["_links"] if x["rel"] == "delegate-skill"])

    def test_testing_only_for_verification(self):
        result = router.affordances(session("verify", ["delivery-first-testing"]))
        self.assertEqual([x["skill_id"] for x in result["_links"]
                          if x["rel"] == "delegate-skill"], ["delivery-first-testing"])


if __name__ == "__main__":
    unittest.main()
