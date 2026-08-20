"""PyTorch Deep Learning Model Training Pipeline for EduSense AI."""

import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from ml.models.pytorch_struggle_nn import StruggleNN

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


def train_pytorch_model():
    """Train PyTorch MLP neural network on prepared CSV dataset and save artifacts."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data", "processed")
    artifacts_dir = os.path.join(base_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    print("--- Loading Prepared Feature Datasets ---")
    train_df = pd.read_csv(os.path.join(data_dir, "train_features.csv"))
    test_df = pd.read_csv(os.path.join(data_dir, "test_features.csv"))

    X_train = train_df[FEATURE_COLS]
    y_train = train_df[TARGET_COL].values
    X_test = test_df[FEATURE_COLS]
    y_test = test_df[TARGET_COL].values

    # Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Save Scaler
    scaler_path = os.path.join(artifacts_dir, "pytorch_scaler.joblib")
    joblib.dump(scaler, scaler_path)
    print(f"Saved PyTorch StandardScaler to {scaler_path}")

    # Convert to Tensors
    X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32)
    y_test_tensor = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

    # PyTorch DataLoader
    dataset = TensorDataset(X_train_tensor, y_train_tensor)
    loader = DataLoader(dataset, batch_size=64, shuffle=True)

    # Initialize Network, Loss, Optimizer
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = StruggleNN(input_dim=len(FEATURE_COLS)).to(device)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)

    print(f"--- Training PyTorch StruggleNN on {device} (25 Epochs) ---")
    epochs = 25
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for batch_x, batch_y in loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * batch_x.size(0)

        epoch_loss = running_loss / len(dataset)
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"Epoch [{epoch+1}/{epochs}] Loss: {epoch_loss:.4f}")

    # Save Model Weights
    model_path = os.path.join(artifacts_dir, "struggle_model_nn_v1.pt")
    torch.save(model.state_dict(), model_path)
    print(f"Saved PyTorch model weights to {model_path}")

    # Evaluation on Test Set
    model.eval()
    with torch.no_grad():
        test_preds_tensor = model(X_test_tensor.to(device)).cpu()
        test_probs = test_preds_tensor.numpy().flatten()
        test_preds = (test_probs >= 0.5).astype(int)

    acc = float(accuracy_score(y_test, test_preds))
    prec = float(precision_score(y_test, test_preds, zero_division=0))
    rec = float(recall_score(y_test, test_preds, zero_division=0))
    f1 = float(f1_score(y_test, test_preds, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, test_probs))

    print("\n--- PyTorch Deep Learning Model Test Performance ---")
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")

    # Load existing classical benchmarks if available
    metrics_path = os.path.join(artifacts_dir, "model_metrics.json")
    comparison = {
        "pytorch_nn": {
            "model_name": "PyTorch Deep Learning MLP",
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
        }
    }

    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, "r") as f:
                classical_metrics = json.load(f)
                comparison.update(classical_metrics)
        except Exception as e:
            print(f"Could not load classical metrics: {e}")

    comp_path = os.path.join(artifacts_dir, "model_comparison.json")
    with open(comp_path, "w") as f:
        json.dump(comparison, f, indent=2)
    print(f"Saved model comparison benchmarks to {comp_path}")

    return comparison


if __name__ == "__main__":
    train_pytorch_model()
