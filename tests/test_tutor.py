"""Unit and API integration tests for LLM Conversational Tutor Engine."""

import pytest
from ml.llm.tutor_engine import tutor_engine
from app.db.models import User, Topic, QuizAttempt


def test_tutor_engine_prompt_and_fallback():
    """Test Socratic prompt builder and fallback tutor response generation."""
    prompt = tutor_engine.build_socratic_prompt(
        student_name="Alex",
        topic_name="Logistic Regression",
        subject="Machine Learning",
        recent_score=55.0,
        struggle_risk="high",
        weak_topics=["Logistic Regression"],
        prerequisites=["Linear Regression"],
    )

    assert "Alex" in prompt
    assert "Logistic Regression" in prompt
    assert "HIGH" in prompt
    assert "Socratic" in prompt

    response_data = tutor_engine.generate_tutor_response(
        student_name="Alex",
        topic_name="Logistic Regression",
        subject="Machine Learning",
        user_message="Can you explain how thresholding works?",
        chat_history=[],
        struggle_risk="high",
        prerequisites=["Linear Regression"],
    )

    assert "tutor_response" in response_data
    assert len(response_data["tutor_response"]) > 0
    assert response_data["provider"] in ("ollama", "socratic_fallback_ai")


def test_post_tutor_chat_api(client, db_session):
    """Test POST /tutor/chat endpoint."""
    user = User(id=501, name="Tutor Learner", email="tutorlearner@example.com", role="student")
    topic = Topic(id=50, subject="Machine Learning", name="Decision Trees", difficulty="medium", prerequisites=[])
    db_session.add_all([user, topic])
    db_session.commit()

    payload = {
        "student_id": 501,
        "topic_id": 50,
        "message": "What is entropy in decision trees?",
    }

    response = client.post("/tutor/chat", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["student_id"] == 501
    assert data["topic_name"] == "Decision Trees"
    assert "tutor_response" in data
    assert "provider" in data
    assert len(data["chat_history"]) > 0


def test_get_tutor_history_api(client, db_session):
    """Test GET /students/{id}/tutor-history endpoint."""
    user = User(id=502, name="History Learner", email="historylearner@example.com", role="student")
    db_session.add(user)
    db_session.commit()

    # Trigger a chat first
    client.post("/tutor/chat", json={"student_id": 502, "message": "Hello tutor!"})

    response = client.get("/students/502/tutor-history")
    assert response.status_code == 200
    data = response.json()

    assert data["student_id"] == 502
    assert data["total_messages"] >= 2
    assert "chat_history" in data
