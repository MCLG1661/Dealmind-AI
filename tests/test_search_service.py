from app.services.search_service import search_products


def test_search_by_product_name():
    result = search_products("Puma")
    assert result
    assert result[0].name == "Puma Darter Pro"


def test_search_respects_budget():
    result = search_products("tênis corrida", max_price=360)
    assert result
    assert all(product.price <= 360 for product in result)
