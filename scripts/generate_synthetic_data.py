"""Synthetic educational dataset generator for EduSense AI."""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set deterministic seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

RAW_DATA_DIR = os.path.join("ml", "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# 1. Generate Topics & Prerequisites
TOPICS_DATA = [
    # Subject: Python Programming
    {"id": 1, "subject": "Python Programming", "name": "Variables & Data Types", "difficulty": "easy", "prerequisites": []},
    {"id": 2, "subject": "Python Programming", "name": "Control Flow & Loops", "difficulty": "easy", "prerequisites": [1]},
    {"id": 3, "subject": "Python Programming", "name": "Functions & Modules", "difficulty": "medium", "prerequisites": [2]},
    {"id": 4, "subject": "Python Programming", "name": "Object-Oriented Programming", "difficulty": "medium", "prerequisites": [3]},
    {"id": 5, "subject": "Python Programming", "name": "AsyncIO & Concurrency", "difficulty": "hard", "prerequisites": [4]},

    # Subject: Mathematics for ML
    {"id": 6, "subject": "Mathematics for ML", "name": "Linear Algebra Basics", "difficulty": "easy", "prerequisites": []},
    {"id": 7, "subject": "Mathematics for ML", "name": "Matrix Operations & Vectors", "difficulty": "medium", "prerequisites": [6]},
    {"id": 8, "subject": "Mathematics for ML", "name": "Calculus & Derivatives", "difficulty": "medium", "prerequisites": []},
    {"id": 9, "subject": "Mathematics for ML", "name": "Gradient & Partial Derivatives", "difficulty": "hard", "prerequisites": [8]},
    {"id": 10, "subject": "Mathematics for ML", "name": "Probability & Statistics", "difficulty": "medium", "prerequisites": []},

    # Subject: Machine Learning
    {"id": 11, "subject": "Machine Learning", "name": "Linear Regression", "difficulty": "easy", "prerequisites": [2, 7]},
    {"id": 12, "subject": "Machine Learning", "name": "Logistic Regression", "difficulty": "medium", "prerequisites": [9, 11]},
    {"id": 13, "subject": "Machine Learning", "name": "Decision Trees & Random Forests", "difficulty": "medium", "prerequisites": [12]},
    {"id": 14, "subject": "Machine Learning", "name": "Support Vector Machines", "difficulty": "hard", "prerequisites": [7, 12]},
    {"id": 15, "subject": "Machine Learning", "name": "Model Evaluation & Cross-Validation", "difficulty": "medium", "prerequisites": [11]},

    # Subject: Deep Learning & NLP
    {"id": 16, "subject": "Deep Learning & NLP", "name": "Neural Networks & Backpropagation", "difficulty": "hard", "prerequisites": [9, 12]},
    {"id": 17, "subject": "Deep Learning & NLP", "name": "Convolutional Neural Networks", "difficulty": "hard", "prerequisites": [16]},
    {"id": 18, "subject": "Deep Learning & NLP", "name": "Recurrent Neural Networks & LSTM", "difficulty": "hard", "prerequisites": [16]},
    {"id": 19, "subject": "Deep Learning & NLP", "name": "TF-IDF & Text Embeddings", "difficulty": "medium", "prerequisites": [10, 11]},
    {"id": 20, "subject": "Deep Learning & NLP", "name": "Transformers & Attention Mechanism", "difficulty": "hard", "prerequisites": [16, 19]},
]


def generate_students(num_students=500):
    """Generate realistic student profiles."""
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley", "Avery", "Dakota", "Cameron", "Jesse", "Reese", "Skyler", "Casey"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson"]

    education_levels = ["High School", "Undergraduate", "Graduate", "Self-Taught / Professional"]
    goals = [
        "Master Machine Learning and AI engineering",
        "Build portfolio projects for tech interviews",
        "Improve fundamental computer science and math skills",
        "Transition career into Data Science and AI",
    ]
    difficulties = ["easy", "medium", "hard"]

    # Student Archetypes: 0=High Performer, 1=Consistent Learner, 2=Struggling Learner, 3=Inconsistent Learner
    archetypes = [0, 1, 2, 3]
    archetype_weights = [0.25, 0.40, 0.25, 0.10]

    students = []
    for i in range(1, num_students + 1):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"student_{i}@edusense.ai"
        role = "student"
        created_at = datetime(2026, 1, 1) + timedelta(days=random.randint(0, 30))
        archetype = np.random.choice(archetypes, p=archetype_weights)

        students.append({
            "id": i,
            "name": name,
            "email": email,
            "role": role,
            "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "education_level": random.choice(education_levels),
            "goals": random.choice(goals),
            "preferred_difficulty": random.choice(difficulties),
            "archetype": archetype,
        })

    return pd.DataFrame(students)


def generate_quiz_attempts_and_events(students_df):
    """Generate quiz attempt histories and learning events."""
    attempts = []
    events = []
    feedbacks = []

    feedback_templates_confused = [
        "I felt confused by the math behind this topic.",
        "The prerequisites for this concept were tricky for me.",
        "I had trouble understanding the step-by-step logic.",
        "Need more examples and visual explanations.",
        "Struggled with the quiz questions on this topic.",
    ]

    feedback_templates_clear = [
        "Clear explanation! Really enjoyed this section.",
        "The examples made this concept easy to understand.",
        "Great overview, ready for the next challenge.",
        "Understood everything on the first try.",
        "Good topic structure and smooth difficulty curve.",
    ]

    start_date = datetime(2026, 2, 1)

    attempt_id = 1
    event_id = 1
    feedback_id = 1

    for idx, student in students_df.iterrows():
        student_id = student["id"]
        archetype = student["archetype"]

        # Base skill probability depending on archetype
        if archetype == 0:  # High Performer
            base_pass_prob = 0.90
            avg_time = 60
        elif archetype == 1:  # Consistent Learner
            base_pass_prob = 0.75
            avg_time = 90
        elif archetype == 2:  # Struggling Learner
            base_pass_prob = 0.45
            avg_time = 140
        else:  # Inconsistent Learner
            base_pass_prob = 0.60
            avg_time = 110

        # Number of topics student attempted (10 to 20 topics)
        num_topics_attempted = random.randint(10, len(TOPICS_DATA))
        attempted_topics = TOPICS_DATA[:num_topics_attempted]

        # Keep track of topic scores for calculating prerequisites
        student_topic_scores = {}

        current_time = datetime.strptime(student["created_at"], "%Y-%m-%d %H:%M:%S") + timedelta(days=1)

        for topic in attempted_topics:
            topic_id = topic["id"]
            topic_diff = topic["difficulty"]

            # Difficulty modifier
            diff_mod = 0.0 if topic_diff == "easy" else (-0.12 if topic_diff == "medium" else -0.25)

            # Check prerequisite mastery
            prereqs = topic["prerequisites"]
            prereq_scores = [student_topic_scores.get(p, 50) for p in prereqs]
            prereq_penalty = 0.0
            if prereq_scores:
                avg_prereq = np.mean(prereq_scores)
                if avg_prereq < 70:
                    prereq_penalty = (70 - avg_prereq) * 0.005

            # Calculate pass probability for this attempt
            effective_pass_prob = max(0.15, min(0.98, base_pass_prob + diff_mod - prereq_penalty))

            # Number of quiz attempts on this topic (1 to 3)
            num_attempts = 1 if random.random() < effective_pass_prob else random.randint(1, 3)

            for att_num in range(1, num_attempts + 1):
                current_time += timedelta(hours=random.randint(4, 48))

                # Calculate score 0-100
                if random.random() < effective_pass_prob:
                    score = random.uniform(70.0, 100.0)
                else:
                    score = random.uniform(30.0, 69.9)

                time_spent = int(np.random.normal(avg_time, 20))
                time_spent = max(30, time_spent)

                student_topic_scores[topic_id] = score

                attempts.append({
                    "id": attempt_id,
                    "student_id": student_id,
                    "topic_id": topic_id,
                    "score": round(score, 1),
                    "time_spent": time_spent,
                    "attempts": att_num,
                    "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                })
                attempt_id += 1

                # Generate related learning events
                events.append({
                    "id": event_id,
                    "student_id": student_id,
                    "topic_id": topic_id,
                    "event_type": random.choice(["view_resource", "complete_lesson", "search_topic"]),
                    "duration": random.randint(60, 600),
                    "timestamp": (current_time - timedelta(minutes=random.randint(10, 60))).strftime("%Y-%m-%d %H:%M:%S"),
                })
                event_id += 1

            # Generate student feedback periodically
            if random.random() < 0.35:
                if score < 70:
                    fb_text = random.choice(feedback_templates_confused)
                else:
                    fb_text = random.choice(feedback_templates_clear)

                feedbacks.append({
                    "id": feedback_id,
                    "student_id": student_id,
                    "topic_id": topic_id,
                    "text": fb_text,
                    "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                })
                feedback_id += 1

    return pd.DataFrame(attempts), pd.DataFrame(events), pd.DataFrame(feedbacks)


def main():
    print("🚀 Generating synthetic educational dataset...")

    # 1. Save Topics
    topics_df = pd.DataFrame(TOPICS_DATA)
    topics_path = os.path.join(RAW_DATA_DIR, "raw_topics.csv")
    topics_df.to_csv(topics_path, index=False)
    print(f" Saved {len(topics_df)} topics to {topics_path}")

    # 2. Save Students
    students_df = generate_students(num_students=500)
    students_path = os.path.join(RAW_DATA_DIR, "raw_students.csv")
    students_df.to_csv(students_path, index=False)
    print(f" Saved {len(students_df)} students to {students_path}")

    # 3. Save Quiz Attempts, Events, Feedback
    attempts_df, events_df, feedback_df = generate_quiz_attempts_and_events(students_df)

    attempts_path = os.path.join(RAW_DATA_DIR, "raw_quiz_attempts.csv")
    attempts_df.to_csv(attempts_path, index=False)
    print(f" Saved {len(attempts_df)} quiz attempts to {attempts_path}")

    events_path = os.path.join(RAW_DATA_DIR, "raw_learning_events.csv")
    events_df.to_csv(events_path, index=False)
    print(f" Saved {len(events_df)} learning events to {events_path}")

    feedback_path = os.path.join(RAW_DATA_DIR, "raw_feedback.csv")
    feedback_df.to_csv(feedback_path, index=False)
    print(f" Saved {len(feedback_df)} feedback entries to {feedback_path}")

    print("✅ Synthetic dataset generation completed successfully!")


if __name__ == "__main__":
    main()
