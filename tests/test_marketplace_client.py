from app.integrations.mercado_livre import MercadoLivreClient

class FakeResponse:
    status_code = 200
    def raise_for_status(self):
        return None
    def json(self):
        return {
            "results": [{
                "id": "MLB123",
                "title": "Tênis Running Teste",
                "price": 299.90,
                "original_price": 399.90,
                "permalink": "https://produto.example/MLB123",
                "thumbnail": "https://img.example/test.jpg",
                "seller": {"id": 10},
                "category_id": "MLB1234",
                "currency_id": "BRL",
            }]
        }

class FakeSession:
    def get(self, url, headers, params, timeout):
        assert "Authorization" in headers
        assert params["q"] == "tenis corrida"
        return FakeResponse()

def test_marketplace_search_normalizes_offer():
    client = MercadoLivreClient(
        access_token="test-token",
        session=FakeSession(),
    )
    offers = client.search("tenis corrida")
    assert len(offers) == 1
    assert offers[0].external_id == "MLB123"
    assert offers[0].price == 299.90
    assert offers[0].original_price == 399.90
