import csv


EXPECTED_GTINS = {
    "074117000734",
    "00712996",
    "041190055661",
    "072940757092",
    "058449870241",
    "689544083023",
    "850017142350",
    "051000010315",
    "00016000124790",
    "00810063710323",
    "085239276495",
    "071012010509",
    "015000047313",
}


def test_repository_loads_all_gtins_as_strings(repository):
    assert {product.gtin for product in repository.products} == EXPECTED_GTINS
    assert all(isinstance(product.gtin, str) for product in repository.products)


def test_repository_filters_by_brand_and_category(repository):
    fage = repository.list_products(brand="fage")
    canned = repository.list_products(category="canned")
    assert [product.gtin for product, _ in fage] == ["689544083023"]
    assert {product.gtin for product, _ in canned} == {
        "00712996",
        "041190055661",
        "072940757092",
        "051000010315",
    }


def test_every_confirmed_relationship_has_a_source(repository):
    verified = [item for item in repository.relationships if item.verification_status == "verified"]
    assert verified
    for relationship in verified:
        assert repository.sources_for_relationship(relationship.id), relationship.id


def test_retailer_owned_cooperative_is_typed(repository):
    wakefern = repository.get_entity("company", "company-wakefern-food-corp")
    assert wakefern.company_type == "cooperative"
