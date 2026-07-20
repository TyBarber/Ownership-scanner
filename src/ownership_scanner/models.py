"""Domain models that do not depend on an HTTP framework."""

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Product:
    id: str
    gtin: str
    name: str
    brand_id: str
    category: str
    package_company_text: str
    image_url: str


@dataclass(frozen=True)
class Brand:
    id: str
    name: str
    website: str
    status: str


@dataclass(frozen=True)
class Company:
    id: str
    legal_name: str
    display_name: str
    company_type: str
    country: str
    website: str
    sec_cik: str
    status: str


@dataclass(frozen=True)
class OwnershipGroup:
    id: str
    name: str
    description: str
    country: str
    status: str


@dataclass(frozen=True)
class Relationship:
    id: str
    child_type: str
    child_id: str
    parent_type: str
    parent_id: str
    relationship_type: str
    effective_from: str
    effective_from_precision: str
    effective_until: str
    verification_status: str
    confidence: float
    last_verified_at: str


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    publisher: str
    source_type: str
    published_at: str
    retrieved_at: str
    notes: str


@dataclass(frozen=True)
class ResearchGap:
    id: str
    subject_type: str
    subject_id: str
    issue_type: str
    status: str
    confidence: float
    explanation: str


Entity = (Brand, Company, OwnershipGroup)
EntityTypes = Tuple[Brand, Company, OwnershipGroup]
OptionalEntity = Optional[object]
