from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.database.db import init_db
from app.repositories.alert_repository import create_alert, list_alerts
from app.repositories.offer_repository import get_price_history
from app.services.marketplace_service import MarketplaceNotConfigured, search_marketplace
from app.services.search_service import search_products
from app.services.recommendation_service import build_recommendation

app = FastAPI(
    title="DealMind AI API",
    description="Copilot de ofertas para corrida e fitness.",
    version="0.2.0",
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
    return {"status": "ok", "service": "dealmind-ai", "version": "0.2.0"}

@app.get("/products/search")
def products_search(
    q: str = Query(min_length=1),
    max_price: float | None = Query(default=None, gt=0),
    source: str = Query(default="demo", pattern="^(demo|mercado_livre)$"),
    limit: int = Query(default=20, ge=1, le=50),
) -> dict:
    if source == "demo":
        products = search_products(q, max_price=max_price)
        recommendations = build_recommendation(products, max_price=max_price)
    else:
        try:
            recommendations = search_marketplace(q, max_price=max_price, limit=limit)
        except MarketplaceNotConfigured as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Marketplace integration failed: {exc}") from exc

    return {
        "query": q,
        "max_price": max_price,
        "source": source,
        "count": len(recommendations),
        "products": recommendations,
    }

@app.get("/products/{product_id}/history")
def product_history(product_id: str) -> dict:
    history = get_price_history(product_id)
    return {"product_id": product_id, "count": len(history), "history": history}

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
