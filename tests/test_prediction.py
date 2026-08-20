"""Unit and API integration tests for ML prediction functionality."""

import pytest
from app.services.prediction_service import prediction_service
from app.db.models import User, Topic, QuizAttempt


def test_prediction_from_features():
    """Test struggle prediction service with explicit features."""
    result = prediction_service.predict_from_features(
        recent_quiz_score=55.0,
        historical_topic_score=60.0,
        attempts_count=3,
        total_time_spent=450,
        prerequisite_completion_rate=0.33,
        score_trend=-5.0,
        engagement_frequency=2,
        topic_difficulty_numeric=3,
    )

    assert "struggle_probability" in result
    assert 0.0 <= result["struggle_probability"] <= 1.0
    assert result["is_struggling"] is True
    assert result["risk_level"] in ["moderate", "high"]
    assert len(result["risk_factors"]) > 0


def test_predict_struggle_api_with_features(client):
    """Test POST /predict/struggle API endpoint with raw features."""
    payload = {
        "recent_quiz_score": 88.0,
        "historical_topic_score": 90.0,
        "attempts_count": 1,
        "total_time_spent": 120,
        "prerequisite_completion_rate": 1.0,
        "score_trend": 2.0,
        "engagement_frequency": 10,
        "topic_difficulty_numeric": 1,
    }

    response = client.post("/predict/struggle", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "struggle_probability" in data
    assert data["is_struggling"] is False
    assert data["risk_level"] == "low"


from datetime import datetime


def test_predict_struggle_api_with_db(client, db_session):
    """Test POST /predict/struggle API endpoint querying DB records."""
    user = User(id=101, name="Test Learner", email="testlearner@example.com", role="student")
    topic = Topic(id=50, subject="Machine Learning", name="Test Neural Nets", difficulty="hard", prerequisites=[])
    db_session.add(user)
    db_session.add(topic)

    attempt = QuizAttempt(
        student_id=101,
        topic_id=50,
        score=50.0,
        time_spent=200,
        attempts=2,
        timestamp=datetime.utcnow(),
    )
    db_session.add(attempt)
    db_session.commit()

    payload = {
        "student_id": 101,
        "topic_id": 50,
    }

    response = client.post("/predict/struggle", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "struggle_probability" in data
    assert "risk_level" in data


def test_get_models_api(client):
    """Test GET /models API endpoint."""
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert "model_name" in data
    assert "metrics_test" in data
    assert "feature_importances" in data
