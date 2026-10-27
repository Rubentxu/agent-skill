import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "affordances.py"
spec = importlib.util.spec_from_file_location("fp_skill_router", SCRIPT)
router = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = router
spec.loader.exec_module(router)


def session(signals=None, intent="refactor", language="rust", basis="observed", risk="routine"):
    return {"intent": intent, "language": language, "basis": basis,
            "signals": signals or [], "risk": risk}


class RouterTests(unittest.TestCase):
    def test_catalog_does_not_activate_planned(self):
        result = router.affordances({"intent": "catalog"})
        self.assertIn("distributed-effects", {x["id"] for x in result["available"]})
        self.assertEqual(result["lenses"], [])
        self.assertEqual(result["_links"], [])

    def test_unknown_basis_never_recommends_refactor(self):
        result = router.affordances(session(["side-effects"], basis="unknown"))
        self.assertEqual(result["lenses"], [])
        self.assertEqual(result["_links"][0]["rel"], "inspect-code")

    def test_stale_basis_requires_refresh(self):
        result = router.affordances(session(["large-service"], basis="stale"))
        self.assertEqual(result["_links"][0]["rel"], "refresh-basis")

    def test_unknown_language_blocks_language_specific_action(self):
        result = router.affordances(session(["invalid-state"], language="unknown"))
        self.assertEqual(result["_links"][0]["rel"], "identify-language")

    def test_rust_selects_methods_then_exactly_one_adapter(self):
        result = router.affordances(session(["large-service", "side-effects", "duplicate-logic"]))
        self.assertEqual([x["id"] for x in result["lenses"]],
                         ["effects-and-core", "vertical-slices", "responsibility-refactor", "language-rust"])
        self.assertTrue(all("href" in link for link in result["_links"] if link["rel"] == "read-lens"))

    def test_kotlin_state_model_chooses_domain_before_adt(self):
        result = router.affordances(session(["domain-ambiguity", "invalid-state", "nested-data"], language="kotlin", intent="design"))
        self.assertEqual([x["id"] for x in result["lenses"]],
                         ["domain-discovery", "adt-invariants", "algebraic-laws", "language-kotlin"])

    def test_no_signals_not_an_excuse_for_every_lens(self):
        result = router.affordances(session())
        self.assertEqual(result["lenses"], [])
        self.assertEqual(result["_links"][0]["rel"], "discover-signals")

    def test_planned_never_advertised_as_ready(self):
        result = router.affordances(session(["side-effects", "cross-context"], intent="design"))
        self.assertNotIn("distributed-effects", {x["id"] for x in result["lenses"]})

    def test_unknown_signals_fail_closed(self):
        with self.assertRaises(ValueError):
            router.affordances(session(["non-existent"]))

    def test_duplicate_signals_fail_closed(self):
        with self.assertRaises(ValueError):
            router.affordances(session(["large-service", "large-service"]))

    def test_all_ready_references_exist_and_are_contained(self):
        for entry in router._read_catalog():
            if entry["status"] == "ready":
                path = (ROOT / entry["playbook"]).resolve()
                self.assertTrue(path.is_file())
                self.assertTrue(path.is_relative_to(ROOT.resolve()))

    def test_router_is_deterministic(self):
        state = session(["side-effects", "large-service"], risk="critical")
        self.assertEqual(router.affordances(state), router.affordances(state))
        self.assertTrue(router.affordances(state)["warnings"])

    def test_other_language_no_fake_adapter(self):
        result = router.affordances(session(["invalid-state"], language="other", intent="design"))
        self.assertFalse(any(x["kind"] == "language" for x in result["lenses"]))
        self.assertTrue(result["warnings"])


if __name__ == "__main__":
    unittest.main()
