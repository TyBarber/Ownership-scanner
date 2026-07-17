import csv
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_data", ROOT / "scripts" / "validate_data.py")
validator = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(validator)


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.data = Path(self.temp.name) / "data"
        shutil.copytree(ROOT / "data", self.data)

    def tearDown(self):
        self.temp.cleanup()

    def rows(self, filename):
        with (self.data / filename).open(newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def write(self, filename, rows):
        with (self.data / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=validator.SCHEMAS[filename])
            writer.writeheader()
            writer.writerows(rows)

    def test_canonical_data_passes_development_profile(self):
        self.assertEqual([], validator.validate(self.data, "development"))

    def test_full_profile_retains_ten_product_gate(self):
        errors = validator.validate(self.data, "full")
        self.assertEqual(1, len(errors))
        self.assertIn("at least 10 real products required; found 5", errors[0])

    def test_all_canonical_gtins_are_valid_and_preserve_zeroes(self):
        products = self.rows("products.csv")
        self.assertTrue(all(row["gtin"].startswith("0") for row in products))
        self.assertTrue(all(validator.valid_gtin(row["gtin"]) for row in products))

    def test_missing_source_is_reported(self):
        links = [row for row in self.rows("relationship_sources.csv") if row["relationship_id"] != "relationship-josephs-middle-east-bakery"]
        self.write("relationship_sources.csv", links)
        self.assertTrue(any("missing sources" in error for error in validator.validate(self.data, "development")))

    def test_invalid_typed_reference_is_reported(self):
        rows = self.rows("ownership_relationships.csv")
        rows[0]["parent_id"] = "missing-company"
        self.write("ownership_relationships.csv", rows)
        self.assertTrue(any("unknown company parent_id" in error for error in validator.validate(self.data, "development")))

    def test_year_precision_is_preserved(self):
        rows = self.rows("ownership_relationships.csv")
        tutt = next(row for row in rows if row["id"] == "relationship-tuttorosso-red-gold")
        self.assertEqual("2001", tutt["effective_from"])
        self.assertEqual("year", tutt["effective_from_precision"])

    def test_invalid_year_precision_is_reported(self):
        rows = self.rows("ownership_relationships.csv")
        rows[0]["effective_from"] = "20XX"
        rows[0]["effective_from_precision"] = "year"
        self.write("ownership_relationships.csv", rows)
        self.assertTrue(any("year precision requires" in error for error in validator.validate(self.data, "development")))

    def test_confirmed_cycle_is_reported(self):
        rows = self.rows("ownership_relationships.csv")
        rows.append({
            "id": "relationship-cycle", "child_type": "ownership_group", "child_id": "ownership-group-aldi-nord",
            "parent_type": "company", "parent_id": "company-trader-joes-company", "relationship_type": "owned_by",
            "effective_from": "", "effective_from_precision": "", "effective_until": "",
            "verification_status": "verified", "confidence": "0.8", "last_verified_at": "2026-07-17",
        })
        self.write("ownership_relationships.csv", rows)
        links = self.rows("relationship_sources.csv")
        links.append({"relationship_id": "relationship-cycle", "source_id": "source-usda-aldi-report"})
        self.write("relationship_sources.csv", links)
        self.assertTrue(any("Cycle in confirmed ownership" in error for error in validator.validate(self.data, "development")))

    def test_unresolved_edge_does_not_become_confirmed_parent(self):
        errors = validator.validate(self.data, "development")
        self.assertFalse(any("albrecht-structure-unresolved" in error for error in errors))

    def test_research_gap_replaces_fictional_parent_entity(self):
        groups = self.rows("ownership_groups.csv")
        self.assertEqual(["ownership-group-aldi-nord"], [row["id"] for row in groups])
        gaps = self.rows("research_gaps.csv")
        self.assertEqual("ownership-group-aldi-nord", gaps[0]["subject_id"])
        self.assertEqual("unresolved_parent_structure", gaps[0]["issue_type"])

    def test_legacy_owns_direction_is_rejected(self):
        rows = self.rows("ownership_relationships.csv")
        rows[0]["relationship_type"] = "owns"
        self.write("ownership_relationships.csv", rows)
        self.assertTrue(any("invalid relationship_type owns" in error for error in validator.validate(self.data, "development")))


if __name__ == "__main__":
    unittest.main()
