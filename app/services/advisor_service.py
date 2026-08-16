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


def _format_brl(value: float) -> str:
    formatted = f"{value:,.2f}"
    return (
        formatted
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def build_advisor_response(product_id: str) -> dict:
    analysis = build_price_analysis(product_id)

    if analysis.get("observations", 0) == 0:
        return {
            "product_id": product_id,
            "available": False,
            "message": "Não há histórico de preços disponível para análise.",
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
            f"O preço atual está {abs(variation):.2f}% abaixo da média observada."
        )
    elif variation > 0:
        reasons.append(
            f"O preço atual está {variation:.2f}% acima da média observada."
        )
    else:
        reasons.append(
            "O preço atual está igual à média observada."
        )

    if current_price <= minimum_price:
        reasons.append(
            "O preço atual está no menor nível observado no histórico."
        )
    elif minimum_price > 0:
        distance_from_minimum = (
            (current_price - minimum_price) / minimum_price
        ) * 100

        reasons.append(
            f"O preço atual está {distance_from_minimum:.2f}% acima "
            "do menor preço histórico."
        )

    opportunity_labels = {
        "excellent": "excelente",
        "good": "boa",
        "fair": "regular",
        "weak": "fraca",
    }

    opportunity_label = opportunity_labels.get(
        analysis["opportunity"],
        analysis["opportunity"],
    )

    reasons.append(
        f"O Deal Score é {deal_score:.1f}/100, indicando uma "
        f"oportunidade {opportunity_label}."
    )

    if observations < 5:
        reasons.append(
            "A recomendação é baseada em um histórico de preços ainda limitado, "
            "por isso a confiança da análise permanece baixa."
        )

    current_price_br = _format_brl(current_price)
    average_price_br = _format_brl(average_price)

    summary = (
        f"{_recommendation_label(recommendation)} — "
        f"preço atual R$ {current_price_br}, "
        f"média histórica R$ {average_price_br} e "
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
            "A recomendação é baseada exclusivamente no histórico de preços "
            "disponível no DealMind AI."
        ),
    }