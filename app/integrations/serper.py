from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

import requests


class SerperError(RuntimeError):
    pass


@dataclass(frozen=True)
class SerperOffer:
    external_id: str
    title: str
    store: str
    price: float
    original_price: float | None
    link: str
    image_url: str | None
    rating: float | None
    rating_count: int | None
    currency_id: str = "BRL"


def _parse_price(value: Any) -> float | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()

    # Remove moeda e outros caracteres, preservando separadores.
    numeric = re.sub(r"[^\d,.\-]", "", text)

    if not numeric:
        return None

    # Formato brasileiro: 1.299,90
    if "," in numeric:
        numeric = numeric.replace(".", "").replace(",", ".")
    # Formato internacional: 1299.90
    elif numeric.count(".") > 1:
        numeric = numeric.replace(".", "")

    try:
        return float(numeric)
    except ValueError:
        return None


class SerperClient:
    BASE_URL = "https://google.serper.dev/shopping"

    def __init__(
        self,
        api_key: str,
        session: requests.Session | None = None,
        timeout: int = 15,
    ) -> None:
        if not api_key:
            raise ValueError("Serper API key is required.")

        self.api_key = api_key
        self.session = session or requests.Session()
        self.timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        return {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

    def search(
        self,
        query: str,
        limit: int = 20,
        max_price: float | None = None,
    ) -> list[SerperOffer]:
        requested_limit = min(max(limit, 1), 50)

        payload = {
            "q": query,
            "gl": "br",
            "hl": "pt-br",
            "num": requested_limit,
        }

        response = self.session.post(
            self.BASE_URL,
            headers=self.headers,
            json=payload,
            timeout=self.timeout,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise SerperError(
                f"Serper API returned HTTP {response.status_code}: "
                f"{response.text}"
            ) from exc

        data = response.json()
        offers: list[SerperOffer] = []

        for position, item in enumerate(data.get("shopping", []), start=1):
            price = _parse_price(item.get("price"))

            if price is None:
                continue

            if max_price is not None and price > max_price:
                continue

            external_id = str(
                item.get("productId")
                or item.get("product_id")
                or f"SERPER-{position}"
            )

            rating = item.get("rating")
            rating_count = item.get("ratingCount")

            offers.append(
                SerperOffer(
                    external_id=external_id,
                    title=str(item.get("title", "")),
                    store=str(item.get("source", "Google Shopping")),
                    price=price,
                    original_price=_parse_price(
                        item.get("oldPrice")
                        or item.get("originalPrice")
                    ),
                    link=str(item.get("link", "")),
                    image_url=item.get("imageUrl"),
                    rating=float(rating) if rating is not None else None,
                    rating_count=(
                        int(rating_count)
                        if rating_count is not None
                        else None
                    ),
                )
            )

        return offers[:requested_limit]