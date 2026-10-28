"""Evaluaciones portables del selector; no ejecutan aplicaciones consumidoras."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fp_portable_router", ROOT / "scripts" / "affordances.py"
)
router = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = router
SPEC.loader.exec_module(router)


def case(filename):
    return json.loads((ROOT / "examples" / filename).read_text(encoding="utf-8"))


class PortableScenarioTests(unittest.TestCase):
    def test_rust_observation_without_preconditions_requests_more_information(self):
        result = router.affordances(case("diagnose-rust-uncharacterized.json"))
        self.assertEqual(result["recommendation"]["decision"], "INSPECT_MORE")
        self.assertNotIn("read-recipe", [x["rel"] for x in result["_links"]])
        self.assertIn("language-rust", [x["id"] for x in result["lenses"]])

    def test_kotlin_cohesion_is_a_reason_not_to_refactor(self):
        result = router.affordances(case("diagnose-kotlin-cohesive.json"))
        self.assertEqual(result["recommendation"]["decision"], "KEEP_AS_IS")
        self.assertIn("preserve-existing", [x["rel"] for x in result["_links"]])

    def test_synthetic_fixtures_are_present_and_used_by_examples(self):
        rust = (ROOT / "examples/fixtures/search_use_case.rs").read_text()
        kotlin = (ROOT / "examples/fixtures/step_dispatch.kt").read_text()
        self.assertIn("self.metrics.record(count)?", rust)
        self.assertIn("step.children.flatMap(::dispatch)", kotlin)
        self.assertIn("examples/fixtures/search_use_case.rs",
                      case("diagnose-rust-uncharacterized.json")["problems"][0]["evidence"][0]["source"])

    def test_generic_ready_case_is_a_proposal_not_an_execution(self):
        state = case("diagnose-rust-uncharacterized.json")
        state["facts"] = ["behavior-characterized", "effect-order-understood"]
        result = router.affordances(state)
        self.assertEqual(result["recommendation"]["decision"], "APPLY")
        self.assertEqual(result["status"], "NAVIGATION_ONLY")
        self.assertIn("read-recipe", [x["rel"] for x in result["_links"]])

    def test_progressive_disclosure_follows_phase(self):
        state = case("diagnose-rust-uncharacterized.json")
        state["facts"] = ["behavior-characterized", "effect-order-understood"]
        state["phase"] = "diagnose"
        diagnose = router.affordances(state)
        self.assertNotIn("read-recipe", [x["rel"] for x in diagnose["_links"]])
        state["phase"] = "plan"
        plan = router.affordances(state)
        self.assertIn("read-recipe", [x["rel"] for x in plan["_links"]])
        state["phase"] = "verify"
        verify = router.affordances(state)
        self.assertIn("verify-contracts", [x["rel"] for x in verify["_links"]])

    def test_changed_context_recalculates_and_stale_invalidates(self):
        rust = case("diagnose-rust-uncharacterized.json")
        kotlin = case("diagnose-kotlin-cohesive.json")
        before = router.affordances(rust)
        alternate = router.affordances(kotlin)
        self.assertNotEqual(before["recommendation"], alternate["recommendation"])
        self.assertEqual(router.affordances(rust), before)
        rust["basis"] = "stale"
        stale = router.affordances(rust)
        self.assertIsNone(stale["recommendation"])
        self.assertEqual(stale["_links"][0]["rel"], "refresh-basis")

    def test_delegation_requires_available_skill(self):
        state = case("diagnose-rust-uncharacterized.json")
        state["available_skills"] = ["nonexistent-skill"]
        self.assertNotIn("delegate-skill", [x["rel"] for x in router.affordances(state)["_links"]])
        state["available_skills"] = ["delivery-first-testing"]
        self.assertIn("delivery-first-testing",
                      [x["skill_id"] for x in router.affordances(state)["_links"]
                       if x["rel"] == "delegate-skill"])


if __name__ == "__main__":
    unittest.main()
