"""Ownership traversal and response assembly, independent of FastAPI."""

from typing import Dict, List, Set, Tuple

from .errors import DataIntegrityError, InvalidGtinError, ProductNotFoundError
from .models import Brand, Company, OwnershipGroup, Product, ResearchGap, Source
from .repository import CsvRepository, Entity, Node


def valid_gtin(value: str) -> bool:
    if not value.isdigit() or len(value) not in {8, 12, 13, 14}:
        return False
    digits = [int(character) for character in value]
    total = sum(
        digit * (3 if offset % 2 == 0 else 1)
        for offset, digit in enumerate(reversed(digits[:-1]))
    )
    return (10 - total % 10) % 10 == digits[-1]


def _source_dict(source: Source) -> Dict[str, object]:
    primary_prefixes = ("official_", "government_")
    return {
        "title": source.title,
        "url": source.url,
        "publisher": source.publisher,
        "source_type": source.source_type,
        "support_type": "primary" if source.source_type.startswith(primary_prefixes) else "secondary",
        "published_at": source.published_at or None,
        "retrieved_at": source.retrieved_at,
    }


def _entity_name(entity: Entity) -> str:
    return entity.display_name if isinstance(entity, Company) else entity.name


def _entity_ref(entity_type: str, entity: Entity) -> Dict[str, str]:
    return {"type": entity_type, "id": entity.id, "name": _entity_name(entity)}


def _owner_dict(entity_type: str, entity: Entity) -> Dict[str, object]:
    result = _entity_ref(entity_type, entity)
    if isinstance(entity, Company):
        result.update({"company_type": entity.company_type, "country": entity.country})
    elif isinstance(entity, OwnershipGroup):
        result.update({"description": entity.description, "country": entity.country})
    return result


def _gap_dict(repository: CsvRepository, gap: ResearchGap) -> Dict[str, object]:
    return {
        "id": gap.id,
        "subject": {"type": gap.subject_type, "id": gap.subject_id},
        "issue_type": gap.issue_type,
        "status": gap.status,
        "confidence": gap.confidence,
        "explanation": gap.explanation,
        "sources": [_source_dict(source) for source in repository.sources_for_gap(gap.id)],
    }


class OwnershipService:
    def __init__(self, repository: CsvRepository):
        self.repository = repository

    def list_products(self, brand=None, category=None, limit=100, offset=0) -> Dict[str, object]:
        matches = self.repository.list_products(brand=brand, category=category)
        page = matches[offset : offset + limit]
        return {
            "products": [
                {
                    "id": product.id,
                    "gtin": product.gtin,
                    "name": product.name,
                    "category": product.category,
                    "brand": {"id": product_brand.id, "name": product_brand.name},
                }
                for product, product_brand in page
            ],
            "total": len(matches),
            "limit": limit,
            "offset": offset,
        }

    def get_product_ownership(self, gtin: str) -> Dict[str, object]:
        if not valid_gtin(gtin):
            raise InvalidGtinError("GTIN must be 8, 12, 13, or 14 digits with a valid check digit")
        product = self.repository.get_product(gtin)
        if product is None:
            raise ProductNotFoundError("Product not found")
        brand = self.repository.get_brand(product.brand_id)
        if brand is None:
            raise DataIntegrityError("Unknown brand_id: {}".format(product.brand_id))

        chain = []
        gaps = []
        seen_gaps: Set[str] = set()
        current_type = "brand"
        current_entity: Entity = brand
        visited: Set[Node] = set()
        chain_complete = True
        stop_reason = "terminal_owner"

        while True:
            node = (current_type, current_entity.id)
            visited.add(node)
            for gap in self.repository.gaps_for(node):
                if gap.id not in seen_gaps:
                    gaps.append(_gap_dict(self.repository, gap))
                    seen_gaps.add(gap.id)

            relationships = self.repository.verified_relationships_from(node)
            if not relationships:
                if self.repository.unresolved_relationships_from(node):
                    chain_complete = False
                    stop_reason = "unresolved_relationship"
                break
            if len(relationships) > 1:
                chain_complete = False
                stop_reason = "multiple_verified_parents"
                break

            relationship = relationships[0]
            parent = self.repository.get_entity(relationship.parent_type, relationship.parent_id)
            if parent is None:
                raise DataIntegrityError("Unknown parent entity: {}".format(relationship.parent_id))
            parent_node = (relationship.parent_type, relationship.parent_id)
            if parent_node in visited:
                chain_complete = False
                stop_reason = "cycle_detected"
                break
            sources = self.repository.sources_for_relationship(relationship.id)
            if not sources:
                raise DataIntegrityError("Confirmed relationship has no source: {}".format(relationship.id))
            chain.append(
                {
                    "child": _entity_ref(current_type, current_entity),
                    "relationship_type": relationship.relationship_type,
                    "parent": _entity_ref(relationship.parent_type, parent),
                    "verification_status": relationship.verification_status,
                    "confidence": relationship.confidence,
                    "effective_from": relationship.effective_from or None,
                    "effective_from_precision": relationship.effective_from_precision or None,
                    "effective_until": relationship.effective_until or None,
                    "last_verified_at": relationship.last_verified_at,
                    "sources": [_source_dict(source) for source in sources],
                }
            )
            current_type = relationship.parent_type
            current_entity = parent

        if gaps:
            chain_complete = False
            if stop_reason == "terminal_owner":
                stop_reason = "research_gap"

        if stop_reason == "cycle_detected":
            overall_status = "cycle_detected"
        elif chain_complete:
            overall_status = "verified"
        else:
            overall_status = "verified_with_gaps"

        return {
            "product": {
                "id": product.id,
                "gtin": product.gtin,
                "name": product.name,
                "category": product.category,
                "package_company_text": product.package_company_text,
            },
            "brand": {"id": brand.id, "name": brand.name, "website": brand.website},
            "ownership_chain": chain,
            "highest_verified_owner": _owner_dict(current_type, current_entity),
            "chain_complete": chain_complete,
            "overall_status": overall_status,
            "stop_reason": stop_reason,
            "research_gaps": gaps,
        }
