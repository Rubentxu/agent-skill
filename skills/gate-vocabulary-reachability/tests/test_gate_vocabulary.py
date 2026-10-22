"""Pruebas del auditor de alcanzabilidad: qué se declara vivo y qué inerte.

El script decide si una variante de una puerta se construye en producción, y
su error se paga en las dos direcciones: declarar muerto lo vivo borra
trabajo, y declarar vivo lo muerto deja una puerta sin cubrir. Por eso cada
prueba monta un repositorio donde la respuesta correcta no coincide con la
que daría un naive.
"""

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_gate_vocabulary.py"
spec = importlib.util.spec_from_file_location("gate_vocabulary_audit", SCRIPT)
audit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit
spec.loader.exec_module(audit)

ENUM = """pub enum Action {
    Allow,
    Deny,
    Escalate,
}
"""


def build(root: Path, files: dict[str, str]) -> None:
    """Monta un repositorio mínimo con los ficheros indicados."""
    for name, body in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")


def run(root: Path, *extra: str) -> tuple[int, str, str]:
    """Ejecuta el auditor como lo haría una persona y devuelve su desenlace."""
    out, err = io.StringIO(), io.StringIO()
    argv = [
        "audit_gate_vocabulary.py",
        "--root", str(root),
        "--enum", "src/domain.rs",
        "--enum-name", "Action",
        *extra,
    ]
    with patch.object(sys, "argv", argv), redirect_stdout(out), redirect_stderr(err):
        code = audit.main()
    return code, out.getvalue(), err.getvalue()


class VocabularyReachabilityTests(unittest.TestCase):
    def test_variant_only_used_inside_a_test_module_is_inert(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build(root, {
                "src/domain.rs": ENUM,
                "src/evaluate.rs": "pub fn decide() -> Action {\n    Action::Allow\n}\n",
                "src/checks.rs": (
                    "#[cfg(test)]\nmod tests {\n    use super::*;\n"
                    "    fn test_escalate() {\n        let _ = Action::Escalate;\n    }\n}\n"
                ),
            })
            code, out, _ = run(root)
            self.assertIn("VIVO    Allow", out)
            self.assertIn("INERTE  Escalate", out)
            self.assertIn("INERTE  Deny", out)
            self.assertEqual(code, 1)

    def test_declaration_in_the_enum_itself_is_not_a_construction(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build(root, {"src/domain.rs": ENUM})
            code, out, _ = run(root)
            for variant in ("Allow", "Deny", "Escalate"):
                self.assertIn(f"INERTE  {variant}", out)
            self.assertIn("resumen: 0/3 construidas, 3 inertes", out)
            self.assertEqual(code, 1)

    def test_exhaustive_name_map_does_not_prove_a_variant_is_built(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build(root, {
                "src/domain.rs": ENUM,
                "src/policy.rs": (
                    "pub fn name(a: Action) -> &'static str {\n    match a {\n"
                    "        Action::Allow => \"allow\",\n"
                    "        Action::Deny => \"deny\",\n"
                    "        Action::Escalate => \"escalate\",\n    }\n}\n"
                ),
                "src/evaluate.rs": "pub fn decide() -> Action {\n    Action::Allow\n}\n",
            })
            code, out, _ = run(root)
            self.assertIn("VIVO    Allow", out)
            self.assertIn("INERTE  Deny", out)
            self.assertIn("INERTE  Escalate", out)
            self.assertEqual(code, 1)

    def test_unqualified_name_does_not_count_as_a_construction(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build(root, {
                "src/domain.rs": ENUM,
                "src/evaluate.rs": "pub fn decide() -> Action {\n    Action::Allow\n}\n",
                "src/loose.rs": "fn pick() -> Action {\n    Deny\n}\n",
            })
            code, out, _ = run(root)
            self.assertIn("VIVO    Allow", out)
            self.assertIn("INERTE  Deny", out)
            self.assertEqual(code, 1)

    def test_longer_variant_does_not_prove_the_shorter_one(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build(root, {
                "src/domain.rs": "pub enum Action {\n    Foo,\n    Foobar,\n}\n",
                "src/evaluate.rs": "pub fn decide() -> Action {\n    Action::Foobar\n}\n",
            })
            code, out, _ = run(root)
            self.assertIn("VIVO    Foobar", out)
            self.assertIn("INERTE  Foo", out)
            self.assertEqual(code, 1)

    def test_report_points_at_the_line_that_constructs_the_variant(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build(root, {
                "src/domain.rs": ENUM,
                "src/evaluate.rs": "pub fn decide() -> Action {\n    Action::Allow\n}\n",
            })
            _, out, _ = run(root)
            self.assertIn("src/evaluate.rs:2", out)

    def test_fully_covered_vocabulary_exits_clean(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build(root, {
                "src/domain.rs": "pub enum Action {\n    Allow,\n}\n",
                "src/evaluate.rs": "pub fn decide() -> Action {\n    Action::Allow\n}\n",
            })
            code, out, _ = run(root)
            self.assertIn("resumen: 1/1 construidas, 0 inertes", out)
            self.assertEqual(code, 0)

    def test_incomplete_inventory_fails_closed_before_auditing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build(root, {
                "src/domain.rs": ENUM,
                "src/evaluate.rs": "pub fn decide() -> Action {\n    Action::Allow\n}\n",
            })
            code, out, err = run(root, "--expect-total", "99")
            self.assertEqual(code, 2)
            self.assertIn("INVENTARIO INCOMPLETO", err)
            self.assertNotIn("resumen:", out)

    def test_matching_expected_total_keeps_the_audit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build(root, {
                "src/domain.rs": ENUM,
                "src/evaluate.rs": "pub fn decide() -> Action {\n    Action::Allow\n}\n",
            })
            code, out, err = run(root, "--expect-total", "3")
            self.assertEqual(code, 1)
            self.assertIn("resumen: 1/3 construidas, 2 inertes", out)
            self.assertEqual(err, "")


if __name__ == "__main__":
    unittest.main()
