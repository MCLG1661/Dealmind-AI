from app.config import settings
from app.integrations.mercado_livre import MercadoLivreClient
from app.repositories.offer_repository import save_offer_snapshot

class MarketplaceNotConfigured(RuntimeError):
    pass

def search_marketplace(query: str, max_price: float | None = None,
                       limit: int = 20) -> list[dict]:
    if not settings.meli_access_token:
        raise MarketplaceNotConfigured(
            "MELI_ACCESS_TOKEN is not configured. "
            "Create a Mercado Livre Developers application and add the token to .env."
        )

    client = MercadoLivreClient(
        access_token=settings.meli_access_token,
        site_id=settings.meli_site_id,
    )

    offers = client.search(query=query, max_price=max_price, limit=limit)
    result = []

    for offer in offers:
        save_offer_snapshot(offer)
        original = offer.original_price or offer.price
        discount = 0.0 if original <= offer.price else round((1 - offer.price / original) * 100, 1)
        deal_score = min(100.0, round(55 + min(discount, 30) * 1.5, 1))

        result.append({
            "id": offer.external_id,
            "name": offer.title,
            "store": "Mercado Livre",
            "price": offer.price,
            "original_price": offer.original_price,
            "discount_percent": discount,
            "deal_score": deal_score,
            "url": offer.permalink,
            "thumbnail": offer.thumbnail,
            "category_id": offer.category_id,
            "source": "mercado_livre",
        })

    return sorted(result, key=lambda item: (-item["deal_score"], item["price"]))
