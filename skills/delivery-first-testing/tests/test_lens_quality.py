"""Behavioral routing fitness: ready lenses must be relevant, not automatic gates."""
import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "affordances.py"
spec = importlib.util.spec_from_file_location("delivery_router_lenses", SCRIPT)
router = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = router
spec.loader.exec_module(router)


def lenses(changed, *, intent="feature", risk="routine", uat="pending", regression="pending"):
    state = {
        "intent": intent, "inventory": "ready", "basis": "current",
        "impact": "known", "changed": changed, "risk": risk,
        "affected": "passed", "uat": uat, "regression": regression,
    }
    if uat == "not_needed":
        state["uat_reason"] = "pure document change with no runtime impact"
    if regression == "decided":
        state["regression_reason"] = "existing guarantee preserved"
    return {entry["id"] for entry in router.affordances(state)["lenses"]}


class RoutingQualityTests(unittest.TestCase):
    def test_docs_only_does_not_offer_code_quality_probes(self):
        found = lenses(["docs"], uat="not_needed")
        self.assertIn("change-impact", found)
        self.assertNotIn("ephemeral-uat", found)
        self.assertNotIn("data-driven-design", found)
        self.assertNotIn("mutation-guidance", found)

    def test_domain_feature_selects_data_driven_not_global_mutation(self):
        found = lenses(["domain"])
        self.assertIn("data-driven-design", found)
        self.assertNotIn("mutation-guidance", found)

    def test_high_risk_security_can_offer_mutation_probe(self):
        found = lenses(["security"], risk="high")
        self.assertIn("mutation-guidance", found)
        self.assertNotIn("data-driven-design", found)

    def test_ui_scenario_offered_only_when_pending(self):
        self.assertIn("ephemeral-uat", lenses(["ui"], uat="pending"))
        self.assertNotIn("ephemeral-uat", lenses(["ui"], uat="passed"))

    def test_closed_regression_does_not_recommend_decision_again(self):
        self.assertNotIn("regression-promotion", lenses(["domain"], regression="decided"))

    def test_portfolio_audit_always_includes_economics(self):
        self.assertIn("harness-economics", lenses([], intent="audit"))

    def test_audit_critical_domain_includes_targeted_probe(self):
        found = lenses(["domain"], intent="audit", risk="critical")
        self.assertIn("harness-economics", found)
        self.assertIn("mutation-guidance", found)

    def test_unrelated_release_has_no_data_driven(self):
        self.assertNotIn("data-driven-design", lenses(["release"], intent="release"))

    def test_all_ready_playbooks_are_inside_lens_directory(self):
        for lens in router.read_catalog().values():
            if lens["status"] == "ready":
                path = (SCRIPT.parent.parent / lens["playbook"]).resolve()
                self.assertTrue(path.is_file())
                self.assertTrue(path.is_relative_to((SCRIPT.parent.parent / "references" / "lenses").resolve()))


if __name__ == "__main__":
    unittest.main()
