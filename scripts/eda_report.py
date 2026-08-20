"""EDA report generator for EduSense AI synthetic dataset."""

import os
import json
import pandas as pd

RAW_DIR = os.path.join("ml", "data", "raw")
PROCESSED_DIR = os.path.join("ml", "data", "processed")


def generate_eda_report():
    """Analyze raw and processed datasets and write eda_summary.json."""
    students = pd.read_csv(os.path.join(RAW_DIR, "raw_students.csv"))
    topics = pd.read_csv(os.path.join(RAW_DIR, "raw_topics.csv"))
    attempts = pd.read_csv(os.path.join(RAW_DIR, "raw_quiz_attempts.csv"))
    events = pd.read_csv(os.path.join(RAW_DIR, "raw_learning_events.csv"))
    features = pd.read_csv(os.path.join(PROCESSED_DIR, "feature_matrix_all.csv"))

    summary = {
        "dataset_metadata": {
            "num_students": int(len(students)),
            "num_topics": int(len(topics)),
            "num_subjects": int(topics["subject"].nunique()),
            "total_quiz_attempts": int(len(attempts)),
            "total_learning_events": int(len(events)),
        },
        "target_distribution": {
            "struggling_count": int(features["target_struggling"].sum()),
            "mastering_count": int((features["target_struggling"] == 0).sum()),
            "struggle_rate": float(round(features["target_struggling"].mean(), 4)),
        },
        "quiz_score_stats": {
            "mean_score": float(round(attempts["score"].mean(), 2)),
            "std_score": float(round(attempts["score"].std(), 2)),
            "min_score": float(round(attempts["score"].min(), 2)),
            "max_score": float(round(attempts["score"].max(), 2)),
        },
        "feature_correlations_with_target": {
            col: float(round(features[col].corr(features["target_struggling"]), 4))
            for col in [
                "recent_quiz_score",
                "historical_topic_score",
                "attempts_count",
                "total_time_spent",
                "prerequisite_completion_rate",
                "score_trend",
                "engagement_frequency",
                "topic_difficulty_numeric",
            ]
        },
    }

    report_path = os.path.join(PROCESSED_DIR, "eda_summary.json")
    with open(report_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"📊 EDA report generated successfully -> {report_path}")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    generate_eda_report()
