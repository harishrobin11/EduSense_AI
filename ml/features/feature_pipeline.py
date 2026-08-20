"""Feature engineering pipeline for EduSense AI struggle prediction."""

import os
import ast
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

PROCESSED_DATA_DIR = os.path.join("ml", "data", "processed")
RAW_DATA_DIR = os.path.join("ml", "data", "raw")
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)


def parse_prerequisites(prereq_val):
    """Parse prerequisites list safely."""
    if isinstance(prereq_val, list):
        return prereq_val
    if isinstance(prereq_val, str):
        try:
            return ast.literal_eval(prereq_val)
        except Exception:
            return []
    return []


def build_feature_matrix(raw_dir=RAW_DATA_DIR):
    """Extract features from raw synthetic datasets."""
    students_df = pd.read_csv(os.path.join(raw_dir, "raw_students.csv"))
    topics_df = pd.read_csv(os.path.join(raw_dir, "raw_topics.csv"))
    attempts_df = pd.read_csv(os.path.join(raw_dir, "raw_quiz_attempts.csv"))
    events_df = pd.read_csv(os.path.join(raw_dir, "raw_learning_events.csv"))

    # Convert timestamps
    attempts_df["timestamp"] = pd.to_datetime(attempts_df["timestamp"])
    events_df["timestamp"] = pd.to_datetime(events_df["timestamp"])

    # Map difficulty to numeric
    diff_map = {"easy": 1, "medium": 2, "hard": 3}
    topics_df["topic_difficulty_numeric"] = topics_df["difficulty"].map(diff_map)
    topic_dict = topics_df.set_index("id").to_dict(orient="index")

    # Sort attempts chronologically
    attempts_df = attempts_df.sort_values(by=["student_id", "timestamp"]).reset_index(drop=True)

    feature_rows = []

    for i, row in attempts_df.iterrows():
        student_id = row["student_id"]
        topic_id = row["topic_id"]
        current_time = row["timestamp"]
        score = row["score"]

        # Filter past attempts for this student prior to current timestamp
        past_attempts = attempts_df[
            (attempts_df["student_id"] == student_id) &
            (attempts_df["timestamp"] < current_time)
        ]

        # 1. Recent Quiz Score (average of last 3 past attempts, or 75 default if none)
        if len(past_attempts) > 0:
            recent_quiz_score = past_attempts.tail(3)["score"].mean()
            historical_topic_score = past_attempts["score"].mean()
        else:
            recent_quiz_score = 75.0
            historical_topic_score = 75.0

        # 2. Topic Attempts Count (past attempts on THIS specific topic)
        past_topic_attempts = past_attempts[past_attempts["topic_id"] == topic_id]
        topic_attempts_count = len(past_topic_attempts) + 1

        # 3. Total Time Spent on target topic
        past_topic_time = past_topic_attempts["time_spent"].sum() if len(past_topic_attempts) > 0 else 0
        total_time_spent = past_topic_time + row["time_spent"]

        # 4. Prerequisite Completion Rate
        target_topic_info = topic_dict.get(topic_id, {})
        prereqs = parse_prerequisites(target_topic_info.get("prerequisites", []))

        if len(prereqs) == 0:
            prereq_completion_rate = 1.0
        else:
            prereq_mastered = 0
            for prereq_id in prereqs:
                prereq_attempts = past_attempts[past_attempts["topic_id"] == prereq_id]
                if len(prereq_attempts) > 0 and prereq_attempts["score"].max() >= 70:
                    prereq_mastered += 1
            prereq_completion_rate = prereq_mastered / len(prereqs)

        # 5. Score Trend (difference between recent 3 attempts and overall historical score)
        score_trend = recent_quiz_score - historical_topic_score

        # 6. Engagement Frequency (total events in last 14 days)
        fourteen_days_ago = current_time - timedelta(days=14)
        past_events = events_df[
            (events_df["student_id"] == student_id) &
            (events_df["timestamp"] >= fourteen_days_ago) &
            (events_df["timestamp"] <= current_time)
        ]
        engagement_frequency = len(past_events)

        # 7. Topic Difficulty Numeric
        topic_difficulty_numeric = target_topic_info.get("topic_difficulty_numeric", 2)

        # 8. Target Label: Struggling if score < 70
        target_struggling = 1 if score < 70 else 0

        feature_rows.append({
            "attempt_id": row["id"],
            "student_id": student_id,
            "topic_id": topic_id,
            "quiz_score": score,
            "recent_quiz_score": round(recent_quiz_score, 2),
            "historical_topic_score": round(historical_topic_score, 2),
            "attempts_count": topic_attempts_count,
            "total_time_spent": total_time_spent,
            "prerequisite_completion_rate": round(prereq_completion_rate, 2),
            "score_trend": round(score_trend, 2),
            "engagement_frequency": engagement_frequency,
            "topic_difficulty_numeric": topic_difficulty_numeric,
            "target_struggling": target_struggling,
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return pd.DataFrame(feature_rows)


def split_data_by_student(df, train_ratio=0.70, val_ratio=0.15, seed=42):
    """Split feature matrix by student ID to prevent data leakage."""
    np.random.seed(seed)
    unique_students = df["student_id"].unique()
    np.random.shuffle(unique_students)

    n_students = len(unique_students)
    n_train = int(n_students * train_ratio)
    n_val = int(n_students * val_ratio)

    train_ids = set(unique_students[:n_train])
    val_ids = set(unique_students[n_train:n_train + n_val])
    test_ids = set(unique_students[n_train + n_val:])

    train_df = df[df["student_id"].isin(train_ids)].reset_index(drop=True)
    val_df = df[df["student_id"].isin(val_ids)].reset_index(drop=True)
    test_df = df[df["student_id"].isin(test_ids)].reset_index(drop=True)

    return train_df, val_df, test_df


def main():
    print("⚙️ Running Feature Engineering Pipeline...")

    # Build Feature Matrix
    features_df = build_feature_matrix()

    all_features_path = os.path.join(PROCESSED_DATA_DIR, "feature_matrix_all.csv")
    features_df.to_csv(all_features_path, index=False)
    print(f" Generated complete feature matrix with {len(features_df)} records -> {all_features_path}")

    # Split Data by Student
    train_df, val_df, test_df = split_data_by_student(features_df)

    train_path = os.path.join(PROCESSED_DATA_DIR, "train_features.csv")
    val_path = os.path.join(PROCESSED_DATA_DIR, "val_features.csv")
    test_path = os.path.join(PROCESSED_DATA_DIR, "test_features.csv")

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f" Train Split: {len(train_df)} rows ({train_df['student_id'].nunique()} students) -> {train_path}")
    print(f" Val Split:   {len(val_df)} rows ({val_df['student_id'].nunique()} students) -> {val_path}")
    print(f" Test Split:  {len(test_df)} rows ({test_df['student_id'].nunique()} students) -> {test_path}")

    # Log struggle distribution
    struggle_rate = features_df["target_struggling"].mean() * 100
    print(f"📊 Target Struggle Rate: {struggle_rate:.2f}% (Struggling: {features_df['target_struggling'].sum()} / Total: {len(features_df)})")

    print("✅ Feature engineering pipeline completed successfully!")


if __name__ == "__main__":
    main()
