from app.providers.base import ProductSearchProvider
from app.providers.demo_provider import DemoProvider
from app.providers.mercado_livre_provider import MercadoLivreProvider


class UnknownProviderError(ValueError):
    pass


_PROVIDERS: dict[str, ProductSearchProvider] = {
    "demo": DemoProvider(),
    "mercado_livre": MercadoLivreProvider(),
}


def list_providers() -> list[dict]:
    return [
        provider.status()
        for provider in _PROVIDERS.values()
    ]


def get_provider(name: str) -> ProductSearchProvider:
    try:
        return _PROVIDERS[name]
    except KeyError as exc:
        raise UnknownProviderError(
            f"Unknown product provider: {name}"
        ) from exc


def search_offers(
    source: str,
    query: str,
    max_price: float | None = None,
    limit: int = 20,
) -> list[dict]:
    provider = get_provider(source)

    return provider.search_offers(
        query=query,
        max_price=max_price,
        limit=limit,
    )
