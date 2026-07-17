# Initial MVP

## Purpose

Determine whether product ownership data can be represented, sourced, reviewed, and kept honest enough to justify building a consumer product.

## Included

- US packaged grocery and household products
- Barcode lookup or manual barcode entry
- Product, brand, direct owner, intermediate subsidiaries, and highest verified ownership entity
- Sources supporting each published ownership relationship
- Last-verified dates and explicit verification status
- Correction reporting in a later MVP iteration

## Excluded initially

- Ethical or political company ratings
- Claims that companies are good or bad
- Product recommendations
- Native mobile applications
- Social features
- Custom-trained ML models
- Automatically publishing AI-generated ownership claims

## Feasibility gate

Proceed only when all of the following are true:

- At least 10 real products have been entered.
- At least five real brands are represented.
- At least three distinct highest verified ownership entities are reached by traversing active verified ownership relationships.
- Every confirmed ownership edge has a credible source.
- Conflicting or insufficient evidence is marked `unresolved` for review.
- The validator and all automated tests pass.

Placeholder rows never count toward this gate.

During data development, `python3 scripts/validate_data.py --profile development` uses a five-product minimum. The full feasibility decision remains governed by `--profile full`, which requires 10 products and must continue to report progress until that threshold is reached.

## Stop condition

Do not begin the frontend, API, database, AI integration, or AWS deployment until the initial real product dataset is provided or approved.
