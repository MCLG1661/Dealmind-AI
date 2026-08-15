import os
import requests

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.database.db import init_db
from app.providers.mercado_livre_provider import MercadoLivreProviderError
from app.repositories.alert_repository import create_alert, list_alerts
from app.repositories.offer_repository import get_price_history
from app.services.provider_service import (
    UnknownProviderError,
    list_providers,
    search_offers,
)
from app.services.token_store import save_tokens, token_status


app = FastAPI(
    title="DealMind AI API",
    description="Copilot de ofertas para corrida e fitness.",
    version="0.3.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


class AlertCreate(BaseModel):
    product_id: str = Field(min_length=1)
    target_price: float = Field(gt=0)
    contact: str | None = None


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "dealmind-ai",
        "version": "0.3.0",
    }


@app.get("/auth/status")
def auth_status() -> dict:
    return token_status()


@app.get("/providers")
def providers() -> dict:
    return {
        "count": len(list_providers()),
        "providers": list_providers(),
    }


@app.get("/products/search")
def products_search(
    q: str = Query(min_length=1),
    max_price: float | None = Query(default=None, gt=0),
    source: str = Query(default="demo"),
    limit: int = Query(default=20, ge=1, le=50),
) -> dict:
    try:
        products = search_offers(
            source=source,
            query=q,
            max_price=max_price,
            limit=limit,
        )
    except MercadoLivreProviderError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except UnknownProviderError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Provider integration failed: {exc}",
        ) from exc

    return {
        "query": q,
        "max_price": max_price,
        "source": source,
        "count": len(products),
        "products": products,
    }


@app.get("/products/{product_id}/history")
def product_history(product_id: str) -> dict:
    history = get_price_history(product_id)

    return {
        "product_id": product_id,
        "count": len(history),
        "history": history,
    }


@app.post("/alerts", status_code=201)
def alerts_create(payload: AlertCreate) -> dict:
    return create_alert(
        product_id=payload.product_id,
        target_price=payload.target_price,
        contact=payload.contact,
    )


@app.get("/alerts")
def alerts_list() -> list[dict]:
    return list_alerts()


@app.get("/callback/mercadolivre")
def mercado_livre_callback(
    code: str | None = None,
    error: str | None = None,
) -> dict:
    if error:
        return {
            "success": False,
            "error": error,
            "message": "Mercado Livre authorization failed.",
        }

    if not code:
        return {
            "success": False,
            "message": "Authorization code was not provided.",
        }

    client_id = os.getenv("MELI_CLIENT_ID")
    client_secret = os.getenv("MELI_CLIENT_SECRET")
    redirect_uri = os.getenv("MELI_REDIRECT_URI")

    if not client_id or not client_secret or not redirect_uri:
        return {
            "success": False,
            "message": "OAuth environment variables are not configured.",
        }

    payload = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
    }

    try:
        response = requests.post(
            "https://api.mercadolibre.com/oauth/token",
            data=payload,
            timeout=15,
        )
        response.raise_for_status()
        token_data = response.json()

        access_token = token_data.get("access_token")

        if not access_token:
            return {
                "success": False,
                "message": "OAuth response did not include an access token.",
            }

        save_tokens(
            access_token=access_token,
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in"),
        )

        return {
            "success": True,
            "message": "Mercado Livre OAuth completed successfully.",
            "access_token_received": True,
            "refresh_token_received": bool(token_data.get("refresh_token")),
            "expires_in": token_data.get("expires_in"),
            "user_id": token_data.get("user_id"),
        }

    except requests.RequestException as exc:
        return {
            "success": False,
            "message": "Failed to exchange authorization code for token.",
            "error": str(exc),
        }
