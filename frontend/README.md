# Protest frontend

This directory contains the local React, TypeScript, and Vite frontend for
Protest — Product Ownership Intelligence.

The first milestone includes the application foundation, typed API client,
product catalog and manual GTIN lookup, ownership results, methodology, and
about pages. Camera barcode scanning and production frontend deployment are not
implemented yet.

## Install and run

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

The browser calls `/api`, which Vite proxies to the configured API target. No
credentials belong in frontend environment files.

### Use the local FastAPI service

Start FastAPI from the repository root:

```bash
source .venv/bin/activate
python -m uvicorn ownership_scanner.api:app --reload
```

Use this frontend configuration:

```dotenv
VITE_API_BASE_URL=/api
VITE_API_PROXY_TARGET=http://127.0.0.1:8000
```

### Use the deployed development API

Keep the browser on the local Vite origin and point the development proxy at the
public API:

```dotenv
VITE_API_BASE_URL=/api
VITE_API_PROXY_TARGET=https://83fwv16l3j.execute-api.us-east-1.amazonaws.com
```

Restart Vite after changing `.env.local`.

## Quality checks

```bash
npm test
npm run typecheck
npm run lint
npm run build
```

`npm run generate:api` explicitly refreshes `src/api/generated.ts` from the
deployed OpenAPI contract. Normal development and production builds use the
committed generated types and do not fetch the live schema.

Runtime Zod schemas validate external responses before the UI displays them.
The generated OpenAPI types and runtime schemas should be reviewed together
whenever the backend response contract changes.
