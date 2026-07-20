from test_repository import EXPECTED_GTINS


def test_health(client):
    assert client.get("/health").json() == {"status": "healthy"}


def test_openapi_docs_are_available(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_all_thirteen_products_resolve_over_http(client):
    for gtin in EXPECTED_GTINS:
        response = client.get("/products/{}".format(gtin))
        assert response.status_code == 200, (gtin, response.text)
        assert response.json()["product"]["gtin"] == gtin


def test_malformed_and_unknown_gtins(client):
    malformed = client.get("/products/not-a-barcode")
    unknown = client.get("/products/000000000000")
    assert malformed.status_code == 400
    assert unknown.status_code == 404


def test_pagination(client):
    first = client.get("/products", params={"limit": 5, "offset": 0}).json()
    second = client.get("/products", params={"limit": 5, "offset": 5}).json()
    assert first["total"] == 13
    assert len(first["products"]) == 5
    assert len(second["products"]) == 5
    assert {item["gtin"] for item in first["products"]}.isdisjoint(
        {item["gtin"] for item in second["products"]}
    )


def test_brand_and_category_filters(client):
    brand = client.get("/products", params={"brand": "Gerber"}).json()
    category = client.get("/products", params={"category": "Yogurt"}).json()
    assert [item["gtin"] for item in brand["products"]] == ["015000047313"]
    assert [item["gtin"] for item in category["products"]] == ["689544083023"]


def test_invalid_pagination_is_rejected(client):
    assert client.get("/products", params={"limit": 0}).status_code == 422
    assert client.get("/products", params={"offset": -1}).status_code == 422
