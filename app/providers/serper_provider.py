from __future__ import annotations

import math
import os
from statistics import mean

from app.integrations.serper import SerperClient, SerperError
from app.providers.base import ProductSearchProvider
from app.repositories.offer_repository import (
    get_price_history,
    save_price_snapshot,
)


class SerperProviderError(RuntimeError):
    pass


def calculate_serper_deal_score(
    price: float,
    min_price: float,
    max_price: float,
    rating: float | None = None,
    rating_count: int | None = None,
    discount_percent: float = 0.0,
    historical_average: float | None = None,
) -> float:
    """
    Deal Score v2 para ofertas de Shopping.

    Componentes:
    - 40 pontos-base
    - até 25 por competitividade de preço
    - até 10 pela avaliação
    - até 5 pelo volume de avaliações
    - até 10 por desconto
    - até 10 pelo preço atual versus histórico
    """

    score = 40.0

    # 1. Competitividade dentro das ofertas encontradas
    if max_price > min_price:
        competitiveness = (
            (max_price - price) / (max_price - min_price)
        )
        score += max(0.0, min(competitiveness, 1.0)) * 25.0
    else:
        score += 12.5

    # 2. Rating
    if rating is not None:
        normalized_rating = max(0.0, min(float(rating), 5.0)) / 5.0
        score += normalized_rating * 10.0

    # 3. Quantidade de avaliações
    if rating_count:
        review_strength = min(
            math.log10(max(rating_count, 1) + 1) / 3.0,
            1.0,
        )
        score += review_strength * 5.0

    # 4. Desconto anunciado
    if discount_percent > 0:
        normalized_discount = min(discount_percent, 30.0) / 30.0
        score += normalized_discount * 10.0

    # 5. Histórico do próprio produto
    if historical_average and historical_average > 0:
        variation_vs_history = (
            historical_average - price
        ) / historical_average

        if variation_vs_history > 0:
            historical_bonus = min(
                variation_vs_history / 0.20,
                1.0,
            ) * 10.0

            score += historical_bonus

    return round(min(score, 100.0), 1)


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
            "note": (
                "Busca real de ofertas via Google Shopping / Serper API."
            ),
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

        if not offers:
            return []

        prices = [float(offer.price) for offer in offers]

        batch_min_price = min(prices)
        batch_max_price = max(prices)

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

            # Histórico anterior — antes de salvar a captura atual
            history = get_price_history(offer.external_id)

            historical_average = None

            if history:
                historical_prices = [
                    float(item["price"])
                    for item in history
                ]

                historical_average = mean(historical_prices)

            deal_score = calculate_serper_deal_score(
                price=offer.price,
                min_price=batch_min_price,
                max_price=batch_max_price,
                rating=offer.rating,
                rating_count=offer.rating_count,
                discount_percent=discount,
                historical_average=historical_average,
            )

            # Agora registra a observação atual
            save_price_snapshot(
                external_id=offer.external_id,
                title=offer.title,
                price=offer.price,
                original_price=offer.original_price,
                permalink=offer.link,
                category_id="serper_shopping",
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
                    "historical_average": (
                        round(historical_average, 2)
                        if historical_average is not None
                        else None
                    ),
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