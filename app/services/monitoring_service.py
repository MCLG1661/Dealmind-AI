from statistics import mean
from app.repositories.alert_repository import deactivate_alert, get_active_alerts_for_product
from app.repositories.offer_repository import get_price_history, save_price_snapshot

def calculate_deal_score(current_price: float, average_price: float, minimum_price: float) -> float:
    if average_price <= 0:
        return 50.0
    discount_vs_average = max(0.0, (average_price - current_price) / average_price)
    minimum_bonus = 20.0 if current_price <= minimum_price else max(0.0, 20.0 * (minimum_price / current_price))
    return round(min(50.0 + discount_vs_average * 150.0 + minimum_bonus, 100.0), 1)

def build_price_analysis(product_id: str) -> dict:
    history = get_price_history(product_id)
    if not history:
        return {"product_id": product_id, "observations": 0, "message": "No price history available."}
    prices = [float(item["price"]) for item in history]
    current, average, minimum, maximum = prices[-1], mean(prices), min(prices), max(prices)
    variation = ((current - average) / average) * 100 if average > 0 else 0.0
    score = calculate_deal_score(current, average, minimum)
    opportunity = "excellent" if score >= 85 else "good" if score >= 70 else "fair" if score >= 55 else "weak"
    latest = history[-1]
    return {
        "product_id": product_id, "title": latest["title"], "url": latest["permalink"],
        "observations": len(history), "current_price": round(current, 2),
        "average_price": round(average, 2), "minimum_price": round(minimum, 2),
        "maximum_price": round(maximum, 2), "variation_vs_average_percent": round(variation, 2),
        "deal_score": score, "opportunity": opportunity, "last_captured_at": latest["captured_at"],
    }

def evaluate_price_alerts(product_id: str, current_price: float) -> list[dict]:
    triggered = []
    for alert in get_active_alerts_for_product(product_id):
        target = float(alert["target_price"])
        if current_price <= target:
            triggered.append({
                "alert_id": alert["id"], "product_id": product_id,
                "target_price": target, "current_price": current_price,
                "contact": alert["contact"], "triggered": True,
            })
            deactivate_alert(alert["id"])
    return triggered

def record_product_snapshot(product_id: str, title: str, price: float, url: str,
                            original_price: float | None = None,
                            category_id: str | None = None) -> dict:
    snapshot = save_price_snapshot(product_id, title, price, original_price, url, category_id)
    return {
        "snapshot": snapshot,
        "analysis": build_price_analysis(product_id),
        "triggered_alerts": evaluate_price_alerts(product_id, price),
    }
