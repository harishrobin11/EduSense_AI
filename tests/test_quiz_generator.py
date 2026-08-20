"""Unit and API integration tests for AI Quiz Generator & Closed Learning Loop."""

import pytest
from ml.generators.quiz_generator import quiz_generator
from app.db.models import User, Topic, StudentProfile, QuizAttempt


def test_quiz_generator_mcq_generation():
    """Test dynamic quiz question and option generation."""
    questions = quiz_generator.generate_quiz(
        topic_name="Logistic Regression",
        subject="Machine Learning",
        difficulty="medium",
        question_count=3,
    )

    assert len(questions) == 3
    for q in questions:
        assert "question_id" in q
        assert len(q["options"]) == 4
        assert 0 <= q["correct_option_index"] < 4
        assert len(q["explanation"]) > 0


def test_post_quiz_generate_api(client, db_session):
    """Test POST /quiz/generate endpoint."""
    user = User(id=601, name="Quiz Learner", email="quizlearner@example.com", role="student")
    topic = Topic(id=60, subject="Machine Learning", name="Linear Regression", difficulty="easy", prerequisites=[])
    db_session.add_all([user, topic])
    db_session.commit()

    payload = {
        "student_id": 601,
        "topic_id": 60,
        "question_count": 2,
    }

    response = client.post("/quiz/generate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["student_id"] == 601
    assert data["topic_id"] == 60
    assert "quiz_session_id" in data
    assert len(data["questions"]) == 2
    # Ensure correct answer is hidden from student payload
    assert "correct_option_index" not in data["questions"][0]


def test_post_quiz_submit_closed_loop_api(client, db_session):
    """Test POST /quiz/submit endpoint and closed-loop state updates."""
    user = User(id=602, name="Closed Loop Learner", email="closedloop@example.com", role="student")
    profile = StudentProfile(user_id=602, education_level="Undergraduate", goals="AI Master", preferred_difficulty="easy")
    topic = Topic(id=61, subject="Python Programming", name="Variables", difficulty="easy", prerequisites=[])

    db_session.add_all([user, profile, topic])
    db_session.commit()

    # Step 1: Generate quiz
    gen_res = client.post("/quiz/generate", json={"student_id": 602, "topic_id": 61, "question_count": 2})
    assert gen_res.status_code == 200
    gen_data = gen_res.json()
    quiz_sid = gen_data["quiz_session_id"]

    # Step 2: Submit quiz answers
    sub_payload = {
        "student_id": 602,
        "topic_id": 61,
        "quiz_session_id": quiz_sid,
        "answers": [0, 0],
        "time_spent": 120,
    }

    sub_res = client.post("/quiz/submit", json=sub_payload)
    assert sub_res.status_code == 200
    data = sub_res.json()

    assert data["student_id"] == 602
    assert "score_percentage" in data
    assert "closed_loop_updates" in data

    cl_updates = data["closed_loop_updates"]
    assert cl_updates["quiz_attempt_recorded"] is True
    assert cl_updates["learning_path_updated"] is True
    assert "struggle_risk_level" in cl_updates

    # Verify attempt saved in DB
    attempts = db_session.query(QuizAttempt).filter(QuizAttempt.student_id == 602).all()
    assert len(attempts) > 0
