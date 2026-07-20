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

## AWS Lambda compatibility

The approved cloud target is AWS Lambda using Python 3.12 on Linux x86_64,
behind an API Gateway HTTP API with payload format 2.0. The Lambda handler is:

```text
ownership_scanner.lambda_handler.handler
```

Mangum wraps the existing FastAPI application. The app, CSV repository, service,
and handler are initialized once at module import so a warm Lambda environment
can reuse them. Uvicorn remains a local-development dependency and is not
started or packaged for Lambda.

Canonical data is discovered in this order:

1. `OWNERSHIP_DATA_DIR`, when explicitly set
2. the packaged `data/` directory beside the deployed application package
3. the repository-root `data/` directory during local development

The selected directory must contain all nine required CSV files. Startup fails
if the configured or discovered dataset is missing or incomplete.

### Build and verify the Lambda artifact

The builder downloads CPython 3.12 manylinux x86_64 wheels directly into an
isolated staging directory. It never copies packages from the local virtual
environment, which makes it safe to run from an Apple Silicon Mac.

```bash
python scripts/build_lambda_artifact.py
python scripts/verify_lambda_artifact.py
```

The output is `dist/ownership-scanner-lambda.zip`. The verifier lists the ZIP,
checks all nine CSVs and required packages, rejects tests, documentation,
virtual environments, caches, local-only dependencies, likely secrets, intake
photos, and absolute Mac paths, validates Linux x86_64 binary extensions, imports
the packaged handler code, and reports compressed and uncompressed sizes.

AWS infrastructure has not been provisioned. There are no IAM roles, API
Gateway resources, deployment commands, Terraform files, alarms, or budgets in
this repository yet.

## Current boundary

This stage does not include a frontend, database, authentication, AI integration, or provisioned AWS resources.

See [docs/manual-research-guide.md](docs/manual-research-guide.md) for the exact research workflow.
