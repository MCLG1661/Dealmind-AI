from __future__ import annotations

import os

from app.integrations.serper import SerperClient, SerperError
from app.providers.base import ProductSearchProvider


class SerperProviderError(RuntimeError):
    pass


class SerperProvider(ProductSearchProvider):
    name = "serper"

    def _api_key(self) -> str | None:
        value = os.getenv("SERPER_API_KEY")
        return value.strip() if value else None

    def status(self) -> dict:
        return {
            "name": self.name,
            "available": bool(self._api_key()),
            "authenticated": bool(self._api_key()),
            "note": "Google Shopping search via Serper API.",
        }

    def search_offers(
        self,
        query: str,
        max_price: float | None = None,
        limit: int = 20,
    ) -> list[dict]:
        api_key = self._api_key()

        if not api_key:
            raise SerperProviderError(
                "SERPER_API_KEY is not configured."
            )

        try:
            client = SerperClient(api_key=api_key)

            offers = client.search(
                query=query,
                max_price=max_price,
                limit=limit,
            )
        except SerperError as exc:
            raise SerperProviderError(str(exc)) from exc

        result = []

        for offer in offers:
            original = offer.original_price or offer.price

            discount = (
                0.0
                if original <= offer.price
                else round(
                    (1 - offer.price / original) * 100,
                    1,
                )
            )

            deal_score = min(
                100.0,
                round(
                    55 + min(discount, 30) * 1.5,
                    1,
                ),
            )

            result.append(
                {
                    "id": offer.external_id,
                    "name": offer.title,
                    "store": offer.store,
                    "price": offer.price,
                    "original_price": offer.original_price,
                    "discount_percent": discount,
                    "deal_score": deal_score,
                    "url": offer.link,
                    "thumbnail": offer.image_url,
                    "rating": offer.rating,
                    "rating_count": offer.rating_count,
                    "source": self.name,
                }
            )

        return sorted(
            result,
            key=lambda item: (
                -item["deal_score"],
                item["price"],
            ),
        )