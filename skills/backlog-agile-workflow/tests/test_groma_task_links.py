"""Contract of task-link updates: exact IDs, no full-list replacement loss."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("backlog_groma_links", ROOT / "scripts/groma_task_links.py")
links = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = links
spec.loader.exec_module(links)


def fixture():
    return {
        "schemaVersion": 1, "kind": "groma-task-link-input",
        "task": {"id": "BACK-41",
                 "modifiedFiles": ["src/orders.rs"],
                 "references": ["docs/ROADMAP.md#R2.W4", "component-old", "ADR-04"]},
        "changedFiles": ["src/stock.rs", "groma/systems/shop.md"],
        "confirmedElementIds": ["stock-component"],
        "replacements": [{"old": "component-old", "new": "order-component"}],
    }


class TaskLinkTests(unittest.TestCase):
    def test_preserves_full_modified_file_list_and_private_path(self):
        r = links.plan(fixture())
        self.assertEqual(r["fullModifiedFiles"],
                         ["src/orders.rs", "src/stock.rs", "groma/systems/shop.md"])
        self.assertEqual(r["suggestedArgv"][0][-6:],
                         ["--modified-file", "src/orders.rs", "--modified-file", "src/stock.rs",
                          "--modified-file", "groma/systems/shop.md"])
        self.assertEqual(r["status"], "PROPOSAL_ONLY")

    def test_preserves_roadmap_and_adr_references_while_replacing_id(self):
        r = links.plan(fixture())
        self.assertEqual(r["removedRefs"], ["component-old"])
        self.assertEqual(r["addedRefs"], ["order-component", "stock-component"])
        self.assertEqual(r["fullReferences"],
                         ["docs/ROADMAP.md#R2.W4", "ADR-04", "order-component", "stock-component"])

    def test_idempotent_repeated_proposal(self):
        start = fixture()
        r = links.plan(start)
        later = fixture()
        later["task"]["modifiedFiles"] = r["fullModifiedFiles"]
        later["task"]["references"] = r["fullReferences"]
        later["replacements"] = []
        self.assertEqual(links.plan(later)["status"], "NO_CHANGE")

    def test_no_mutation_and_no_execution(self):
        data = fixture()
        before = copy.deepcopy(data)
        self.assertEqual(links.plan(data), links.plan(data))
        self.assertEqual(data, before)
        self.assertTrue(all(argv[0] == "backlog" for argv in links.plan(data)["suggestedArgv"]))

    def test_missing_old_id_must_be_inspected(self):
        d = fixture()
        d["replacements"][0]["old"] = "does-not-exist"
        with self.assertRaises(ValueError):
            links.plan(d)

    def test_traversal_or_shell_control_rejected(self):
        for p in ("../secret.md", "/etc/passwd", "src/x\n--status=Done", "src//a"):
            d = fixture()
            d["changedFiles"] = [p]
            with self.subTest(path=p), self.assertRaises(ValueError):
                links.plan(d)

    def test_invented_architecture_id_rejected(self):
        d = fixture()
        d["confirmedElementIds"] = ["unknown relationship ->"]
        with self.assertRaises(ValueError):
            links.plan(d)

    def test_no_implicit_ownership_from_changed_file(self):
        d = fixture()
        d["confirmedElementIds"] = []
        d["replacements"] = []
        out = links.plan(d)
        self.assertEqual(out["addedRefs"], [])
        self.assertTrue(out["addedFiles"])


if __name__ == "__main__":
    unittest.main()
