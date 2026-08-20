"""Struggle prediction inference service for EduSense AI."""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db.models import User, Topic, QuizAttempt, LearningEvent

from ml.models.pytorch_struggle_nn import PyTorchStrugglePredictor

MODELS_DIR = os.path.join("ml", "models")
ARTIFACTS_DIR = os.path.join("ml", "artifacts")
MODEL_PATH = os.path.join(MODELS_DIR, "struggle_model_rf_v1.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler_v1.pkl")
METRICS_PATH = os.path.join(MODELS_DIR, "model_metrics.json")
COMPARISON_PATH = os.path.join(ARTIFACTS_DIR, "model_comparison.json")
FEATURES_PATH = os.path.join(MODELS_DIR, "feature_names.json")
PYTORCH_MODEL_PATH = os.path.join(ARTIFACTS_DIR, "struggle_model_nn_v1.pt")
PYTORCH_SCALER_PATH = os.path.join(ARTIFACTS_DIR, "pytorch_scaler.joblib")

FEATURE_COLS = [
    "recent_quiz_score",
    "historical_topic_score",
    "attempts_count",
    "total_time_spent",
    "prerequisite_completion_rate",
    "score_trend",
    "engagement_frequency",
    "topic_difficulty_numeric",
]


class StrugglePredictionService:
    """Service handling model artifact loading and struggle predictions."""

    def __init__(self):
        self.model = None
        self.scaler = None
        self.pytorch_predictor = None
        self.feature_names = FEATURE_COLS
        self.metadata = {}
        self._load_artifacts()

    def _load_artifacts(self):
        """Load saved Random Forest model, scaler, and PyTorch NN artifacts."""
        try:
            if os.path.exists(MODEL_PATH):
                self.model = joblib.load(MODEL_PATH)
                logger.info(f"Loaded ML struggle prediction model from {MODEL_PATH}")
            if os.path.exists(SCALER_PATH):
                self.scaler = joblib.load(SCALER_PATH)
            if os.path.exists(METRICS_PATH):
                with open(METRICS_PATH, "r") as f:
                    self.metadata = json.load(f)
            if os.path.exists(PYTORCH_MODEL_PATH) and os.path.exists(PYTORCH_SCALER_PATH):
                self.pytorch_predictor = PyTorchStrugglePredictor(PYTORCH_MODEL_PATH, PYTORCH_SCALER_PATH)
                logger.info("Loaded PyTorch StruggleNN predictor artifact")
        except Exception as e:
            logger.error(f"Error loading model artifacts: {e}")

    def get_model_metadata(self) -> Dict[str, Any]:
        """Return model metadata, metrics, and PyTorch benchmarks."""
        if not self.metadata and os.path.exists(METRICS_PATH):
            with open(METRICS_PATH, "r") as f:
                self.metadata = json.load(f)

        if os.path.exists(COMPARISON_PATH):
            try:
                with open(COMPARISON_PATH, "r") as f:
                    comp_data = json.load(f)
                    if "pytorch_nn" in comp_data:
                        self.metadata["pytorch_nn"] = comp_data["pytorch_nn"]
            except Exception:
                pass
        return self.metadata

    def predict_from_features(
        self,
        recent_quiz_score: float,
        historical_topic_score: float,
        attempts_count: int,
        total_time_spent: int,
        prerequisite_completion_rate: float,
        score_trend: float,
        engagement_frequency: int,
        topic_difficulty_numeric: int,
        model_type: str = "random_forest",
    ) -> Dict[str, Any]:
        """Predict struggle probability from raw feature values using specified model."""
        features = [
            recent_quiz_score,
            historical_topic_score,
            attempts_count,
            total_time_spent,
            prerequisite_completion_rate,
            score_trend,
            engagement_frequency,
            topic_difficulty_numeric,
        ]

        if model_type == "pytorch_nn" and self.pytorch_predictor is not None:
            feature_arr = np.array(features)
            prob = float(self.pytorch_predictor.predict_proba(feature_arr)[0, 1])
            model_ver = "pytorch_nn_v1.0"
        else:
            if self.model is None:
                self._load_artifacts()
                if self.model is None:
                    return self._fallback_rule_based_prediction(
                        recent_quiz_score, prerequisite_completion_rate, topic_difficulty_numeric
                    )
            X_input = pd.DataFrame([features], columns=self.feature_names)
            prob = float(self.model.predict_proba(X_input)[0, 1])
            model_ver = self.metadata.get("version", "v1.0.0")

        prob = max(0.0, min(1.0, round(prob, 4)))

        is_struggling = prob >= 0.50

        if prob >= 0.70:
            risk_level = "high"
        elif prob >= 0.40:
            risk_level = "moderate"
        else:
            risk_level = "low"

        # Identify key risk factors
        risk_factors = []
        if recent_quiz_score < 70:
            risk_factors.append(f"Low recent quiz score ({recent_quiz_score:.1f}%)")
        if prerequisite_completion_rate < 0.70:
            risk_factors.append(f"Incomplete prerequisites ({prerequisite_completion_rate * 100:.0f}% mastered)")
        if topic_difficulty_numeric == 3:
            risk_factors.append("High topic difficulty level")
        if attempts_count >= 3:
            risk_factors.append(f"Multiple previous attempts ({attempts_count})")
        if score_trend < -5.0:
            risk_factors.append(f"Negative performance trend ({score_trend:.1f} pts)")
        if engagement_frequency < 3:
            risk_factors.append("Low study engagement in last 14 days")

        return {
            "struggle_probability": prob,
            "is_struggling": is_struggling,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "features_used": dict(zip(self.feature_names, features)),
            "model_version": model_ver,
        }

    def predict_from_db(
        self,
        db: Session,
        student_id: int,
        topic_id: int,
        model_type: str = "random_forest",
    ) -> Dict[str, Any]:
        """Dynamically extract student & topic features from DB and predict struggle."""
        user = db.query(User).filter(User.id == student_id).first()
        topic = db.query(Topic).filter(Topic.id == topic_id).first()

        if not user:
            raise ValueError(f"Student ID {student_id} not found in database.")
        if not topic:
            raise ValueError(f"Topic ID {topic_id} not found in database.")

        # Compute historical features for student from DB
        past_attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).all()
        target_attempts = [a for a in past_attempts if a.topic_id == topic_id]

        if past_attempts:
            past_scores = [a.score for a in past_attempts]
            recent_quiz_score = float(np.mean(past_scores[-3:]))
            historical_topic_score = float(np.mean(past_scores))
        else:
            recent_quiz_score = 75.0
            historical_topic_score = 75.0

        attempts_count = len(target_attempts) + 1
        total_time_spent = sum([a.time_spent for a in target_attempts]) + 120

        # Prerequisites completion
        prereqs = topic.prerequisites or []
        if isinstance(prereqs, str):
            try:
                prereqs = json.loads(prereqs)
            except Exception:
                prereqs = []

        if not isinstance(prereqs, list) or len(prereqs) == 0:
            prereq_completion_rate = 1.0
        else:
            prereq_mastered = 0
            for p_id in prereqs:
                p_attempts = [a for a in past_attempts if a.topic_id == p_id]
                if p_attempts and max([a.score for a in p_attempts]) >= 70:
                    prereq_mastered += 1
            prereq_completion_rate = prereq_mastered / len(prereqs)

        score_trend = recent_quiz_score - historical_topic_score

        # Engagement events
        events_count = db.query(LearningEvent).filter(LearningEvent.student_id == student_id).count()

        diff_map = {"easy": 1, "medium": 2, "hard": 3}
        topic_difficulty_numeric = diff_map.get(topic.difficulty, 2)

        return self.predict_from_features(
            recent_quiz_score=recent_quiz_score,
            historical_topic_score=historical_topic_score,
            attempts_count=attempts_count,
            total_time_spent=total_time_spent,
            prerequisite_completion_rate=prereq_completion_rate,
            score_trend=score_trend,
            engagement_frequency=events_count,
            topic_difficulty_numeric=topic_difficulty_numeric,
            model_type=model_type,
        )

    def _fallback_rule_based_prediction(self, score, prereq, diff) -> Dict[str, Any]:
        """Fallback rule-based prediction if model is not loaded."""
        prob = 0.50
        if score < 70:
            prob += 0.25
        if prereq < 0.70:
            prob += 0.15
        if diff == 3:
            prob += 0.10

        prob = min(0.95, prob)
        return {
            "struggle_probability": prob,
            "is_struggling": prob >= 0.50,
            "risk_level": "high" if prob >= 0.70 else "moderate",
            "risk_factors": ["Rule-based fallback prediction"],
            "model_version": "fallback_v0.1",
        }


prediction_service = StrugglePredictionService()
