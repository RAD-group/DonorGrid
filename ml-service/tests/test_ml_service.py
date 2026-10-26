"""Checks of the ML service. Run from ml-service/: python -m pytest tests"""
import os
import sys
import warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.pop("HF_API_KEY", None)  # the chat must work without a key, using the fallback

with warnings.catch_warnings():
    warnings.simplefilter("error", UserWarning)  # fail if the saved models need another scikit-learn version
    import main

from fastapi.testclient import TestClient

client = TestClient(main.app)


def test_health():
    assert client.get("/health").json() == {"status": "healthy", "models_loaded": True}


def test_predict_donor():
    r = client.post("/predict-donor", json={"age": 30, "total_donations": 4, "days_since_last": 120,
                                             "blood_group": "O+", "city": "Chennai"})
    assert r.status_code == 200
    assert 0 <= r.json()["probability"] <= 1


def test_predict_stock():
    r = client.post("/predict-stock", json={"current_units": 40, "daily_usage": 6, "camps_this_month": 2,
                                             "season": "Summer"})
    assert r.status_code == 200
    assert r.json()["alert_level"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def test_recommend_location():
    r = client.post("/recommend-location", json={"lat": 13.08, "lon": 80.27})
    assert r.status_code == 200


def test_bad_input_is_rejected():
    assert client.post("/predict-donor", json={"age": "old"}).status_code == 422


def test_chat_falls_back_without_a_key():
    r = client.post("/chat", json={"message": "who is the universal donor?"})
    assert r.json()["source"] == "smart-fallback"


def test_no_key_in_the_code():
    source = open(os.path.join(os.path.dirname(main.__file__), "main.py")).read()
    assert "hf_" + "ePGJ" not in source and main.HF_KEY == ""


def test_cors_refuses_other_sites():
    r = client.options("/chat", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    assert r.headers.get("access-control-allow-origin") is None
