"""Commit trace references are review hints, not proofs of implementation."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "scripts/commit_trace.py"
spec = importlib.util.spec_from_file_location("backlog_commit_trace", p)
trace = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = trace
spec.loader.exec_module(trace)

SHA1 = "a" * 40
SHA2 = "b" * 40


def packet():
    return json.loads((ROOT / "examples/spec-packet.json").read_text(encoding="utf-8"))


def entry(sha=SHA1, refs="Roadmap-Block: R1.W1"):
    return {"sha": sha, "message": ("feat: finish a vertical slice\n\n"
            + refs + "\nImplementation: extracted state decision\n"
            + "Verification: unit tests PASS on this commit")}


class CommitTraceTests(unittest.TestCase):
    def test_exact_roadmap_ref_matches_without_cli_task(self):
        d = trace.index({"schemaVersion": 1, "kind": "commit-messages",
                         "commits": [entry()]}, packet())
        self.assertEqual(d["matches"]["R1.W1"][0]["sha"], SHA1)
        self.assertEqual(d["matches"]["R1.W1"][0]["status"], "REVIEW_ONLY")

    def test_nontrailer_body_is_not_historical_evidence(self):
        e = entry(refs="Roadmap-Block: R1.W1\n\nIn unrelated prose")
        d = trace.index({"schemaVersion": 1, "kind": "commit-messages",
                         "commits": [e]}, packet())
        self.assertEqual(d["matches"]["R1.W1"], [])

    def test_incomplete_trailers_are_not_matches(self):
        e = entry()
        e["message"] = "feat: refactor\n\nRoadmap-Block: R1.W1"
        d = trace.index({"schemaVersion": 1, "kind": "commit-messages",
                         "commits": [e]}, packet())
        self.assertEqual(d["matches"]["R1.W1"], [])
        self.assertTrue(d["warnings"])

    def test_ambiguous_fragment_never_matched_by_short_id(self):
        p = packet()
        p["tasks"][2]["sourceRef"] = "alt/OTHER.md#R1.W1"
        d = trace.index({"schemaVersion": 1, "kind": "commit-messages",
                         "commits": [entry()]}, p)
        self.assertEqual(d["matches"]["R1.W1"], [])

    def test_qualified_id_resolves_ambiguity(self):
        p = packet()
        p["tasks"][2]["sourceRef"] = "alt/OTHER.md#R1.W1"
        d = trace.index({"schemaVersion": 1, "kind": "commit-messages",
                         "commits": [entry(refs="Roadmap-Block: docs/ROADMAP.md#R1.W1")]}, p)
        self.assertEqual(d["matches"]["R1.W1"][0]["sha"], SHA1)

    def test_multiple_commit_evidence_preserved(self):
        d = trace.index({"schemaVersion": 1, "kind": "commit-messages",
                         "commits": [entry(), entry(SHA2)]}, packet())
        self.assertEqual(len(d["matches"]["R1.W1"]), 2)

    def test_duplicate_sha_refused(self):
        with self.assertRaises(ValueError):
            trace.index({"schemaVersion": 1, "kind": "commit-messages",
                         "commits": [entry(), entry()]}, packet())


if __name__ == "__main__":
    unittest.main()
