"""Focused tests of safe CRUD proposals; no Backlog.md runtime needed."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("kanban_board_crud", ROOT / "scripts/board_crud.py")
board = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = board
spec.loader.exec_module(board)


def sample(name):
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


def task():
    return {"id": "BACK-21", "status": "In Progress", "archived": False,
            "isReady": True, "acceptanceCriteriaCount": 2, "acceptanceCriteriaCompleted": 2,
            "definitionOfDoneCount": 1, "definitionOfDoneCompleted": 1,
            "finalSummaryRecorded": True}


def state(op="transition", **overrides):
    result = {"schemaVersion": 1, "kind": "board-operation", "operation": op,
              "statuses": ["To Do", "In Progress", "Done"], "terminalStatus": "Done",
              "task": task(), "targetStatus": "Done", "gateResult": "PASS",
              "config": {"autoCommit": False, "remoteOperations": False,
                         "bypassGitHooks": False, "onStatusChange": False},
              "authorized": False}
    result.update(overrides)
    return result


class BoardCrudTests(unittest.TestCase):
    def test_create_is_proposal_and_preserves_repeated_acceptance(self):
        r = board.plan(sample("board-create.json"))
        self.assertEqual(r["decision"], "PROPOSE_ONLY")
        self.assertEqual(r["suggestedArgv"][:3], ["backlog", "task", "create"])
        self.assertEqual(r["suggestedArgv"].count("--ac"), 2)
        self.assertIn("docs/ROADMAP.md#R2.W1", r["suggestedArgv"])

    def test_create_requires_review_and_ac(self):
        first = sample("board-create.json")
        first["duplicateReview"] = "unknown"
        self.assertEqual(board.plan(first)["decision"], "INSPECT_MORE")
        first["duplicateReview"] = "clear"
        first["newTask"]["acceptanceCriteria"] = []
        self.assertEqual(board.plan(first)["decision"], "BLOCKED")

    def test_create_fails_on_unknown_column(self):
        s = sample("board-create.json")
        s["newTask"]["status"] = "Already Done"
        self.assertEqual(board.plan(s)["decision"], "BLOCKED")

    def test_transition_to_done_requires_verification(self):
        r = board.plan(sample("board-transition.json"))
        self.assertEqual(r["suggestedArgv"], ["backlog", "task", "edit", "TASK-7", "-s", "Done"])
        for override in ({"gateResult": "NOT_RUN"}, {"task": {**task(), "acceptanceCriteriaCompleted": 1}},
                         {"task": {**task(), "finalSummaryRecorded": False}}):
            with self.subTest(override=override):
                self.assertEqual(board.plan(state(**override))["decision"], "BLOCKED")

    def test_transition_uses_configured_custom_statuses(self):
        s = state(statuses=["Pendiente", "En curso", "Comprobado"],
                  terminalStatus="Comprobado", task={**task(), "status": "En curso"},
                  targetStatus="Comprobado", authorized=True)
        self.assertEqual(board.plan(s)["decision"], "AUTHORIZED_ACTION")

    def test_transition_no_change_and_archived_refusal(self):
        self.assertEqual(board.plan(state(targetStatus="In Progress"))["decision"], "NO_CHANGE")
        self.assertEqual(board.plan(state(task={**task(), "archived": True}))["decision"], "BLOCKED")

    def test_unknown_ready_blocks_start(self):
        s = state(task={**task(), "status": "To Do", "isReady": False}, targetStatus="In Progress")
        self.assertEqual(board.plan(s)["decision"], "INSPECT_MORE")

    def test_archive_finished_vs_cancelled(self):
        s = state("archive", task={**task(), "status": "Done"}, archiveReason="completed")
        self.assertEqual(board.plan(s)["suggestedArgv"], ["backlog", "task", "archive", "BACK-21"])
        unfinished = sample("board-archive.json")
        self.assertEqual(board.plan(unfinished)["decision"], "PROPOSE_ONLY")
        unfinished["dependencyImpact"] = "unknown"
        self.assertEqual(board.plan(unfinished)["decision"], "INSPECT_MORE")

    def test_archive_does_not_imply_done(self):
        s = sample("board-archive.json")
        self.assertEqual(s["task"]["status"], "To Do")
        self.assertEqual(board.plan(s)["suggestedArgv"], ["backlog", "task", "archive", "TASK-8"])

    def test_archive_requires_summary_and_is_idempotent(self):
        s = sample("board-archive.json")
        s["task"]["finalSummaryRecorded"] = False
        self.assertEqual(board.plan(s)["decision"], "INSPECT_MORE")
        s["task"]["archived"] = True
        self.assertEqual(board.plan(s)["decision"], "NO_CHANGE")

    def test_restore_keeps_identity_and_status(self):
        s = state("restore", task={**task(), "archived": True, "status": "In Progress"})
        self.assertEqual(board.plan(s)["suggestedArgv"], ["backlog", "task", "restore", "BACK-21"])
        s["task"]["archived"] = False
        self.assertEqual(board.plan(s)["decision"], "NO_CHANGE")

    def test_delete_never_offered(self):
        s = state("delete", authorized=True)
        r = board.plan(s)
        self.assertEqual(r["decision"], "BLOCKED")
        self.assertIsNone(r["suggestedArgv"])

    def test_effects_apply_to_creation_and_restoration(self):
        for s in (sample("board-create.json"), state("restore", task={**task(), "archived": True})):
            with self.subTest(operation=s["operation"]):
                s["config"]["onStatusChange"] = True
                self.assertEqual(board.plan(s)["decision"], "BLOCKED")
                s["effectsAcknowledged"] = True
                self.assertIn(board.plan(s)["decision"], {"PROPOSE_ONLY", "AUTHORIZED_ACTION"})

    def test_unknown_config_blocks_write(self):
        self.assertEqual(board.plan(state(config={}))["decision"], "INSPECT_MORE")

    def test_no_mutation_and_determinism(self):
        s = sample("board-create.json")
        old = copy.deepcopy(s)
        self.assertEqual(board.plan(s), board.plan(s))
        self.assertEqual(s, old)

    def test_injection_and_invalid_schema_rejected(self):
        for s in (state(task={**task(), "id": "BACK-1; rm -rf /"}),
                  state(targetStatus="Done; echo unsafe"),
                  state(statuses=["Done", "Done"])):
            with self.subTest(s=s):
                if s["targetStatus"].startswith("Done;"):
                    self.assertEqual(board.plan(s)["decision"], "BLOCKED")
                else:
                    with self.assertRaises(ValueError):
                        board.plan(s)


if __name__ == "__main__":
    unittest.main()
