from app.integrations.mercado_livre import MercadoLivreOffer

def test_offer_shape():
    offer = MercadoLivreOffer(
        external_id="MLB1",
        title="Produto",
        price=100.0,
        original_price=150.0,
        permalink="https://example.com",
        thumbnail=None,
        seller_id=1,
        category_id="MLBTEST",
    )
    assert offer.price < offer.original_price
    assert offer.currency_id == "BRL"
