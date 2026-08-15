from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    category: str
    store: str
    price: float
    original_price: float
    url: str
    rating: float | None = None

    @property
    def discount_percent(self) -> float:
        if self.original_price <= 0 or self.original_price <= self.price:
            return 0.0
        return round((1 - self.price / self.original_price) * 100, 1)
