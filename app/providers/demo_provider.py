from app.providers.base import ProductSearchProvider
from app.services.recommendation_service import build_recommendation
from app.services.search_service import search_products


class DemoProvider(ProductSearchProvider):
    name = "demo"

    def search_offers(
        self,
        query: str,
        max_price: float | None = None,
        limit: int = 20,
    ) -> list[dict]:
        products = search_products(
            query,
            max_price=max_price,
        )

        recommendations = build_recommendation(
            products,
            max_price=max_price,
        )

        return recommendations[:limit]
