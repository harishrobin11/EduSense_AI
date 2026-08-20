"""PyTorch Deep Learning Multi-Layer Perceptron (MLP) for Student Struggle Prediction."""

import os
import torch
import torch.nn as nn
import numpy as np
import joblib
from typing import Dict, Any, Tuple


class StruggleNN(nn.Module):
    """Deep Multi-Layer Perceptron Neural Network for predicting student struggle probability."""

    def __init__(self, input_dim: int = 8):
        super(StruggleNN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


class PyTorchStrugglePredictor:
    """Inference wrapper handling scaling, tensor conversion, and neural network prediction."""

    def __init__(self, model_path: str, scaler_path: str):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model: StruggleNN = None
        self.scaler = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._load_artifacts()

    def _load_artifacts(self):
        """Load PyTorch weights and StandardScaler joblib artifact."""
        if os.path.exists(self.scaler_path):
            self.scaler = joblib.load(self.scaler_path)

        self.model = StruggleNN(input_dim=8).to(self.device)
        if os.path.exists(self.model_path):
            state_dict = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.eval()

    def predict_proba(self, feature_array: np.ndarray) -> np.ndarray:
        """
        Accept numpy array of shape (N, 7) or (7,), preprocess with scaler,
        run PyTorch forward pass, and return probability array of shape (N, 2)
        [p_not_struggling, p_struggling] for compatibility with scikit-learn API.
        """
        if feature_array.ndim == 1:
            feature_array = feature_array.reshape(1, -1)

        if self.scaler is not None:
            scaled_features = self.scaler.transform(feature_array)
        else:
            scaled_features = feature_array

        tensor_x = torch.tensor(scaled_features, dtype=torch.float32).to(self.device)

        self.model.eval()
        with torch.no_grad():
            outputs = self.model(tensor_x).cpu().numpy().flatten()

        # Build (N, 2) array [1-p, p]
        probs = np.column_stack((1.0 - outputs, outputs))
        return probs

    def predict(self, feature_array: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Predict binary classification label (0 or 1)."""
        probs = self.predict_proba(feature_array)
        return (probs[:, 1] >= threshold).astype(int)
