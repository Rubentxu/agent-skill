"""Optional architecture guidance never changes Backlog's ordinary behavior."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("backlog_groma_router", ROOT / "scripts/affordances.py")
router = importlib.util.module_from_spec(sp)
sys.modules[sp.name] = router
sp.loader.exec_module(router)


def session(intent, **kw):
    state = {"intent": intent, "mode": "read", "basis": "observed",
             "cli": "available", "project": "initialized",
             "task": {"id": "TASK-12", "isReady": True}}
    state.update(kw)
    return state


class GromaRouterTests(unittest.TestCase):
    def test_missing_groma_does_not_block_backlog(self):
        regular = router.affordances(session("triage", groma="missing"))
        self.assertEqual(regular["decision"], "READY")
        self.assertEqual(regular["lenses"], ["triage"])
        self.assertNotIn("inspect-architecture", [x["rel"] for x in regular["_links"]])

    def test_architecture_without_groma_is_discovery_only(self):
        result = router.affordances(session("architecture", groma="missing"))
        self.assertEqual(result["decision"], "DISCOVER")
        self.assertEqual(result["_links"][0]["rel"], "inspect-groma")

    def test_architecture_can_be_inspected_without_backlog(self):
        result = router.affordances(session("architecture", cli="missing",
                                           project="absent", groma="available"))
        self.assertEqual(result["lenses"], ["groma-architecture"])
        self.assertEqual(result["decision"], "READY")
        self.assertIn(["groma", "view", "--plain"], result["suggested_reads"])
        self.assertNotIn(["backlog", "instructions", "overview"], result["suggested_reads"])

    def test_task_mapping_needs_both_tools(self):
        a = router.affordances(session("map-task", groma="available", cli="missing"))
        b = router.affordances(session("map-task", groma="missing", cli="available"))
        self.assertEqual(a["decision"], "DISCOVER")
        self.assertEqual(b["decision"], "DISCOVER")

    def test_task_mapping_uses_official_backlog_guide(self):
        result = router.affordances(session("map-task", groma="available",
                                           mode="propose"))
        self.assertEqual(result["decision"], "PROPOSE_ONLY")
        self.assertEqual(result["lenses"], ["groma-task-linking"])
        self.assertIn(["groma", "agent-instructions", "backlog"], result["suggested_reads"])
        self.assertIn("plan-groma-task-links", [x["rel"] for x in result["_links"]])

    def test_unknown_task_id_requires_real_backlog_view(self):
        result = router.affordances(session("map-task", groma="available", task={}))
        self.assertEqual(result["decision"], "INSPECT_MORE")
        self.assertIn("select-task", [x["rel"] for x in result["_links"]])

    def test_normal_execution_offers_groma_only_when_observed(self):
        a = router.affordances(session("execute"))
        b = router.affordances(session("execute", groma="available"))
        self.assertNotIn("inspect-architecture", [x["rel"] for x in a["_links"]])
        self.assertIn("inspect-architecture", [x["rel"] for x in b["_links"]])
        self.assertEqual(a["decision"], b["decision"])

    def test_invalid_availability_is_rejected(self):
        with self.assertRaises(ValueError):
            router.affordances(session("architecture", groma="probably"))


if __name__ == "__main__":
    unittest.main()
