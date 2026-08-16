from __future__ import annotations

from app.services.monitoring_service import build_price_analysis


def _confidence_from_observations(observations: int) -> str:
    if observations >= 10:
        return "high"
    if observations >= 5:
        return "medium"
    return "low"


def _recommendation_from_score(score: float) -> str:
    if score >= 85:
        return "buy"
    if score >= 70:
        return "consider_buying"
    if score >= 55:
        return "monitor"
    return "wait"


def _recommendation_label(value: str) -> str:
    labels = {
        "buy": "COMPRAR",
        "consider_buying": "CONSIDERAR COMPRA",
        "monitor": "ACOMPANHAR",
        "wait": "AGUARDAR",
    }
    return labels[value]


def build_advisor_response(product_id: str) -> dict:
    analysis = build_price_analysis(product_id)

    if analysis.get("observations", 0) == 0:
        return {
            "product_id": product_id,
            "available": False,
            "message": "No price history available for advisor analysis.",
        }

    current_price = float(analysis["current_price"])
    average_price = float(analysis["average_price"])
    minimum_price = float(analysis["minimum_price"])
    maximum_price = float(analysis["maximum_price"])
    variation = float(analysis["variation_vs_average_percent"])
    deal_score = float(analysis["deal_score"])
    observations = int(analysis["observations"])

    recommendation = _recommendation_from_score(deal_score)
    confidence = _confidence_from_observations(observations)

    reasons = []

    if variation < 0:
        reasons.append(
            f"Current price is {abs(variation):.2f}% below the observed average."
        )
    elif variation > 0:
        reasons.append(
            f"Current price is {variation:.2f}% above the observed average."
        )
    else:
        reasons.append("Current price is equal to the observed average.")

    if current_price <= minimum_price:
        reasons.append("Current price is at the lowest observed level.")
    elif minimum_price > 0:
        distance_from_minimum = (
            (current_price - minimum_price) / minimum_price
        ) * 100
        reasons.append(
            f"Current price is {distance_from_minimum:.2f}% above "
            "the historical minimum."
        )

    reasons.append(
        f"Deal Score is {deal_score:.1f}/100, classified as "
        f"{analysis['opportunity']}."
    )

    if observations < 5:
        reasons.append(
            "The recommendation is based on a limited price history, "
            "so confidence is still low."
        )

    summary = (
        f"{_recommendation_label(recommendation)} — "
        f"current price R$ {current_price:.2f}, "
        f"average R$ {average_price:.2f}, "
        f"Deal Score {deal_score:.1f}/100."
    )

    return {
        "product_id": product_id,
        "title": analysis["title"],
        "available": True,
        "recommendation": recommendation,
        "recommendation_label": _recommendation_label(recommendation),
        "confidence": confidence,
        "summary": summary,
        "reasons": reasons,
        "metrics": {
            "current_price": current_price,
            "average_price": average_price,
            "minimum_price": minimum_price,
            "maximum_price": maximum_price,
            "variation_vs_average_percent": variation,
            "deal_score": deal_score,
            "opportunity": analysis["opportunity"],
            "observations": observations,
        },
        "disclaimer": (
            "Recommendation is based only on the price history available "
            "inside DealMind AI."
        ),
    }
