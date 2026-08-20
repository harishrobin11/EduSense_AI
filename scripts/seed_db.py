"""Database seeding script for EduSense AI."""

import os
import ast
import json
import pandas as pd
from datetime import datetime
from app.db.session import SessionLocal, init_db, engine, Base
from app.db.models import (
    User,
    StudentProfile,
    Topic,
    LearningResource,
    QuizAttempt,
    LearningEvent,
    StudentFeedback,
)

RAW_DIR = os.path.join("ml", "data", "raw")


def seed_database():
    """Populate database tables with synthetic educational data."""
    print("🌱 Initializing and seeding database tables...")

    # Ensure tables exist
    init_db()

    db = SessionLocal()

    try:
        # Clear existing data in reverse order of foreign key dependencies
        db.query(StudentFeedback).delete()
        db.query(LearningEvent).delete()
        db.query(QuizAttempt).delete()
        db.query(LearningResource).delete()
        db.query(Topic).delete()
        db.query(StudentProfile).delete()
        db.query(User).delete()
        db.commit()

        # 1. Seed Topics
        topics_df = pd.read_csv(os.path.join(RAW_DIR, "raw_topics.csv"))
        topic_id_map = {}

        for _, row in topics_df.iterrows():
            prereqs = row["prerequisites"]
            if isinstance(prereqs, str):
                try:
                    prereqs = ast.literal_eval(prereqs)
                except Exception:
                    prereqs = []

            topic = Topic(
                id=int(row["id"]),
                subject=row["subject"],
                name=row["name"],
                difficulty=row["difficulty"],
                prerequisites=prereqs,
            )
            db.add(topic)
            topic_id_map[row["id"]] = topic

        db.commit()
        print(f" Seeded {len(topics_df)} Topic records.")

        # Seed Learning Resources for Topics
        resource_id = 1
        for topic_id, topic_obj in topic_id_map.items():
            resources = [
                LearningResource(
                    id=resource_id,
                    topic_id=topic_id,
                    type="article",
                    title=f"Introduction to {topic_obj.name}",
                    url_or_path=f"https://edusense.ai/learn/{topic_id}/intro",
                    difficulty=topic_obj.difficulty,
                ),
                LearningResource(
                    id=resource_id + 1,
                    topic_id=topic_id,
                    type="video",
                    title=f"Deep Dive: {topic_obj.name} Video Lecture",
                    url_or_path=f"https://edusense.ai/learn/{topic_id}/video",
                    difficulty=topic_obj.difficulty,
                ),
                LearningResource(
                    id=resource_id + 2,
                    topic_id=topic_id,
                    type="exercise",
                    title=f"Practice Problems on {topic_obj.name}",
                    url_or_path=f"https://edusense.ai/learn/{topic_id}/practice",
                    difficulty=topic_obj.difficulty,
                ),
            ]
            for r in resources:
                db.add(r)
            resource_id += 3

        db.commit()
        print(" Seeded Learning Resources for all topics.")

        # 2. Seed Users & Student Profiles
        students_df = pd.read_csv(os.path.join(RAW_DIR, "raw_students.csv"))
        user_id_map = {}

        for _, row in students_df.iterrows():
            created_dt = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S")
            user = User(
                id=int(row["id"]),
                name=row["name"],
                email=row["email"],
                role=row["role"],
                created_at=created_dt,
            )
            db.add(user)

            profile = StudentProfile(
                user_id=int(row["id"]),
                education_level=row["education_level"],
                goals=row["goals"],
                preferred_difficulty=row["preferred_difficulty"],
            )
            db.add(profile)
            user_id_map[row["id"]] = user

        db.commit()
        print(f" Seeded {len(students_df)} User & StudentProfile records.")

        # 3. Seed Quiz Attempts
        attempts_df = pd.read_csv(os.path.join(RAW_DIR, "raw_quiz_attempts.csv"))
        for _, row in attempts_df.iterrows():
            ts = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            attempt = QuizAttempt(
                id=int(row["id"]),
                student_id=int(row["student_id"]),
                topic_id=int(row["topic_id"]),
                score=float(row["score"]),
                time_spent=int(row["time_spent"]),
                attempts=int(row["attempts"]),
                timestamp=ts,
            )
            db.add(attempt)

        db.commit()
        print(f" Seeded {len(attempts_df)} QuizAttempt records.")

        # 4. Seed Learning Events
        events_df = pd.read_csv(os.path.join(RAW_DIR, "raw_learning_events.csv"))
        for _, row in events_df.iterrows():
            ts = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            event = LearningEvent(
                id=int(row["id"]),
                student_id=int(row["student_id"]),
                topic_id=int(row["topic_id"]),
                event_type=row["event_type"],
                duration=int(row["duration"]),
                timestamp=ts,
            )
            db.add(event)

        db.commit()
        print(f" Seeded {len(events_df)} LearningEvent records.")

        # 5. Seed Student Feedback
        feedback_df = pd.read_csv(os.path.join(RAW_DIR, "raw_feedback.csv"))
        for _, row in feedback_df.iterrows():
            ts = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S")
            fb = StudentFeedback(
                id=int(row["id"]),
                student_id=int(row["student_id"]),
                topic_id=int(row["topic_id"]) if pd.notnull(row["topic_id"]) else None,
                text=row["text"],
                timestamp=ts,
            )
            db.add(fb)

        db.commit()
        print(f" Seeded {len(feedback_df)} StudentFeedback records.")

        print("✅ Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during database seeding: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
