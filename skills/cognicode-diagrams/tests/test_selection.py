"""Contratos mínimos de selección C4: pruebas aisladas, sin acceder al checkout."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import selection


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / "view.atlas.json"
        self.data = {
            "schema_version": 1, "lens": "c4", "question": "C2",
            "label": "Contenedores", "claim_ids": ["C-1"],
            "kinds": {"C-1": "container"},
        }

    def write(self):
        self.file.write_text(json.dumps(self.data), encoding="utf-8")

    def test_valid_selection_preserves_metadata(self):
        self.data["assets"] = ["lenses/c4/renders/view.svg"]
        self.write()
        self.assertEqual(selection.load(self.file), self.data)

    def test_rejects_wrong_version(self):
        self.data["schema_version"] = 2
        self.write()
        with self.assertRaises(selection.SelectionError):
            selection.load(self.file)

    def test_rejects_empty_claim_ids(self):
        self.data["claim_ids"] = []
        self.write()
        with self.assertRaises(selection.SelectionError):
            selection.load(self.file)

    def test_rejects_duplicate_claim_ids(self):
        self.data["claim_ids"] = ["C-1", "C-1"]
        self.write()
        with self.assertRaises(selection.SelectionError):
            selection.load(self.file)

    def test_rejects_invalid_kinds_shape(self):
        self.data["kinds"] = []
        self.write()
        with self.assertRaises(selection.SelectionError):
            selection.load(self.file)

    def test_rejects_oversized_input(self):
        self.write()
        with self.file.open("a", encoding="utf-8") as handle:
            handle.write(" " * selection.MAX_BYTES)
        with self.assertRaises(selection.SelectionError):
            selection.load(self.file)

    def test_rejects_symlink(self):
        self.write()
        link = self.file.with_name("alias.atlas.json")
        link.symlink_to(self.file)
        with self.assertRaises(selection.SelectionError):
            selection.load(link)

    def test_rejects_invalid_json(self):
        self.file.write_text("{", encoding="utf-8")
        with self.assertRaises(selection.SelectionError):
            selection.load(self.file)


if __name__ == "__main__":
    unittest.main()
