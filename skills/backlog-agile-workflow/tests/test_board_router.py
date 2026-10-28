"""Minimal navigation contracts for Kanban CRUD."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("kanban_nav", ROOT / "scripts/affordances.py")
router = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = router
spec.loader.exec_module(router)


def state(intent, task=None, mode="apply", **kwargs):
    data = {"intent": intent, "cli": "available", "project": "initialized",
            "basis": "observed", "mode": mode,
            "config": {"autoCommit": False, "remoteOperations": False,
                       "bypassGitHooks": False, "onStatusChange": False}}
    if task is not None:
        data["task"] = task
    data.update(kwargs)
    return data


class BoardRoutingTests(unittest.TestCase):
    def test_create_routes_lens_without_task_id(self):
        x = router.affordances(state("create-task"))
        self.assertEqual(x["lenses"], ["board-create"])
        self.assertEqual(x["decision"], "PROPOSE_ONLY")
        self.assertIn(["backlog", "task", "list", "--json"], x["suggested_reads"])

    def test_move_needs_observed_id(self):
        x = router.affordances(state("move-task"))
        self.assertEqual(x["decision"], "INSPECT_MORE")
        self.assertIn("select-task", [i["rel"] for i in x["_links"]])

    def test_move_archived_blocked_even_when_requested(self):
        x = router.affordances(state("move-task", task={"id": "TASK-10", "archived": True}))
        self.assertEqual(x["decision"], "BLOCKED")

    def test_archive_unknown_state_requires_view(self):
        x = router.affordances(state("archive-task", task={"id": "TASK-10"}))
        self.assertEqual(x["decision"], "INSPECT_MORE")

    def test_archived_archival_and_active_restoration_idempotent(self):
        a = router.affordances(state("archive-task", task={"id": "TASK-10", "archived": True}))
        b = router.affordances(state("restore-task", task={"id": "TASK-10", "archived": False}))
        self.assertEqual(a["decision"], "KEEP_AS_IS")
        self.assertEqual(b["decision"], "KEEP_AS_IS")

    def test_archival_and_restoration_are_proposals(self):
        for intent, archived in (("archive-task", False), ("restore-task", True)):
            x = router.affordances(state(intent, task={"id": "TASK-10", "archived": archived}))
            self.assertEqual(x["decision"], "PROPOSE_ONLY")
            self.assertIn("plan-board-operation", [i["rel"] for i in x["_links"]])

    def test_delete_never_authorized_by_router(self):
        x = router.affordances(state("delete-task", task={"id": "TASK-10", "archived": True}))
        self.assertEqual(x["decision"], "BLOCKED")
        self.assertNotIn("propose-cli-write", [i["rel"] for i in x["_links"]])

    def test_missing_cli_no_crud_write(self):
        x = router.affordances(state("create-task", cli="missing"))
        self.assertEqual(x["decision"], "DISCOVER")

    def test_read_can_browse_board_without_writes(self):
        x = router.affordances(state("archive-task", task={"id": "TASK-10", "archived": False}, mode="read"))
        self.assertEqual(x["decision"], "READY")
        self.assertEqual(x["lenses"], ["board-archive-restore"])


if __name__ == "__main__":
    unittest.main()
