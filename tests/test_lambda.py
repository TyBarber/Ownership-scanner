import importlib
import json
import shutil
from types import SimpleNamespace

import pytest
from mangum import Mangum

from ownership_scanner.api import create_app
from ownership_scanner.config import REQUIRED_CSV_FILES, resolve_data_dir
from ownership_scanner.errors import DataConfigurationError, DataIntegrityError


def http_api_event(path, raw_query_string="", query_parameters=None):
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": path,
        "rawQueryString": raw_query_string,
        "headers": {"accept": "application/json", "host": "example.execute-api.us-east-1.amazonaws.com"},
        "queryStringParameters": query_parameters,
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "example",
            "domainName": "example.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "example",
            "http": {
                "method": "GET",
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "pytest",
            },
            "requestId": "test-request",
            "routeKey": "$default",
            "stage": "$default",
            "time": "20/Jul/2026:12:00:00 +0000",
            "timeEpoch": 1784548800000,
        },
        "isBase64Encoded": False,
    }


def invoke(handler, path, raw_query_string="", query_parameters=None):
    response = handler(
        http_api_event(path, raw_query_string, query_parameters),
        SimpleNamespace(function_name="ownership-scanner", aws_request_id="test-request"),
    )
    response["json"] = json.loads(response["body"])
    return response


@pytest.fixture
def lambda_module():
    return importlib.import_module("ownership_scanner.lambda_handler")


def test_lambda_handler_imports_and_is_global(lambda_module):
    assert isinstance(lambda_module.handler, Mangum)
    assert lambda_module.handler is importlib.import_module(
        "ownership_scanner.lambda_handler"
    ).handler


def test_http_api_v2_health(lambda_module):
    response = invoke(lambda_module.handler, "/health")
    assert response["statusCode"] == 200
    assert response["json"] == {"status": "healthy"}


def test_http_api_v2_product(lambda_module):
    response = invoke(lambda_module.handler, "/products/850017142350")
    assert response["statusCode"] == 200
    assert response["json"]["product"]["gtin"] == "850017142350"


def test_http_api_v2_query_string(lambda_module):
    response = invoke(
        lambda_module.handler,
        "/products",
        "brand=FAGE&limit=1",
        {"brand": "FAGE", "limit": "1"},
    )
    assert response["statusCode"] == 200
    assert response["json"]["total"] == 1
    assert response["json"]["products"][0]["gtin"] == "689544083023"


def test_http_api_v2_malformed_and_unknown_gtins(lambda_module):
    malformed = invoke(lambda_module.handler, "/products/not-a-barcode")
    unknown = invoke(lambda_module.handler, "/products/000000000000")
    assert malformed["statusCode"] == 400
    assert unknown["statusCode"] == 404


def test_http_api_v2_trader_joes_research_gap(lambda_module):
    response = invoke(lambda_module.handler, "/products/00712996")
    assert response["statusCode"] == 200
    assert response["json"]["chain_complete"] is False
    assert response["json"]["highest_verified_owner"]["type"] == "ownership_group"
    assert response["json"]["research_gaps"][0]["status"] == "unresolved"


def test_packaged_data_discovery(tmp_path, repository, monkeypatch):
    monkeypatch.delenv("OWNERSHIP_DATA_DIR", raising=False)
    package_root = tmp_path / "artifact"
    shutil.copytree(repository.data_dir, package_root / "data")
    resolved = resolve_data_dir(
        packaged_root=package_root,
        local_root=tmp_path / "missing-local-root",
    )
    assert resolved == (package_root / "data").resolve()


def test_explicit_data_directory_override(tmp_path, repository, monkeypatch):
    override = tmp_path / "override-data"
    shutil.copytree(repository.data_dir, override)
    monkeypatch.setenv("OWNERSHIP_DATA_DIR", str(override))
    assert resolve_data_dir() == override.resolve()


def test_missing_dataset_fails_clearly(tmp_path, monkeypatch):
    monkeypatch.delenv("OWNERSHIP_DATA_DIR", raising=False)
    with pytest.raises(DataConfigurationError, match="unavailable"):
        resolve_data_dir(
            packaged_root=tmp_path / "missing-package",
            local_root=tmp_path / "missing-local",
        )


def test_incomplete_dataset_fails_clearly(tmp_path, monkeypatch):
    monkeypatch.delenv("OWNERSHIP_DATA_DIR", raising=False)
    data = tmp_path / "artifact" / "data"
    data.mkdir(parents=True)
    (data / REQUIRED_CSV_FILES[0]).write_text("id\n", encoding="utf-8")
    with pytest.raises(DataConfigurationError, match="incomplete"):
        resolve_data_dir(packaged_root=tmp_path / "artifact")


def test_warm_invocations_reuse_global_handler(lambda_module):
    handler_id = id(lambda_module.handler)
    assert invoke(lambda_module.handler, "/health")["statusCode"] == 200
    assert invoke(lambda_module.handler, "/health")["statusCode"] == 200
    assert id(lambda_module.handler) == handler_id


def test_public_500_does_not_expose_internal_path_or_entity_id():
    class BrokenRepository:
        def get_product(self, gtin):
            raise DataIntegrityError(
                "/private/internal/data/products.csv contains company-secret-entity-id"
            )

    handler = Mangum(create_app(BrokenRepository()), lifespan="off")
    response = invoke(handler, "/products/850017142350")
    assert response["statusCode"] == 500
    assert response["json"] == {"detail": "Internal server error"}
    assert "/private/" not in response["body"]
    assert "company-secret-entity-id" not in response["body"]
