"""Model training & evaluation script for EduSense AI struggle prediction."""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    brier_score_loss,
)

# Set deterministic random seed
SEED = 42
np.random.seed(SEED)

PROCESSED_DATA_DIR = os.path.join("ml", "data", "processed")
MODELS_DIR = os.path.join("ml", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

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

TARGET_COL = "target_struggling"


def evaluate_model(model, X, y, model_name="Model", scaler=None):
    """Evaluate a trained model and return comprehensive classification metrics."""
    if scaler is not None:
        X_eval = scaler.transform(X)
    else:
        X_eval = X

    y_pred = model.predict(X_eval)
    y_prob = model.predict_proba(X_eval)[:, 1]

    acc = accuracy_score(y, y_pred)
    prec = precision_score(y, y_pred, zero_division=0)
    rec = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y, y_prob)
    brier = brier_score_loss(y, y_prob)
    cm = confusion_matrix(y, y_pred).tolist()

    metrics = {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(roc_auc), 4),
        "brier_score": round(float(brier), 4),
        "confusion_matrix": cm,
    }

    print(f"\n📊 Evaluation Metrics for {model_name}:")
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f} (High recall prioritized)")
    print(f"  F1-Score:  {metrics['f1_score']:.4f}")
    print(f"  ROC-AUC:   {metrics['roc_auc']:.4f}")
    print(f"  Confusion Matrix: TN={cm[0][0]}, FP={cm[0][1]}, FN={cm[1][0]}, TP={cm[1][1]}")

    return metrics


def train_models():
    """Train Logistic Regression and Random Forest models and select top performer."""
    print("🚀 Training EduSense AI Struggle Prediction Models...")

    train_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "train_features.csv"))
    val_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "val_features.csv"))
    test_df = pd.read_csv(os.path.join(PROCESSED_DATA_DIR, "test_features.csv"))

    X_train = train_df[FEATURE_COLS]
    y_train = train_df[TARGET_COL]

    X_val = val_df[FEATURE_COLS]
    y_val = val_df[TARGET_COL]

    X_test = test_df[FEATURE_COLS]
    y_test = test_df[TARGET_COL]

    # 1. Train Baseline Model: Logistic Regression with Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    lr_model = LogisticRegression(random_state=SEED, class_weight="balanced", max_iter=1000)
    lr_model.fit(X_train_scaled, y_train)
    lr_metrics = evaluate_model(lr_model, X_test, y_test, model_name="Baseline Logistic Regression", scaler=scaler)

    # 2. Train Target Model: Random Forest Classifier
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        min_samples_split=5,
        class_weight="balanced",
        random_state=SEED,
    )
    rf_model.fit(X_train, y_train)
    rf_metrics = evaluate_model(rf_model, X_test, y_test, model_name="Random Forest Classifier")

    # Feature Importance analysis for Random Forest
    importances = rf_model.feature_importances_
    feature_importance_dict = {
        feat: round(float(imp), 4)
        for feat, imp in zip(FEATURE_COLS, importances)
    }
    sorted_importances = dict(sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True))

    print("\n💡 Feature Importances (Random Forest):")
    for feat, imp in sorted_importances.items():
        print(f"  - {feat}: {imp:.4f}")

    # Save Random Forest Model & Scaler Artifacts
    rf_path = os.path.join(MODELS_DIR, "struggle_model_rf_v1.pkl")
    scaler_path = os.path.join(MODELS_DIR, "scaler_v1.pkl")
    features_json_path = os.path.join(MODELS_DIR, "feature_names.json")

    joblib.dump(rf_model, rf_path)
    joblib.dump(scaler, scaler_path)

    with open(features_json_path, "w") as f:
        json.dump(FEATURE_COLS, f, indent=2)

    # Combined Metadata Report
    model_metadata = {
        "model_name": "RandomForestClassifier",
        "version": "v1.0.0",
        "trained_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "feature_names": FEATURE_COLS,
        "metrics_test": rf_metrics,
        "metrics_baseline_logistic_regression": lr_metrics,
        "feature_importances": sorted_importances,
    }

    metrics_path = os.path.join(MODELS_DIR, "model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(model_metadata, f, indent=2)

    print(f"\n💾 Model artifacts saved to {MODELS_DIR}/")
    print(f"  - Model: {rf_path}")
    print(f"  - Scaler: {scaler_path}")
    print(f"  - Metrics: {metrics_path}")

    # Record run in DB if possible
    try:
        from app.db.session import SessionLocal
        from app.db.models import ModelRun

        db = SessionLocal()
        run_record = ModelRun(
            model_name="RandomForestClassifier",
            version="v1.0.0",
            metrics=rf_metrics,
            trained_at=datetime.utcnow(),
        )
        db.add(run_record)
        db.commit()
        db.close()
        print(" Recorded ModelRun entry in database.")
    except Exception as e:
        print(f" (Note: DB log skipped or failed: {e})")

    print("\n✅ Sprint 3 ML model training and evaluation completed!")
    return model_metadata


if __name__ == "__main__":
    train_models()
