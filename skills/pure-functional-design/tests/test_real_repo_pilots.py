"""Evals reales de navegación; no confundir con tests de producto.

Las sesiones referencian código versionado, pero el router no lo lee ni valida.
"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "affordances.py"
spec = importlib.util.spec_from_file_location("fp_real_pilot_router", SCRIPT)
router = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = router
spec.loader.exec_module(router)


def pilot(name):
    return json.loads((ROOT / "examples" / name).read_text(encoding="utf-8"))


class RealPilotDecisionTests(unittest.TestCase):
    def test_rust_pilot_requires_characterization_before_refactor(self):
        state = pilot("pilot-hodei-search-rust.json")
        result = router.affordances(state)
        self.assertEqual(result["recommendation"]["decision"], "INSPECT_MORE")
        self.assertFalse(any(link["rel"] == "read-recipe" for link in result["_links"]))
        self.assertFalse(any(link["rel"] == "propose-slice" for link in result["_links"]))
        self.assertIn("language-rust", {lens["id"] for lens in result["lenses"]})

    def test_kotlin_pilot_abstains_from_breaking_cohesive_dispatch_cycle(self):
        state = pilot("pilot-pipelinek-dispatch-kotlin.json")
        result = router.affordances(state)
        self.assertEqual(result["recommendation"]["decision"], "KEEP_AS_IS")
        self.assertIn("preserve-existing", {link["rel"] for link in result["_links"]})
        self.assertFalse(any(link["rel"] == "read-recipe" for link in result["_links"]))

    def test_pilot_evidence_is_anchored_to_exact_revisions(self):
        rust = pilot("pilot-hodei-search-rust.json")
        self.assertIn("@26c5c08b646960e9545f0918847d207bb5d0acec",
                      rust["problems"][0]["evidence"][0]["source"])
        # The Kotlin example records a hypothesis, not a confirmed cause.
        kotlin = pilot("pilot-pipelinek-dispatch-kotlin.json")
        self.assertEqual(kotlin["problems"][0]["evidence"], [])

    def test_stale_pilot_avoids_reusing_previous_diagnosis(self):
        state = pilot("pilot-hodei-search-rust.json")
        state["basis"] = "stale"
        result = router.affordances(state)
        self.assertIsNone(result["recommendation"])
        self.assertEqual(result["_links"][0]["rel"], "refresh-basis")


if __name__ == "__main__":
    unittest.main()
