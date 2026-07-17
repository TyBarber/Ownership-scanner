#!/usr/bin/env python3
"""Validate Ownership Scanner CSV data using only the Python standard library."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


SCHEMAS = {
    "products.csv": ["id", "gtin", "name", "brand_id", "category", "package_company_text", "image_url", "created_at", "updated_at"],
    "brands.csv": ["id", "name", "website", "status"],
    "companies.csv": ["id", "legal_name", "display_name", "company_type", "country", "website", "sec_cik", "status"],
    "ownership_groups.csv": ["id", "name", "description", "country", "status"],
    "ownership_relationships.csv": ["id", "child_type", "child_id", "parent_type", "parent_id", "relationship_type", "effective_from", "effective_from_precision", "effective_until", "verification_status", "confidence", "last_verified_at"],
    "sources.csv": ["id", "title", "url", "publisher", "source_type", "published_at", "retrieved_at", "notes"],
    "relationship_sources.csv": ["relationship_id", "source_id"],
    "research_gaps.csv": ["id", "subject_type", "subject_id", "issue_type", "status", "confidence", "explanation"],
    "research_gap_sources.csv": ["research_gap_id", "source_id"],
}
ENTITY_FILES = {"brand": "brands.csv", "company": "companies.csv", "ownership_group": "ownership_groups.csv"}
ALLOWED_STATUSES = {"verified", "probable", "unresolved"}
ALLOWED_RELATIONSHIPS = {"owned_by", "controlled_by_group", "affiliated_with_group"}


def parse_iso_date(value: str) -> date | None:
    if not value:
        return None
    try:
        result = date.fromisoformat(value)
    except ValueError:
        return None
    return result if result.isoformat() == value else None


def valid_gtin(value: str) -> bool:
    if not value.isdigit() or len(value) not in {8, 12, 13, 14}:
        return False
    digits = [int(char) for char in value]
    total = sum(digit * (3 if offset % 2 == 0 else 1) for offset, digit in enumerate(reversed(digits[:-1])))
    return (10 - total % 10) % 10 == digits[-1]


def load_tables(data_dir: Path, errors: list[str]) -> dict[str, list[dict[str, str]]]:
    tables = {}
    for filename, columns in SCHEMAS.items():
        path = data_dir / filename
        if not path.is_file():
            errors.append(f"Missing required file: {filename}")
            tables[filename] = []
            continue
        with path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            missing = [column for column in columns if column not in (reader.fieldnames or [])]
            if missing:
                errors.append(f"{filename}: missing required columns: {', '.join(missing)}")
            tables[filename] = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    return tables


def validate(data_dir: Path, profile: str = "full") -> list[str]:
    errors: list[str] = []
    tables = load_tables(data_dir, errors)
    ids: dict[str, set[str]] = {}

    for filename, rows in tables.items():
        if filename in {"relationship_sources.csv", "research_gap_sources.csv"}:
            continue
        seen: set[str] = set()
        for line, row in enumerate(rows, 2):
            row_id = row.get("id", "")
            if not row_id:
                errors.append(f"{filename}:{line}: missing ID")
            elif row_id in seen:
                errors.append(f"{filename}:{line}: duplicate ID {row_id}")
            seen.add(row_id)
        ids[filename] = seen

    for filename, fields in {
        "products.csv": ("created_at", "updated_at"),
        "sources.csv": ("published_at", "retrieved_at"),
        "ownership_relationships.csv": ("effective_until", "last_verified_at"),
    }.items():
        for line, row in enumerate(tables[filename], 2):
            for field in fields:
                value = row.get(field, "")
                if value and parse_iso_date(value) is None:
                    errors.append(f"{filename}:{line}: invalid ISO date in {field}: {value}")

    gtins: set[str] = set()
    for line, row in enumerate(tables["products.csv"], 2):
        gtin = row.get("gtin", "")
        if gtin in gtins:
            errors.append(f"products.csv:{line}: duplicate GTIN {gtin}")
        gtins.add(gtin)
        if not valid_gtin(gtin):
            errors.append(f"products.csv:{line}: invalid GTIN length or check digit: {gtin}")
        if row.get("brand_id") not in ids["brands.csv"]:
            errors.append(f"products.csv:{line}: unknown brand_id {row.get('brand_id', '')}")

    for line, row in enumerate(tables["sources.csv"], 2):
        parsed = urlparse(row.get("url", ""))
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"sources.csv:{line}: source URL must be HTTPS")

    source_links: dict[str, set[str]] = defaultdict(set)
    seen_links: set[tuple[str, str]] = set()
    for line, row in enumerate(tables["relationship_sources.csv"], 2):
        relationship_id, source_id = row.get("relationship_id", ""), row.get("source_id", "")
        pair = (relationship_id, source_id)
        if pair in seen_links:
            errors.append(f"relationship_sources.csv:{line}: duplicate relationship/source link")
        seen_links.add(pair)
        if relationship_id not in ids["ownership_relationships.csv"]:
            errors.append(f"relationship_sources.csv:{line}: unknown relationship_id {relationship_id}")
        if source_id not in ids["sources.csv"]:
            errors.append(f"relationship_sources.csv:{line}: unknown source_id {source_id}")
        source_links[relationship_id].add(source_id)

    research_gap_links: dict[str, set[str]] = defaultdict(set)
    for line, row in enumerate(tables["research_gap_sources.csv"], 2):
        gap_id, source_id = row.get("research_gap_id", ""), row.get("source_id", "")
        if gap_id not in ids["research_gaps.csv"]:
            errors.append(f"research_gap_sources.csv:{line}: unknown research_gap_id {gap_id}")
        if source_id not in ids["sources.csv"]:
            errors.append(f"research_gap_sources.csv:{line}: unknown source_id {source_id}")
        research_gap_links[gap_id].add(source_id)

    for line, row in enumerate(tables["research_gaps.csv"], 2):
        subject_type, subject_id = row.get("subject_type", ""), row.get("subject_id", "")
        if subject_type not in ENTITY_FILES:
            errors.append(f"research_gaps.csv:{line}: invalid subject_type {subject_type}")
        elif subject_id not in ids[ENTITY_FILES[subject_type]]:
            errors.append(f"research_gaps.csv:{line}: unknown {subject_type} subject_id {subject_id}")
        if row.get("status") != "unresolved":
            errors.append(f"research_gaps.csv:{line}: research gap status must be unresolved")
        try:
            confidence = float(row.get("confidence", ""))
            if not 0 <= confidence <= 1:
                raise ValueError
        except ValueError:
            errors.append(f"research_gaps.csv:{line}: confidence must be between 0 and 1")
        if not row.get("explanation"):
            errors.append(f"research_gaps.csv:{line}: explanation is required")
        if not research_gap_links.get(row.get("id", "")):
            errors.append(f"research_gaps.csv:{line}: missing sources")

    confirmed_edges: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    for line, row in enumerate(tables["ownership_relationships.csv"], 2):
        child_type, parent_type = row.get("child_type", ""), row.get("parent_type", "")
        child_id, parent_id = row.get("child_id", ""), row.get("parent_id", "")
        if child_type not in ENTITY_FILES:
            errors.append(f"ownership_relationships.csv:{line}: invalid child_type {child_type}")
        elif child_id not in ids[ENTITY_FILES[child_type]]:
            errors.append(f"ownership_relationships.csv:{line}: unknown {child_type} child_id {child_id}")
        if parent_type not in {"company", "ownership_group"}:
            errors.append(f"ownership_relationships.csv:{line}: invalid parent_type {parent_type}")
        elif parent_id not in ids[ENTITY_FILES[parent_type]]:
            errors.append(f"ownership_relationships.csv:{line}: unknown {parent_type} parent_id {parent_id}")
        relationship_type = row.get("relationship_type", "")
        if relationship_type not in ALLOWED_RELATIONSHIPS:
            errors.append(f"ownership_relationships.csv:{line}: invalid relationship_type {relationship_type}")
        if relationship_type in {"controlled_by_group", "affiliated_with_group"} and parent_type != "ownership_group":
            errors.append(f"ownership_relationships.csv:{line}: {relationship_type} requires an ownership_group parent")
        status = row.get("verification_status", "")
        if status not in ALLOWED_STATUSES:
            errors.append(f"ownership_relationships.csv:{line}: invalid verification_status {status}")
        try:
            confidence = float(row.get("confidence", ""))
            if not 0 <= confidence <= 1:
                raise ValueError
        except ValueError:
            errors.append(f"ownership_relationships.csv:{line}: confidence must be between 0 and 1")
        precision, effective_from = row.get("effective_from_precision", ""), row.get("effective_from", "")
        if precision not in {"", "day", "year"}:
            errors.append(f"ownership_relationships.csv:{line}: invalid effective_from_precision {precision}")
        if precision == "year":
            if len(effective_from) != 4 or not effective_from.isdigit():
                errors.append(f"ownership_relationships.csv:{line}: year precision requires YYYY effective_from")
        elif effective_from and parse_iso_date(effective_from) is None:
            errors.append(f"ownership_relationships.csv:{line}: day precision requires ISO effective_from")
        if effective_from and not precision:
            errors.append(f"ownership_relationships.csv:{line}: effective_from_precision is required")
        end = parse_iso_date(row.get("effective_until", ""))
        if end and effective_from:
            start_year = int(effective_from[:4])
            if end.year < start_year:
                errors.append(f"ownership_relationships.csv:{line}: effective_until precedes effective_from")
        if not source_links.get(row.get("id", "")):
            errors.append(f"ownership_relationships.csv:{line}: missing sources")
        if status == "verified":
            confirmed_edges[(child_type, child_id)].append((parent_type, parent_id))

    def walk(node: tuple[str, str], trail: tuple[tuple[str, str], ...]) -> tuple[str, str] | None:
        if node in trail:
            errors.append("Cycle in confirmed ownership: " + " -> ".join(item[1] for item in trail + (node,)))
            return None
        parents = list(dict.fromkeys(confirmed_edges.get(node, [])))
        if len(parents) > 1:
            errors.append(f"Broken confirmed ownership chain: {node[1]} has multiple confirmed parents")
            return None
        return node if not parents else walk(parents[0], trail + (node,))

    real_products = [row for row in tables["products.csv"] if not row.get("id", "").startswith("placeholder-")]
    required_products = 5 if profile == "development" else 10
    if len(real_products) < required_products:
        errors.append(f"{profile.capitalize()} gate: at least {required_products} real products required; found {len(real_products)}")
    real_brands = {row.get("brand_id", "") for row in real_products}
    if len(real_brands) < 5:
        errors.append(f"Feasibility gate: at least 5 brands required; found {len(real_brands)}")
    highest_verified_entities = set()
    for brand_id in real_brands:
        result = walk(("brand", brand_id), ())
        if result == ("brand", brand_id):
            errors.append(f"Broken ownership chain: brand {brand_id} has no verified owner")
        elif result:
            highest_verified_entities.add(result)
    if len(highest_verified_entities) < 3:
        errors.append(f"Feasibility gate: at least 3 highest verified ownership entities required; found {len(highest_verified_entities)}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", nargs="?", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    parser.add_argument("--profile", choices=("development", "full"), default="full")
    args = parser.parse_args(argv)
    errors = validate(args.data_dir, args.profile)
    if errors:
        print(f"VALIDATION FAILED ({len(errors)} issue(s))")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"VALIDATION PASSED ({args.profile} profile)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
