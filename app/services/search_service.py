import json
from pathlib import Path
import unicodedata

from app.models.product import Product


DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "products.json"


def _normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return value.lower().strip()


def load_products() -> list[Product]:
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return [Product(**item) for item in raw]


def search_products(query: str, max_price: float | None = None) -> list[Product]:
    terms = [term for term in _normalize_text(query).split() if term]
    products = load_products()

    def matches(product: Product) -> bool:
        haystack = _normalize_text(
            f"{product.name} {product.category} {product.store}"
        )
        return all(term in haystack for term in terms)

    result = [p for p in products if matches(p)]

    if max_price is not None:
        result = [p for p in result if p.price <= max_price]

    return sorted(result, key=lambda p: (p.price, -p.discount_percent))
