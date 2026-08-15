from app.config import settings
from app.integrations.mercado_livre import MercadoLivreClient
from app.providers.base import ProductSearchProvider
from app.repositories.offer_repository import save_offer_snapshot
from app.services.token_store import get_access_token


class MercadoLivreProviderError(RuntimeError):
    pass


class MercadoLivreProvider(ProductSearchProvider):
    name = "mercado_livre"

    def _access_token(self) -> str | None:
        return get_access_token() or settings.meli_access_token

    def status(self) -> dict:
        return {
            "name": self.name,
            "available": bool(self._access_token()),
            "authenticated": bool(self._access_token()),
            "note": (
                "OAuth is configured. Generic marketplace search may be "
                "restricted by Mercado Livre API policy."
            ),
        }

    def search_offers(
        self,
        query: str,
        max_price: float | None = None,
        limit: int = 20,
    ) -> list[dict]:
        access_token = self._access_token()

        if not access_token:
            raise MercadoLivreProviderError(
                "Mercado Livre is not authenticated. "
                "Complete the OAuth authorization flow before searching."
            )

        client = MercadoLivreClient(
            access_token=access_token,
            site_id=settings.meli_site_id,
        )

        offers = client.search(
            query=query,
            max_price=max_price,
            limit=limit,
        )

        result = []

        for offer in offers:
            save_offer_snapshot(offer)

            original = offer.original_price or offer.price
            discount = (
                0.0
                if original <= offer.price
                else round((1 - offer.price / original) * 100, 1)
            )

            deal_score = min(
                100.0,
                round(55 + min(discount, 30) * 1.5, 1),
            )

            result.append(
                {
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
                    "source": self.name,
                }
            )

        return sorted(
            result,
            key=lambda item: (-item["deal_score"], item["price"]),
        )
