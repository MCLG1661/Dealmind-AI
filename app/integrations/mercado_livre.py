from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


class MercadoLivreError(RuntimeError):
    pass


@dataclass(frozen=True)
class MercadoLivreOffer:
    external_id: str
    title: str
    price: float
    original_price: float | None
    permalink: str
    thumbnail: str | None
    seller_id: int | None
    category_id: str | None
    currency_id: str = "BRL"


class MercadoLivreClient:
    BASE_URL = "https://api.mercadolibre.com"

    def __init__(
        self,
        access_token: str,
        site_id: str = "MLB",
        session: requests.Session | None = None,
        timeout: int = 15,
    ) -> None:
        if not access_token:
            raise ValueError("Mercado Livre access token is required.")
        self.access_token = access_token
        self.site_id = site_id
        self.session = session or requests.Session()
        self.timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "User-Agent": "DealMindAI/0.2",
        }

    def search(
        self,
        query: str,
        limit: int = 20,
        max_price: float | None = None,
    ) -> list[MercadoLivreOffer]:
        params: dict[str, Any] = {
            "q": query,
            "limit": min(max(limit, 1), 50),
        }

        response = self.session.get(
            f"{self.BASE_URL}/sites/{self.site_id}/search",
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )

        if response.status_code in (401, 403):
            raise MercadoLivreError(
                f"Mercado Livre API returned HTTP {response.status_code}: "
                f"{response.text}"
            )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise MercadoLivreError(
                f"Mercado Livre API returned HTTP {response.status_code}: "
                f"{response.text}"
            ) from exc

        payload = response.json()
        offers = []

        for item in payload.get("results", []):
            price = item.get("price")
            if price is None:
                continue

            price = float(price)
            if max_price is not None and price > max_price:
                continue

            seller = item.get("seller")
            seller_id = (
                seller.get("id")
                if isinstance(seller, dict)
                else item.get("seller_id")
            )

            offers.append(
                MercadoLivreOffer(
                    external_id=str(item.get("id", "")),
                    title=str(item.get("title", "")),
                    price=price,
                    original_price=(
                        float(item["original_price"])
                        if item.get("original_price") is not None
                        else None
                    ),
                    permalink=str(item.get("permalink", "")),
                    thumbnail=item.get("thumbnail"),
                    seller_id=seller_id,
                    category_id=item.get("category_id"),
                    currency_id=str(item.get("currency_id", "BRL")),
                )
            )

        return offers
