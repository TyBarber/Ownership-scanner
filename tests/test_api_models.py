import pytest
from pydantic import ValidationError

from ownership_scanner.api_models import (
    HealthResponse,
    ProductListResponse,
    ProductOwnershipResponse,
)
from ownership_scanner.ownership_service import OwnershipService
from test_repository import EXPECTED_GTINS


def _successful_response_schema(client, path):
    schema = client.get("/openapi.json").json()
    response = schema["paths"][path]["get"]["responses"]["200"]
    return response["content"]["application/json"]["schema"]


def test_response_models_validate_actual_endpoint_responses(client):
    health = client.get("/health")
    products = client.get("/products")
    ownership = client.get("/products/850017142350")

    assert HealthResponse.model_validate(health.json()).status == "healthy"
    assert ProductListResponse.model_validate(products.json()).total == 13
    assert (
        ProductOwnershipResponse.model_validate(ownership.json()).product.gtin
        == "850017142350"
    )


def test_response_models_preserve_existing_service_payloads(client, repository):
    service = OwnershipService(repository)

    assert client.get("/products").json() == service.list_products()
    for gtin in EXPECTED_GTINS:
        assert client.get("/products/{}".format(gtin)).json() == (
            service.get_product_ownership(gtin)
        )


@pytest.mark.parametrize(
    ("path", "model_name"),
    [
        ("/health", "HealthResponse"),
        ("/products", "ProductListResponse"),
        ("/products/{gtin}", "ProductOwnershipResponse"),
    ],
)
def test_openapi_success_responses_reference_explicit_models(client, path, model_name):
    response_schema = _successful_response_schema(client, path)
    assert response_schema == {
        "$ref": "#/components/schemas/{}".format(model_name)
    }


def test_openapi_ownership_schema_is_nonempty_and_nested(client):
    schema = client.get("/openapi.json").json()
    components = schema["components"]["schemas"]
    ownership = components["ProductOwnershipResponse"]

    assert ownership["type"] == "object"
    assert "ownership_chain" in ownership["properties"]
    assert "highest_verified_owner" in ownership["properties"]
    assert "research_gaps" in ownership["properties"]
    assert components["OwnershipRelationship"]["properties"]["confidence"]["maximum"] == 1
    assert components["OwnershipRelationship"]["properties"]["confidence"]["minimum"] == 0


def test_trader_joes_gap_validates_as_an_ownership_group(client):
    response = client.get("/products/00712996")
    model = ProductOwnershipResponse.model_validate(response.json())

    assert response.status_code == 200
    assert model.chain_complete is False
    assert model.overall_status == "verified_with_gaps"
    assert model.highest_verified_owner.type == "ownership_group"
    assert model.research_gaps[0].status == "unresolved"
    assert model.research_gaps[0].issue_type == "unresolved_parent_structure"


def test_cooperative_and_ownership_group_points_are_distinguishable(client):
    cooperative = ProductOwnershipResponse.model_validate(
        client.get("/products/041190055661").json()
    )
    ownership_group = ProductOwnershipResponse.model_validate(
        client.get("/products/00712996").json()
    )

    assert cooperative.highest_verified_owner.type == "company"
    assert cooperative.highest_verified_owner.company_type == "cooperative"
    assert ownership_group.highest_verified_owner.type == "ownership_group"
    assert ownership_group.highest_verified_owner.description


def test_partial_date_and_precision_survive_response_validation(client):
    response = client.get("/products/072940757092")
    model = ProductOwnershipResponse.model_validate(response.json())
    serialized = model.model_dump(mode="json")

    assert serialized["ownership_chain"][0]["effective_from"] == "2001"
    assert serialized["ownership_chain"][0]["effective_from_precision"] == "year"


def test_confidence_bounds_are_validated(client):
    payload = client.get("/products/850017142350").json()
    payload["ownership_chain"][0]["confidence"] = 1.1

    with pytest.raises(ValidationError):
        ProductOwnershipResponse.model_validate(payload)


def test_success_models_do_not_change_existing_status_behavior(client):
    assert client.get("/health").status_code == 200
    assert client.get("/products").status_code == 200
    assert client.get("/products/850017142350").status_code == 200
    assert client.get("/products/not-a-barcode").status_code == 400
    assert client.get("/products/000000000000").status_code == 404
    assert client.get("/products", params={"limit": 0}).status_code == 422
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200
