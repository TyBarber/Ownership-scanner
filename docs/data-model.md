# Data Model

## Entities

### Product

A packaged item identified by a GTIN and associated with one brand. `package_company_text` preserves the manufacturer/distributor wording printed on the physical package; it is evidence to research, not proof of ownership.

### Brand

A consumer-facing identity. A brand may be the child of a company in an ownership relationship.

### Company

A legal or operating entity. A company may own a brand and may itself be owned by another company.

### Ownership relationship

One directed edge from a child brand, company, or ownership group to a parent company or ownership group. Intermediate entities must be represented as separate edges. The highest verified owner is derived by traversing verified active edges and is never stored on a product. A terminal record is not automatically claimed to be the ultimate owner.

Dates describe the relationship's known effective interval. A blank end date means no known end. Status and confidence preserve uncertainty rather than presenting it as fact.

### Source

Evidence cited by an ownership edge. `relationship_sources.csv` provides a many-to-many join so an edge can cite several sources without duplicating the ownership claim. Every relationship requires at least one source, including unresolved and probable edges retained for review.

### Ownership group

A consumer-level affiliation grouping used only when credible evidence supports group control but does not identify an exact immediate parent legal entity. It must not be substituted for a company or silently presented as exact legal parentage.

### Research gap

A structured unresolved question attached to a real entity. It records issue type, confidence, explanation, and supporting incomplete or conflicting sources without inventing a parent entity or ownership edge.

## Relationship rules

```text
Product --belongs to--> Brand
Brand --owned_by--> Company
Company --owned_by--> Company
Company --controlled by--> Ownership group
Ownership relationship --supported by--> Source
```

- `child_type` is `brand`, `company`, or `ownership_group`.
- `parent_type` is `company` or `ownership_group`.
- `relationship_type` is `owned_by`, `controlled_by_group`, or `affiliated_with_group`.
- `verification_status` is `verified`, `probable`, or `unresolved`.
- `confidence` is between 0 and 1 inclusive.
- `effective_from_precision` is `day` or `year`; year-only evidence is stored as `YYYY` without invented month/day precision.
- Effective end cannot precede effective start.
- Company ownership must be acyclic.
- Confirmed traversal uses only `verified` edges. Probable and unresolved edges are never returned as facts.
- A publishable brand chain must resolve without broken references, multiple confirmed parents, or cycles.

## IDs and placeholders

IDs are stable strings. Rows whose ID starts with `placeholder-` are templates only and never count toward the feasibility gate. Replace them with researched records rather than treating them as facts.
