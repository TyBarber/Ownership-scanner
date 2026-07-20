"""FastAPI transport for the framework-independent ownership domain."""

from typing import Optional

from fastapi import FastAPI, HTTPException, Query

from .config import Settings
from .errors import DataIntegrityError, InvalidGtinError, ProductNotFoundError
from .ownership_service import OwnershipService
from .repository import CsvRepository


def create_app(repository: Optional[CsvRepository] = None) -> FastAPI:
    repository = repository or CsvRepository(Settings().data_dir)
    service = OwnershipService(repository)
    application = FastAPI(title="Ownership Scanner API", version="0.1.0")

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
    def product(gtin: str):
        try:
            return service.get_product_ownership(gtin)
        except InvalidGtinError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except ProductNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except DataIntegrityError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return application


app = create_app()
