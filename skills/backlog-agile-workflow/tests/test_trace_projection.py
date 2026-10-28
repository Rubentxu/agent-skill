"""Commit evidence can block duplicate task creation, never certify completion."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sp = importlib.util.spec_from_file_location("spec_with_commit_provenance", ROOT / "scripts/spec_projection.py")
module = importlib.util.module_from_spec(sp)
sys.modules[sp.name] = module
sp.loader.exec_module(module)


def fixtures():
    return (json.loads((ROOT / "examples/spec-packet.json").read_text(encoding="utf-8")),
            json.loads((ROOT / "examples/spec-existing-tasks.json").read_text(encoding="utf-8")))


def evidence(backlog_ids=None):
    return {"schemaVersion": 1, "kind": "implementation-references",
            "matches": {"R1.W1": [
                {"sha": "a" * 40, "backlogTaskIds": backlog_ids or [],
                 "implementation": ["extracted domain rule"],
                 "verification": ["NOT_RUN"], "status": "REVIEW_ONLY"}]},
            "warnings": []}


class CommitAwareProjectionTests(unittest.TestCase):
    def test_implementation_requires_review_not_new_task(self):
        packet, snapshot = fixtures()
        result = module.project(packet, snapshot, evidence())
        task = next(x for x in result["actions"] if x["key"] == "R1.W1")
        self.assertEqual(task["disposition"], "REVIEW_IMPLEMENTATION")
        self.assertEqual(task["linkedCommitSHAs"], ["a" * 40])
        self.assertNotIn("PROPOSE_CREATE", [task["disposition"]])

    def test_commit_without_evidence_keeps_original_proposal(self):
        packet, snapshot = fixtures()
        task = next(x for x in module.project(packet, snapshot)["actions"]
                    if x["key"] == "R1.W1")
        self.assertEqual(task["disposition"], "PROPOSE_CREATE")

    def test_existing_task_id_from_commit_blocks_duplicate(self):
        packet, snapshot = fixtures()
        result = module.project(packet, snapshot, evidence(["TASK-1"]))
        item = next(x for x in result["actions"] if x["key"] == "R1.W1")
        self.assertEqual(item["disposition"], "REVIEW_POSSIBLE_DUPLICATE")

    def test_bad_commit_snapshot_fails_closed(self):
        packet, snapshot = fixtures()
        with self.assertRaises(ValueError):
            module.project(packet, snapshot, {"kind": "implementation-references",
                                             "schemaVersion": 2, "matches": {}})

    def test_unknown_key_fails_closed(self):
        packet, snapshot = fixtures()
        bad = evidence()
        bad["matches"]["R9.W7"] = []
        with self.assertRaises(ValueError):
            module.project(packet, snapshot, bad)

    def test_result_never_claims_done_from_sha(self):
        packet, snapshot = fixtures()
        result = module.project(packet, snapshot, evidence())
        self.assertEqual(result["status"], "PROPOSAL_ONLY")
        self.assertTrue(any("no completion inferred" in s for s in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
