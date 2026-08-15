from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl
from app.repositories.offer_repository import get_price_history
from app.services.monitoring_service import build_price_analysis, record_product_snapshot

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])

class ProductSnapshotCreate(BaseModel):
    product_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    price: float = Field(gt=0)
    url: HttpUrl
    original_price: float | None = Field(default=None, gt=0)
    category_id: str | None = None

@router.post("/snapshots", status_code=201)
def create_snapshot(payload: ProductSnapshotCreate) -> dict:
    return record_product_snapshot(
        payload.product_id, payload.title, payload.price, str(payload.url),
        payload.original_price, payload.category_id
    )

@router.get("/{product_id}")
def monitoring_analysis(product_id: str) -> dict:
    analysis = build_price_analysis(product_id)
    if analysis.get("observations") == 0:
        raise HTTPException(status_code=404, detail="No monitoring data found for this product.")
    return analysis

@router.get("/{product_id}/history")
def monitoring_history(product_id: str) -> dict:
    history = get_price_history(product_id)
    return {"product_id": product_id, "count": len(history), "history": history}
