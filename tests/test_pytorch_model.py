"""Unit and API integration tests for PyTorch Deep Learning Struggling Predictor."""

import os
import torch
import numpy as np
import pytest
from ml.models.pytorch_struggle_nn import StruggleNN, PyTorchStrugglePredictor
from app.db.models import User, Topic, QuizAttempt


def test_pytorch_struggle_nn_forward_pass():
    """Test PyTorch StruggleNN neural network forward pass tensor shapes."""
    model = StruggleNN(input_dim=8)
    dummy_input = torch.randn(10, 8)
    output = model(dummy_input)

    assert output.shape == (10, 1)
    assert (output >= 0.0).all() and (output <= 1.0).all()


def test_pytorch_struggle_predictor_inference():
    """Test PyTorchStrugglePredictor inference wrapper loading and probabilities."""
    model_path = os.path.join("ml", "artifacts", "struggle_model_nn_v1.pt")
    scaler_path = os.path.join("ml", "artifacts", "pytorch_scaler.joblib")

    assert os.path.exists(model_path), "PyTorch model weights not found."
    assert os.path.exists(scaler_path), "PyTorch scaler artifact not found."

    predictor = PyTorchStrugglePredictor(model_path, scaler_path)
    sample_features = np.array([55.0, 60.0, 3, 450, 0.33, -5.0, 2, 3])

    probs = predictor.predict_proba(sample_features)
    assert probs.shape == (1, 2)
    assert round(float(probs[0, 0] + probs[0, 1]), 2) == 1.0

    label = predictor.predict(sample_features)
    assert label[0] in (0, 1)


def test_post_predict_struggle_pytorch_nn_api(client, db_session):
    """Test POST /predict/struggle API endpoint with model_type='pytorch_nn'."""
    payload = {
        "recent_quiz_score": 45.0,
        "historical_topic_score": 50.0,
        "attempts_count": 4,
        "total_time_spent": 600,
        "prerequisite_completion_rate": 0.25,
        "score_trend": -10.0,
        "engagement_frequency": 2,
        "topic_difficulty_numeric": 3,
        "model_type": "pytorch_nn",
    }

    response = client.post("/predict/struggle", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "struggle_probability" in data
    assert "is_struggling" in data
    assert "risk_level" in data
    assert data["model_version"] == "pytorch_nn_v1.0"
