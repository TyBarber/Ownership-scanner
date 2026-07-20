import csv
import shutil

import pytest

from ownership_scanner.errors import InvalidGtinError, ProductNotFoundError
from ownership_scanner.ownership_service import OwnershipService
from ownership_scanner.repository import CsvRepository

from test_repository import EXPECTED_GTINS


def _append_csv(path, row):
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = list(reader)
    rows.append(row)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _temporary_repository(tmp_path, canonical_data):
    copied = tmp_path / "data"
    shutil.copytree(canonical_data, copied)
    return copied


def test_all_known_gtins_resolve(repository):
    service = OwnershipService(repository)
    for gtin in EXPECTED_GTINS:
        result = service.get_product_ownership(gtin)
        assert result["product"]["gtin"] == gtin
        assert result["ownership_chain"]
        assert all(edge["verification_status"] == "verified" for edge in result["ownership_chain"])


def test_spindrift_uses_validated_gtin(repository):
    result = OwnershipService(repository).get_product_ownership("850017142350")
    assert result["product"]["name"] == "Spindrift Sparkling Water"


def test_leading_zero_gtin_is_preserved(repository):
    result = OwnershipService(repository).get_product_ownership("00016000124790")
    assert result["product"]["gtin"] == "00016000124790"


def test_malformed_gtin_is_rejected(repository):
    with pytest.raises(InvalidGtinError):
        OwnershipService(repository).get_product_ownership("not-a-barcode")


def test_valid_unknown_gtin_is_not_found(repository):
    with pytest.raises(ProductNotFoundError):
        OwnershipService(repository).get_product_ownership("000000000000")


def test_year_precision_is_preserved(repository):
    result = OwnershipService(repository).get_product_ownership("072940757092")
    edge = result["ownership_chain"][0]
    assert edge["effective_from"] == "2001"
    assert edge["effective_from_precision"] == "year"


def test_trader_joes_returns_group_and_research_gap(repository):
    result = OwnershipService(repository).get_product_ownership("00712996")
    assert result["highest_verified_owner"]["type"] == "ownership_group"
    assert result["highest_verified_owner"]["id"] == "ownership-group-aldi-nord"
    assert result["chain_complete"] is False
    assert result["overall_status"] == "verified_with_gaps"
    assert result["research_gaps"][0]["issue_type"] == "unresolved_parent_structure"


def test_retailer_owned_cooperative_is_returned(repository):
    result = OwnershipService(repository).get_product_ownership("041190055661")
    assert result["highest_verified_owner"]["company_type"] == "cooperative"


def test_multiple_sources_are_attached(repository):
    result = OwnershipService(repository).get_product_ownership("074117000734")
    assert len(result["ownership_chain"][0]["sources"]) == 2


def test_cycle_detection_stops_safely(tmp_path, repository):
    data = _temporary_repository(tmp_path, repository.data_dir)
    _append_csv(
        data / "ownership_relationships.csv",
        {
            "id": "relationship-test-cycle",
            "child_type": "company",
            "child_id": "company-fage-international-sa",
            "parent_type": "company",
            "parent_id": "company-fage-usa-dairy-industry-inc",
            "relationship_type": "owned_by",
            "effective_from": "",
            "effective_from_precision": "",
            "effective_until": "",
            "verification_status": "verified",
            "confidence": "0.9",
            "last_verified_at": "2026-07-20",
        },
    )
    _append_csv(
        data / "relationship_sources.csv",
        {"relationship_id": "relationship-test-cycle", "source_id": "source-fage-2024-annual-report"},
    )
    result = OwnershipService(CsvRepository(data)).get_product_ownership("689544083023")
    assert result["chain_complete"] is False
    assert result["overall_status"] == "cycle_detected"
    assert result["stop_reason"] == "cycle_detected"


def test_unresolved_relationship_is_never_returned_as_verified(tmp_path, repository):
    data = _temporary_repository(tmp_path, repository.data_dir)
    _append_csv(
        data / "ownership_relationships.csv",
        {
            "id": "relationship-test-unresolved",
            "child_type": "company",
            "child_id": "company-spindrift-beverage-co-inc",
            "parent_type": "company",
            "parent_id": "company-pepsico-inc",
            "relationship_type": "owned_by",
            "effective_from": "",
            "effective_from_precision": "",
            "effective_until": "",
            "verification_status": "unresolved",
            "confidence": "0.2",
            "last_verified_at": "2026-07-20",
        },
    )
    _append_csv(
        data / "relationship_sources.csv",
        {"relationship_id": "relationship-test-unresolved", "source_id": "source-spindrift-privacy"},
    )
    result = OwnershipService(CsvRepository(data)).get_product_ownership("850017142350")
    ids = [edge["parent"]["id"] for edge in result["ownership_chain"]]
    assert "company-pepsico-inc" not in ids
    assert result["highest_verified_owner"]["id"] == "company-spindrift-beverage-co-inc"
    assert result["chain_complete"] is False
