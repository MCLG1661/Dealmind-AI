from app.services.provider_service import (
    get_provider,
    list_providers,
)


def test_demo_provider_is_registered():
    provider = get_provider("demo")
    assert provider.name == "demo"


def test_mercado_livre_provider_is_registered():
    provider = get_provider("mercado_livre")
    assert provider.name == "mercado_livre"


def test_list_providers_returns_both_sources():
    providers = list_providers()
    names = {item["name"] for item in providers}

    assert "demo" in names
    assert "mercado_livre" in names
