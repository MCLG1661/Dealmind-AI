from __future__ import annotations

from abc import ABC, abstractmethod


class ProductSearchProvider(ABC):
    name: str

    @abstractmethod
    def search_offers(
        self,
        query: str,
        max_price: float | None = None,
        limit: int = 20,
    ) -> list[dict]:
        raise NotImplementedError

    def status(self) -> dict:
        return {
            "name": self.name,
            "available": True,
        }
