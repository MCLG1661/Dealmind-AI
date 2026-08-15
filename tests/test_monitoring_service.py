from app.services.monitoring_service import calculate_deal_score

def test_deal_score_is_high_at_historical_minimum():
    assert calculate_deal_score(80.0, 100.0, 80.0) >= 85

def test_deal_score_never_exceeds_100():
    assert calculate_deal_score(50.0, 100.0, 50.0) <= 100
