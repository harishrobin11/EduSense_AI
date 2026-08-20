"""Unit and API integration tests for recommendation engine."""

import pytest
from ml.recommender.content_recommender import ContentBasedRecommender
from app.db.models import User, Topic, QuizAttempt, StudentProfile


@pytest.fixture
def sample_topics():
    return [
        {"id": 1, "subject": "Python", "name": "Variables", "difficulty": "easy", "prerequisites": []},
        {"id": 2, "subject": "Python", "name": "Loops", "difficulty": "easy", "prerequisites": [1]},
        {"id": 3, "subject": "Python", "name": "Functions", "difficulty": "medium", "prerequisites": [2]},
        {"id": 4, "subject": "ML", "name": "Linear Regression", "difficulty": "easy", "prerequisites": [2]},
        {"id": 5, "subject": "ML", "name": "Logistic Regression", "difficulty": "medium", "prerequisites": [4]},
    ]


def test_recommender_weak_topics_and_prerequisite_filtering(sample_topics):
    """Test recommender identifies weak topics and respects prerequisites."""
    recommender = ContentBasedRecommender(sample_topics)

    # Student attempted topic 4 (Linear Regression) and scored 50% (weak)
    # Mastered topic 1 (Variables) with score 90%
    attempts = [
        {"topic_id": 1, "score": 90.0},
        {"topic_id": 4, "score": 50.0},
    ]

    weak_topics = recommender.detect_weak_topics(attempts)
    assert 4 in weak_topics

    mastered_topics = recommender.detect_mastered_topics(attempts)
    assert 1 in mastered_topics

    recs = recommender.generate_recommendations(
        attempts_history=attempts, preferred_difficulty="medium", top_n=5
    )

    assert len(recs) > 0
    rec_topic_ids = [r["topic_id"] for r in recs]
    # Topic 4 (weak) should be recommended or its prerequisites
    assert 4 in rec_topic_ids or 2 in rec_topic_ids

    # Topic 1 (mastered >=80%) should NOT be recommended
    assert 1 not in rec_topic_ids

    # Each recommendation must have a non-empty explanation reason
    for r in recs:
        assert len(r["reason"]) > 0
        assert "score" in r


def test_get_topics_api(client, db_session):
    """Test GET /topics endpoint."""
    topic = Topic(id=99, subject="Testing", name="Unit Testing Basics", difficulty="easy", prerequisites=[])
    db_session.add(topic)
    db_session.commit()

    response = client.get("/topics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_student_recommendations_api(client, db_session):
    """Test GET /students/{id}/recommendations endpoint."""
    user = User(id=201, name="Rec Student", email="recstudent@example.com", role="student")
    profile = StudentProfile(user_id=201, education_level="Undergraduate", goals="Learn ML", preferred_difficulty="medium")
    topic1 = Topic(id=10, subject="Python", name="Python Basics", difficulty="easy", prerequisites=[])
    topic2 = Topic(id=11, subject="Python", name="Python OOP", difficulty="medium", prerequisites=[10])

    db_session.add_all([user, profile, topic1, topic2])

    attempt = QuizAttempt(student_id=201, topic_id=10, score=85.0, time_spent=100, attempts=1)
    db_session.add(attempt)
    db_session.commit()

    response = client.get("/students/201/recommendations?top_n=3")
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == 201
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0

    first_rec = data["recommendations"][0]
    assert "topic_name" in first_rec
    assert "reason" in first_rec
    assert "score" in first_rec
