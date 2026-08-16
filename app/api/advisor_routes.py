from fastapi import APIRouter, HTTPException

from app.services.advisor_service import build_advisor_response


router = APIRouter(
    prefix="/advisor",
    tags=["Advisor"],
)


@router.get("/{product_id}")
def advisor(product_id: str) -> dict:
    result = build_advisor_response(product_id)

    if not result.get("available"):
        raise HTTPException(
            status_code=404,
            detail=result.get(
                "message",
                "No advisor analysis available for this product.",
            ),
        )

    return result