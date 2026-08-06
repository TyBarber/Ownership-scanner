"""Explicit public API response models used for validation and OpenAPI."""

from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field


Confidence = Annotated[float, Field(ge=0, le=1)]
EntityType = Literal["brand", "company", "ownership_group"]
RelationshipType = Literal[
    "owned_by",
    "controlled_by_group",
    "affiliated_with_group",
]
VerificationStatus = Literal["verified", "probable", "unresolved"]
DatePrecision = Literal["year", "month", "day"]


class HealthResponse(BaseModel):
    status: Literal["healthy"]


class ProductBrand(BaseModel):
    id: str
    name: str


class ProductSummary(BaseModel):
    id: str
    gtin: str
    name: str
    category: str
    brand: ProductBrand


class ProductListResponse(BaseModel):
    products: List[ProductSummary]
    total: Annotated[int, Field(ge=0)]
    limit: Annotated[int, Field(ge=1, le=100)]
    offset: Annotated[int, Field(ge=0)]


class ProductDetail(BaseModel):
    id: str
    gtin: str
    name: str
    category: str
    package_company_text: str


class BrandDetail(BaseModel):
    id: str
    name: str
    website: str


class BrandReference(BaseModel):
    type: Literal["brand"]
    id: str
    name: str


class CompanyReference(BaseModel):
    type: Literal["company"]
    id: str
    name: str


class OwnershipGroupReference(BaseModel):
    type: Literal["ownership_group"]
    id: str
    name: str


EntityReference = Annotated[
    Union[BrandReference, CompanyReference, OwnershipGroupReference],
    Field(discriminator="type"),
]
ParentReference = Annotated[
    Union[CompanyReference, OwnershipGroupReference],
    Field(discriminator="type"),
]


class SupportingSource(BaseModel):
    title: str
    url: str
    publisher: str
    source_type: str
    support_type: Literal["primary", "secondary"]
    published_at: Optional[str]
    retrieved_at: str


class OwnershipRelationship(BaseModel):
    child: EntityReference
    relationship_type: RelationshipType
    parent: ParentReference
    verification_status: VerificationStatus
    confidence: Confidence
    effective_from: Optional[str]
    effective_from_precision: Optional[DatePrecision]
    effective_until: Optional[str]
    last_verified_at: str
    sources: List[SupportingSource]


class CompanyOwnershipPoint(CompanyReference):
    company_type: Literal["public", "private", "cooperative"]
    country: str


class OwnershipGroupPoint(OwnershipGroupReference):
    description: str
    country: str


HighestVerifiedOwnershipPoint = Annotated[
    Union[BrandReference, CompanyOwnershipPoint, OwnershipGroupPoint],
    Field(discriminator="type"),
]


class ResearchGapSubject(BaseModel):
    type: EntityType
    id: str


class ResearchGap(BaseModel):
    id: str
    subject: ResearchGapSubject
    issue_type: str
    status: Literal["unresolved"]
    confidence: Confidence
    explanation: str
    sources: List[SupportingSource]


class ProductOwnershipResponse(BaseModel):
    product: ProductDetail
    brand: BrandDetail
    ownership_chain: List[OwnershipRelationship]
    highest_verified_owner: HighestVerifiedOwnershipPoint
    chain_complete: bool
    overall_status: Literal["verified", "verified_with_gaps", "cycle_detected"]
    stop_reason: Literal[
        "terminal_owner",
        "research_gap",
        "unresolved_relationship",
        "multiple_verified_parents",
        "cycle_detected",
    ]
    research_gaps: List[ResearchGap]
