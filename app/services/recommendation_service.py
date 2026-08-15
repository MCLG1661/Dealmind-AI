from app.models.product import Product


def score_product(product: Product, max_price: float | None = None) -> float:
    score = 50.0

    # Quanto maior o desconto, melhor.
    score += min(product.discount_percent, 30)

    # Pequeno bônus para avaliações altas.
    if product.rating is not None:
        score += max(0, product.rating - 4.0) * 10

    # Bônus por folga dentro do orçamento.
    if max_price and max_price > 0 and product.price <= max_price:
        budget_ratio = product.price / max_price
        score += max(0, (1 - budget_ratio) * 20)

    return round(min(score, 100), 1)


def build_recommendation(
    products: list[Product],
    max_price: float | None = None
) -> list[dict]:
    enriched = []

    for product in products:
        enriched.append(
            {
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "store": product.store,
                "price": product.price,
                "original_price": product.original_price,
                "discount_percent": product.discount_percent,
                "rating": product.rating,
                "url": product.url,
                "deal_score": score_product(product, max_price),
            }
        )

    return sorted(
        enriched,
        key=lambda item: (-item["deal_score"], item["price"])
    )
