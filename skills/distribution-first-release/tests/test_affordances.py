from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "affordances.py"
spec = importlib.util.spec_from_file_location("release_router", SCRIPT)
router = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = router
spec.loader.exec_module(router)


def state(**changes):
    result = dict(
        intent="release", product="cli", inventory="ready", basis="current",
        signals=["release"], git_artifacts="clean", archive_confusion=False,
        asset_set="complete", package="passed", consumer="passed",
        integrity="passed", publication="not_run"
    )
    result.update(changes)
    return result


class RegistryTests(unittest.TestCase):
    def test_registry_ready_lenses(self):
        c = router.read_catalog()
        self.assertGreaterEqual(sum(x["status"] == "ready" for x in c.values()), 9)

    def test_planned_not_offered(self):
        self.assertEqual(router.read_catalog()["registry-contracts"]["status"], "planned")
        ids = [x["id"] for x in router.affordances(state(signals=["package"]))["lenses"]]
        self.assertNotIn("registry-contracts", ids)

    def test_every_action_path_exists_and_safe(self):
        for rel in router.ACTIONS.values():
            p = (ROOT / rel).resolve()
            self.assertTrue(p.is_file() and p.is_relative_to(ROOT.resolve()), rel)

    def test_duplicate_lens_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            j = json.loads(router.CATALOG.read_text())
            j["lenses"].append(j["lenses"][0])
            p = Path(td) / "lenses.json"
            p.write_text(json.dumps(j))
            with self.assertRaises(router.InvalidState):
                router.read_catalog(p)


class NavigationTests(unittest.TestCase):
    def action(self, **kw):
        return router.affordances(state(**kw))["recommended"]

    def test_catalog_never_executes(self):
        r = router.affordances({"intent": "catalog"})
        self.assertEqual((r["recommended"], r["status"]), ("list-lenses", "READY"))

    def test_unknown_product(self):
        self.assertEqual(self.action(product="unknown"), "inspect-product")

    def test_unknown_inventory(self):
        self.assertEqual(self.action(inventory="unknown"), "inspect-product")

    def test_stale_evidence(self):
        r = router.affordances(state(basis="stale"))
        self.assertEqual((r["recommended"], r["status"]), ("refresh-basis", "BLOCKED"))

    def test_git_bloated_first(self):
        self.assertEqual(self.action(git_artifacts="bloated"), "plan-git-hygiene")

    def test_cleanup_does_not_delete(self):
        self.assertIn(self.action(intent="cleanup"), {"assess-history", "plan-git-hygiene"})

    def test_archive_confusion(self):
        self.assertEqual(self.action(archive_confusion=True), "clarify-source-archives")

    def test_missing_asset_never_done(self):
        r = router.affordances(state(asset_set="incomplete", publication="passed"))
        self.assertEqual((r["recommended"], r["status"]), ("fix-asset-set", "FAILED"))

    def test_unexpected_asset_never_done(self):
        self.assertEqual(self.action(asset_set="unexpected"), "fix-asset-set")

    def test_unknown_asset_set(self):
        self.assertEqual(self.action(asset_set="unknown"), "inventory-assets")

    def test_failure_overrides_green(self):
        self.assertEqual(self.action(consumer="failed"), "investigate-failure")

    def test_blocked_is_not_pass(self):
        self.assertEqual(router.affordances(state(integrity="blocked"))["status"], "BLOCKED")

    def test_package_then_consumer_then_integrity(self):
        self.assertEqual(self.action(package="not_run"), "inspect-package")
        self.assertEqual(self.action(consumer="not_run"), "verify-consumer")
        self.assertEqual(self.action(integrity="not_run"), "verify-integrity")

    def test_publication_is_separate(self):
        self.assertEqual(self.action(publication="not_run"), "publish-or-check-release")

    def test_done_requires_all_observed(self):
        r = router.affordances(state(publication="passed"))
        self.assertEqual((r["recommended"], r["status"]), ("finish-release", "DONE"))
        self.assertIn("no tests executed", r["notice"])

    def test_skills_only_when_observed_available(self):
        r = router.affordances(state(signals=["release", "consumer"], available_skills=["delivery-first-testing"]))
        self.assertEqual(r["related_skills"][0]["id"], "delivery-first-testing")
        self.assertEqual(router.affordances(state())["related_skills"], [])

    def test_new_lens_is_proposal_only(self):
        r = router.affordances(state(signals=["unknown"]))
        self.assertEqual(r["discovery"][0]["rel"], "propose-lens")

    def test_invalid_signal(self):
        with self.assertRaises(router.InvalidState):
            router.affordances(state(signals=["unknown-tool"]))

    def test_invalid_boolean(self):
        with self.assertRaises(router.InvalidState):
            router.affordances(state(archive_confusion="yes"))

    def test_unknown_status_invalid(self):
        with self.assertRaises(router.InvalidState):
            router.affordances(state(publication="greenish"))

    def test_readonly_cli_example(self):
        p = ROOT / "examples" / "session-release.json"
        run = subprocess.run([sys.executable, str(SCRIPT), str(p)], text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout)["recommended"], "verify-consumer")

    def test_invalid_json_exit_2(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "-"], input="{",
                             text=True, capture_output=True)
        self.assertEqual(run.returncode, 2)
        self.assertIn("INVALID_STATE", run.stderr)


if __name__ == "__main__":
    unittest.main()
