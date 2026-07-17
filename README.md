# Ownership Scanner

Ownership Scanner is a feasibility-stage project for testing whether product-to-company ownership can be modeled and verified reliably before building a public application.

This repository currently contains:

- CSV templates for products, brands, companies, ownership relationships, and sources
- A standard-library Python validator
- Automated validator tests
- MVP, data-model, and manual-research documentation

It intentionally contains placeholder data only. The feasibility gate must remain closed until at least 10 real, manually researched products and their sourced ownership chains have been entered.

## Run locally

Requires Python 3.10 or newer. No third-party packages are needed.

```bash
python3 scripts/validate_data.py --profile development
python3 scripts/validate_data.py --profile full
python3 -m unittest discover -s tests -v
```

The development profile passes with the five researched products. The full feasibility profile intentionally continues to fail until 10 real products have been researched. The tests are expected to pass.

## Current boundary

This stage does not include a frontend, API, database, AI integration, or AWS resources. Those should begin only after the initial real product data is supplied or approved and the feasibility gate passes.

See [docs/manual-research-guide.md](docs/manual-research-guide.md) for the exact research workflow.
