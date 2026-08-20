"""Tests for ORM models and database operations."""

from app.db.models import User, StudentProfile, Topic, QuizAttempt


def test_create_user_and_profile(db_session):
    """Test creating a user and student profile."""
    user = User(name="Jane Doe", email="jane@example.com", role="student")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.name == "Jane Doe"
    assert user.role == "student"

    profile = StudentProfile(
        user_id=user.id,
        education_level="Undergraduate",
        goals="Master ML and AI",
        preferred_difficulty="medium",
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)

    assert profile.id is not None
    assert profile.user_id == user.id
    assert profile.education_level == "Undergraduate"


def test_create_topic_and_attempt(db_session):
    """Test creating a topic and a quiz attempt."""
    user = User(name="Alice Smith", email="alice@example.com", role="student")
    db_session.add(user)
    
    topic = Topic(
        subject="Machine Learning",
        name="Linear Regression",
        difficulty="easy",
        prerequisites=["Linear Algebra Basics"],
    )
    db_session.add(topic)
    db_session.commit()

    attempt = QuizAttempt(
        student_id=user.id,
        topic_id=topic.id,
        score=85.5,
        time_spent=120,
        attempts=1,
    )
    db_session.add(attempt)
    db_session.commit()
    db_session.refresh(attempt)

    assert attempt.id is not None
    assert attempt.score == 85.5
    assert attempt.topic.name == "Linear Regression"
