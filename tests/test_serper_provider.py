from app.providers.serper_provider import (
    calculate_serper_deal_score,
)


def test_cheaper_high_rated_offer_scores_better():
    strong_offer = calculate_serper_deal_score(
        price=200.0,
        min_price=200.0,
        max_price=500.0,
        rating=4.8,
        rating_count=300,
    )

    weak_offer = calculate_serper_deal_score(
        price=500.0,
        min_price=200.0,
        max_price=500.0,
        rating=None,
        rating_count=None,
    )

    assert strong_offer > weak_offer


def test_history_below_average_increases_score():
    without_history = calculate_serper_deal_score(
        price=250.0,
        min_price=200.0,
        max_price=500.0,
    )

    with_history = calculate_serper_deal_score(
        price=250.0,
        min_price=200.0,
        max_price=500.0,
        historical_average=300.0,
    )

    assert with_history > without_history