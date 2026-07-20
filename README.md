# Ownership Scanner

Ownership Scanner is a feasibility-stage project for testing whether product-to-company ownership can be modeled and verified reliably. It includes a local, read-only API over the canonical CSV dataset.

This repository currently contains:

- CSV templates for products, brands, companies, ownership relationships, and sources
- A standard-library Python validator
- Automated validator tests
- A framework-independent ownership traversal service
- A local FastAPI HTTP interface
- MVP, data-model, and manual-research documentation

The feasibility dataset now contains 13 real, manually researched products with sourced ownership chains.

## Install

Requires Python 3.9 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.lock
python -m pip install --no-build-isolation --no-deps -e .
```

## Validate and test

```bash
python3 scripts/validate_data.py --profile development
python3 scripts/validate_data.py --profile full
python -m pytest
```

Both the development and full feasibility profiles pass with the researched product set. The tests are expected to pass.

## Start the local API

```bash
python -m uvicorn ownership_scanner.api:app --reload
```

Open the interactive OpenAPI documentation at <http://127.0.0.1:8000/docs>.

Example product lookup (the quotes preserve the GTIN as text in the shell):

```bash
curl "http://127.0.0.1:8000/products/00016000124790"
```

## Current boundary

This stage does not include a frontend, database, authentication, AI integration, or AWS resources.

See [docs/manual-research-guide.md](docs/manual-research-guide.md) for the exact research workflow.
