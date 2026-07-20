"""CSV-backed data access, independent of FastAPI."""

import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Tuple, Union

from .errors import DataIntegrityError
from .models import Brand, Company, OwnershipGroup, Product, Relationship, ResearchGap, Source


Entity = Union[Brand, Company, OwnershipGroup]
Node = Tuple[str, str]


class CsvRepository:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.products = self._load_products()
        self.brands = self._load_brands()
        self.companies = self._load_companies()
        self.ownership_groups = self._load_ownership_groups()
        self.relationships = self._load_relationships()
        self.sources = self._load_sources()
        self.research_gaps = self._load_research_gaps()
        self._relationship_source_ids = self._load_links(
            "relationship_sources.csv", "relationship_id", "source_id"
        )
        self._gap_source_ids = self._load_links(
            "research_gap_sources.csv", "research_gap_id", "source_id"
        )
        self._products_by_gtin = self._index(self.products, "gtin")
        self._brands_by_id = self._index(self.brands, "id")
        self._companies_by_id = self._index(self.companies, "id")
        self._groups_by_id = self._index(self.ownership_groups, "id")
        self._sources_by_id = self._index(self.sources, "id")
        self._relationships_by_child = defaultdict(list)
        for relationship in self.relationships:
            self._relationships_by_child[(relationship.child_type, relationship.child_id)].append(relationship)
        self._gaps_by_subject = defaultdict(list)
        for gap in self.research_gaps:
            self._gaps_by_subject[(gap.subject_type, gap.subject_id)].append(gap)

    def _rows(self, filename: str) -> List[Dict[str, str]]:
        path = self.data_dir / filename
        try:
            with path.open(newline="", encoding="utf-8-sig") as handle:
                return [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(handle)]
        except OSError as exc:
            raise DataIntegrityError("Unable to read canonical data file: {}".format(filename)) from exc

    @staticmethod
    def _index(items: Iterable[object], field: str) -> Dict[str, object]:
        result = {}
        for item in items:
            key = getattr(item, field)
            if key in result:
                raise DataIntegrityError("Duplicate {}: {}".format(field, key))
            result[key] = item
        return result

    def _load_products(self) -> List[Product]:
        return [Product(**{key: row[key] for key in Product.__dataclass_fields__}) for row in self._rows("products.csv")]

    def _load_brands(self) -> List[Brand]:
        return [Brand(**row) for row in self._rows("brands.csv")]

    def _load_companies(self) -> List[Company]:
        return [Company(**row) for row in self._rows("companies.csv")]

    def _load_ownership_groups(self) -> List[OwnershipGroup]:
        return [OwnershipGroup(**row) for row in self._rows("ownership_groups.csv")]

    def _load_relationships(self) -> List[Relationship]:
        items = []
        for row in self._rows("ownership_relationships.csv"):
            row["confidence"] = float(row["confidence"])
            items.append(Relationship(**row))
        return items

    def _load_sources(self) -> List[Source]:
        return [Source(**row) for row in self._rows("sources.csv")]

    def _load_research_gaps(self) -> List[ResearchGap]:
        items = []
        for row in self._rows("research_gaps.csv"):
            row["confidence"] = float(row["confidence"])
            items.append(ResearchGap(**row))
        return items

    def _load_links(self, filename: str, left: str, right: str) -> Mapping[str, List[str]]:
        links = defaultdict(list)
        for row in self._rows(filename):
            links[row[left]].append(row[right])
        return links

    def get_product(self, gtin: str) -> Optional[Product]:
        return self._products_by_gtin.get(gtin)

    def get_brand(self, brand_id: str) -> Optional[Brand]:
        return self._brands_by_id.get(brand_id)

    def get_entity(self, entity_type: str, entity_id: str) -> Optional[Entity]:
        collections = {
            "brand": self._brands_by_id,
            "company": self._companies_by_id,
            "ownership_group": self._groups_by_id,
        }
        collection = collections.get(entity_type)
        return None if collection is None else collection.get(entity_id)

    def list_products(
        self, brand: Optional[str] = None, category: Optional[str] = None
    ) -> List[Tuple[Product, Brand]]:
        brand_filter = brand.casefold() if brand else None
        category_filter = category.casefold() if category else None
        result = []
        for product in self.products:
            product_brand = self.get_brand(product.brand_id)
            if product_brand is None:
                raise DataIntegrityError("Unknown brand_id: {}".format(product.brand_id))
            if brand_filter and brand_filter not in product_brand.name.casefold():
                continue
            if category_filter and category_filter not in product.category.casefold():
                continue
            result.append((product, product_brand))
        return result

    def verified_relationships_from(self, node: Node) -> List[Relationship]:
        return [
            relationship
            for relationship in self._relationships_by_child.get(node, [])
            if relationship.verification_status == "verified"
        ]

    def unresolved_relationships_from(self, node: Node) -> List[Relationship]:
        return [
            relationship
            for relationship in self._relationships_by_child.get(node, [])
            if relationship.verification_status != "verified"
        ]

    def sources_for_relationship(self, relationship_id: str) -> List[Source]:
        return self._resolve_sources(self._relationship_source_ids.get(relationship_id, []), relationship_id)

    def gaps_for(self, node: Node) -> List[ResearchGap]:
        return list(self._gaps_by_subject.get(node, []))

    def sources_for_gap(self, gap_id: str) -> List[Source]:
        return self._resolve_sources(self._gap_source_ids.get(gap_id, []), gap_id)

    def _resolve_sources(self, source_ids: Iterable[str], subject_id: str) -> List[Source]:
        result = []
        for source_id in source_ids:
            source = self._sources_by_id.get(source_id)
            if source is None:
                raise DataIntegrityError("Unknown source {} for {}".format(source_id, subject_id))
            result.append(source)
        return result
