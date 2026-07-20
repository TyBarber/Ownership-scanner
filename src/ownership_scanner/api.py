"""FastAPI transport for the framework-independent ownership domain."""

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from .config import Settings
from .errors import DataIntegrityError, InvalidGtinError, ProductNotFoundError
from .ownership_service import OwnershipService
from .repository import CsvRepository


LOGGER = logging.getLogger(__name__)
PUBLIC_INTERNAL_ERROR = "Internal server error"


def create_app(repository: Optional[CsvRepository] = None) -> FastAPI:
    repository = repository or CsvRepository(Settings().data_dir)
    service = OwnershipService(repository)
    application = FastAPI(title="Ownership Scanner API", version="0.1.0")

    @application.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        LOGGER.exception(
            "Unexpected API failure while handling %s %s",
            request.method,
            request.url.path,
            exc_info=exc,
        )
        return JSONResponse(status_code=500, content={"detail": PUBLIC_INTERNAL_ERROR})

    @application.get("/health")
    def health():
        return {"status": "healthy"}

    @application.get("/products")
    def products(
        brand: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = Query(100, ge=1, le=100),
        offset: int = Query(0, ge=0),
    ):
        return service.list_products(brand=brand, category=category, limit=limit, offset=offset)

    @application.get("/products/{gtin}")
    def product(gtin: str, request: Request):
        try:
            return service.get_product_ownership(gtin)
        except InvalidGtinError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except ProductNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except DataIntegrityError as exc:
            LOGGER.exception(
                "Canonical data failure while handling %s %s",
                request.method,
                request.url.path,
                exc_info=exc,
            )
            raise HTTPException(status_code=500, detail=PUBLIC_INTERNAL_ERROR) from exc

    return application


app = create_app()
