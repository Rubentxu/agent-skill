"""Context-aware intents remain pure navigation; no CLI/Git effects."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("backlog_context_navigation", ROOT / "scripts/affordances.py")
nav = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = nav
spec.loader.exec_module(nav)

def state(intent, task=None, mode="read"):
    result = {
        "intent": intent, "basis": "observed", "cli": "available",
        "project": "initialized", "mode": mode,
        "config": {"autoCommit": False, "remoteOperations": False,
                   "bypassGitHooks": False, "onStatusChange": False},
    }
    if task is not None:
        result["task"] = task
    return result

class ContextRouterTests(unittest.TestCase):
    def test_alignment_navigates_without_claiming_completion(self):
        r = nav.affordances(state("align-work"))
        self.assertEqual(r["status"], "NAVIGATION_ONLY")
        self.assertEqual(r["decision"], "READY")
        self.assertIn("work-alignment", r["lenses"])
        self.assertIn("inspect-work", [x["rel"] for x in r["_links"]])

    def test_unplanned_work_is_proposed_only(self):
        r = nav.affordances(state("unplanned-work", mode="propose"))
        self.assertEqual(r["decision"], "PROPOSE_ONLY")
        self.assertEqual(r["lenses"], ["unplanned-work"])
        self.assertIn(["backlog", "task", "list", "--json"], r["suggested_reads"])

    def test_dependencies_require_task_identity(self):
        absent = nav.affordances(state("manage-dependencies"))
        self.assertEqual(absent["decision"], "INSPECT_MORE")
        actual = nav.affordances(state("manage-dependencies", {"id": "TASK-10", "archived": False}))
        self.assertEqual(actual["decision"], "READY")
        self.assertIn("inspect-dependency-graph", [x["rel"] for x in actual["_links"]])

    def test_epic_is_optional_and_does_not_create_hierarchy(self):
        r = nav.affordances(state("manage-epic"))
        self.assertEqual(r["lenses"], ["epic-management"])
        self.assertEqual(r["decision"], "READY")
        self.assertNotIn("propose-cli-write", [x["rel"] for x in r["_links"]])

    def test_missing_cli_reverts_to_discovery(self):
        s = state("align-work")
        s["cli"] = "missing"
        self.assertEqual(nav.affordances(s)["decision"], "DISCOVER")

if __name__ == "__main__":
    unittest.main()
