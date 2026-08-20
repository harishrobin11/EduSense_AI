"""Unit and API integration tests for Personalization & Learning Path Engine."""

import pytest
from app.services.personalization_service import personalization_service
from app.db.models import User, StudentProfile, Topic, QuizAttempt


def test_adaptive_difficulty_scaling():
    """Test adaptive difficulty shifts based on performance history."""
    # Test scaling UP when recent average >= 85%
    up_history = [{"score": 75.0}, {"score": 90.0}, {"score": 95.0}, {"score": 92.0}]
    new_diff_up, reason_up = personalization_service.compute_adaptive_difficulty("easy", up_history)
    assert new_diff_up == "medium"
    assert "scaled UP" in reason_up

    # Test scaling DOWN when recent average < 60%
    down_history = [{"score": 80.0}, {"score": 50.0}, {"score": 45.0}, {"score": 52.0}]
    new_diff_down, reason_down = personalization_service.compute_adaptive_difficulty("hard", down_history)
    assert new_diff_down == "medium"
    assert "adjusted DOWN" in reason_down

    # Test MAINTAINING when performance is stable
    stable_history = [{"score": 75.0}, {"score": 72.0}, {"score": 74.0}]
    new_diff_st, reason_st = personalization_service.compute_adaptive_difficulty("medium", stable_history)
    assert new_diff_st == "medium"
    assert "Maintaining" in reason_st


def test_learning_path_generation_and_api(client, db_session):
    """Test POST /learning-path endpoint and topological ordering."""
    user = User(id=301, name="Path Learner", email="pathlearner@example.com", role="student")
    profile = StudentProfile(user_id=301, education_level="Undergraduate", goals="Machine Learning", preferred_difficulty="easy")

    t1 = Topic(id=30, subject="ML", name="Intro ML", difficulty="easy", prerequisites=[])
    t2 = Topic(id=31, subject="ML", name="Supervised Learning", difficulty="medium", prerequisites=[30])

    db_session.add_all([user, profile, t1, t2])
    db_session.commit()

    payload = {
        "student_id": 301,
        "target_subject": "ML",
    }

    response = client.post("/learning-path", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["student_id"] == 301
    assert "steps" in data
    assert len(data["steps"]) >= 2

    # Verify prerequisite ordering: Intro ML (t1) step_number < Supervised Learning (t2) step_number
    step_map = {step["topic_id"]: step["step_number"] for step in data["steps"]}
    assert step_map[30] < step_map[31]


def test_submit_quiz_attempt_api(client, db_session):
    """Test POST /quiz-attempts endpoint and automatic profile updating."""
    user = User(id=302, name="Quiz Taker", email="quiztaker@example.com", role="student")
    profile = StudentProfile(user_id=302, education_level="Graduate", goals="Deep Learning", preferred_difficulty="easy")
    topic = Topic(id=32, subject="Python", name="Data Types", difficulty="easy", prerequisites=[])

    db_session.add_all([user, profile, topic])
    db_session.commit()

    payload = {
        "student_id": 302,
        "topic_id": 32,
        "score": 95.0,
        "time_spent": 180,
    }

    response = client.post("/quiz-attempts", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["student_id"] == 302
    assert data["topic_id"] == 32
    assert data["score"] == 95.0
    assert "new_difficulty" in data
