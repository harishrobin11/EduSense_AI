"""Unit and API integration tests for NLP Feedback Analysis Engine."""

import pytest
from ml.nlp.feedback_analyzer import nlp_analyzer
from app.db.models import User, Topic, StudentFeedback


def test_nlp_analyzer_sentiment_and_themes():
    """Test text cleaning, sentiment polarity scoring, and keyword extraction."""
    pos_text = "The machine learning explanation was great, clear, and very helpful!"
    pos_score, pos_label = nlp_analyzer.analyze_sentiment(pos_text)
    assert pos_label == "positive"
    assert pos_score > 0.1

    neg_text = "I felt confused, frustrated, and stuck on the difficult calculus problems."
    neg_score, neg_label = nlp_analyzer.analyze_sentiment(neg_text)
    assert neg_label == "negative"
    assert neg_score < -0.1

    keywords = nlp_analyzer.extract_keywords_and_themes(pos_text, top_n=3)
    assert len(keywords) > 0


def test_post_feedback_analyze_api(client, db_session):
    """Test POST /feedback/analyze endpoint and DB persistence."""
    user = User(id=401, name="Feedback Learner", email="fblearner@example.com", role="student")
    topic = Topic(id=40, subject="Python", name="AsyncIO", difficulty="hard", prerequisites=[])
    db_session.add_all([user, topic])
    db_session.commit()

    payload = {
        "student_id": 401,
        "topic_id": 40,
        "text": "AsyncIO concepts were really hard and confusing at first, but the examples were clear and good.",
    }

    response = client.post("/feedback/analyze", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["student_id"] == 401
    assert data["topic_id"] == 40
    assert "sentiment_score" in data
    assert "sentiment_label" in data
    assert "keywords_extracted" in data
    assert len(data["keywords_extracted"]) > 0

    # Verify saved in DB
    saved_fb = db_session.query(StudentFeedback).filter(StudentFeedback.student_id == 401).first()
    assert saved_fb is not None
    assert saved_fb.text == payload["text"]


def test_get_student_sentiment_api(client, db_session):
    """Test GET /students/{id}/sentiment endpoint."""
    user = User(id=402, name="Analytics Learner", email="analyticslearner@example.com", role="student")
    db_session.add(user)
    db_session.commit()

    fb1 = StudentFeedback(student_id=402, text="Great lecture, enjoyed it!")
    fb2 = StudentFeedback(student_id=402, text="Hard assignment, stuck on syntax.")
    db_session.add_all([fb1, fb2])
    db_session.commit()

    response = client.get("/students/402/sentiment")
    assert response.status_code == 200
    data = response.json()

    assert data["student_id"] == 402
    assert data["total_feedback_count"] == 2
    assert "sentiment_breakdown" in data
    assert "recurring_themes" in data
