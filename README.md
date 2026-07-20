# Ownership Scanner

Ownership Scanner is a feasibility-stage project for testing whether product-to-company ownership can be modeled and verified reliably before building a public application.

This repository currently contains:

- CSV templates for products, brands, companies, ownership relationships, and sources
- A standard-library Python validator
- Automated validator tests
- MVP, data-model, and manual-research documentation

The feasibility dataset now contains 13 real, manually researched products with sourced ownership chains.

## Run locally

Requires Python 3.10 or newer. No third-party packages are needed.

```bash
python3 scripts/validate_data.py --profile development
python3 scripts/validate_data.py --profile full
python3 -m unittest discover -s tests -v
```

Both the development and full feasibility profiles pass with the researched product set. The tests are expected to pass.

## Current boundary

This stage does not include a frontend, API, database, AI integration, or AWS resources. Those should begin only after the initial real product data is supplied or approved and the feasibility gate passes.

See [docs/manual-research-guide.md](docs/manual-research-guide.md) for the exact research workflow.
