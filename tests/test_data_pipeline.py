"""Unit tests for synthetic dataset generation, feature pipeline, and train/val/test splitting."""

import os
import pandas as pd
import pytest
from ml.features.feature_pipeline import build_feature_matrix, split_data_by_student

RAW_DIR = os.path.join("ml", "data", "raw")
PROCESSED_DIR = os.path.join("ml", "data", "processed")


def test_raw_files_exist_and_non_empty():
    """Verify that raw CSV files exist and have data."""
    raw_files = [
        "raw_students.csv",
        "raw_topics.csv",
        "raw_quiz_attempts.csv",
        "raw_learning_events.csv",
        "raw_feedback.csv",
    ]
    for filename in raw_files:
        filepath = os.path.join(RAW_DIR, filename)
        assert os.path.exists(filepath), f"File {filename} does not exist!"
        df = pd.read_csv(filepath)
        assert len(df) > 0, f"File {filename} is empty!"


def test_feature_matrix_generation():
    """Test feature matrix building logic."""
    processed_path = os.path.join(PROCESSED_DIR, "feature_matrix_all.csv")
    if os.path.exists(processed_path):
        features_df = pd.read_csv(processed_path)
    else:
        features_df = build_feature_matrix()

    required_columns = [
        "attempt_id",
        "student_id",
        "topic_id",
        "quiz_score",
        "recent_quiz_score",
        "historical_topic_score",
        "attempts_count",
        "total_time_spent",
        "prerequisite_completion_rate",
        "score_trend",
        "engagement_frequency",
        "topic_difficulty_numeric",
        "target_struggling",
    ]

    for col in required_columns:
        assert col in features_df.columns, f"Missing feature column: {col}"

    # Check value bounds
    assert features_df["target_struggling"].isin([0, 1]).all()
    assert (features_df["prerequisite_completion_rate"] >= 0.0).all()
    assert (features_df["prerequisite_completion_rate"] <= 1.0).all()
    assert (features_df["topic_difficulty_numeric"].isin([1, 2, 3])).all()


def test_train_val_test_split_no_leakage():
    """Verify student-stratified split prevents student ID leakage across splits."""
    features_path = os.path.join(PROCESSED_DIR, "feature_matrix_all.csv")
    if not os.path.exists(features_path):
        features_df = build_feature_matrix()
    else:
        features_df = pd.read_csv(features_path)

    train_df, val_df, test_df = split_data_by_student(features_df)

    train_students = set(train_df["student_id"].unique())
    val_students = set(val_df["student_id"].unique())
    test_students = set(test_df["student_id"].unique())

    # Check zero overlap across sets
    assert len(train_students.intersection(val_students)) == 0, "Train and Val student overlap!"
    assert len(train_students.intersection(test_students)) == 0, "Train and Test student overlap!"
    assert len(val_students.intersection(test_students)) == 0, "Val and Test student overlap!"

    # Check total student count matches
    total_split_students = len(train_students) + len(val_students) + len(test_students)
    assert total_split_students == features_df["student_id"].nunique()
