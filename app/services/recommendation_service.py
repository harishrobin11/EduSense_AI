"""Recommendation Service connecting DB and ContentBasedRecommender."""

import json
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db.models import User, StudentProfile, Topic, LearningResource, QuizAttempt, Recommendation
from ml.recommender.content_recommender import ContentBasedRecommender


class RecommendationService:
    """Service orchestrating student recommendation generation and database storage."""

    def get_student_recommendations(
        self, db: Session, student_id: int, top_n: int = 5
    ) -> Dict[str, Any]:
        """Fetch student context, compute recommendations, save to DB, and return response."""
        user = db.query(User).filter(User.id == student_id).first()
        if not user:
            raise ValueError(f"Student ID {student_id} not found.")

        profile = db.query(StudentProfile).filter(StudentProfile.user_id == student_id).first()
        preferred_difficulty = profile.preferred_difficulty if profile else "medium"

        # Load all topics from DB
        db_topics = db.query(Topic).all()
        topics_data = []
        topic_map = {}
        for t in db_topics:
            td = {
                "id": t.id,
                "subject": t.subject,
                "name": t.name,
                "difficulty": t.difficulty,
                "prerequisites": t.prerequisites or [],
            }
            topics_data.append(td)
            topic_map[t.id] = t

        # Load student quiz attempt history
        db_attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).all()
        attempts_history = [
            {
                "topic_id": a.topic_id,
                "score": a.score,
                "time_spent": a.time_spent,
                "attempts": a.attempts,
            }
            for a in db_attempts
        ]

        # Initialize Recommender and generate recommendations
        recommender = ContentBasedRecommender(topics_data)
        raw_recs = recommender.generate_recommendations(
            attempts_history=attempts_history,
            preferred_difficulty=preferred_difficulty,
            top_n=top_n,
        )

        # Clear old recommendations for this student and persist new ones
        db.query(Recommendation).filter(Recommendation.student_id == student_id).delete()

        recommendation_results = []
        for item in raw_recs:
            t_id = item["topic_id"]

            # Save to recommendations DB table
            rec_db = Recommendation(
                student_id=student_id,
                topic_id=t_id,
                score=item["score"],
                reason=item["reason"],
                created_at=datetime.utcnow(),
            )
            db.add(rec_db)

            # Fetch associated learning resources
            resources_db = db.query(LearningResource).filter(LearningResource.topic_id == t_id).all()
            resources_list = [
                {
                    "id": r.id,
                    "type": r.type,
                    "title": r.title,
                    "url_or_path": r.url_or_path,
                    "difficulty": r.difficulty,
                }
                for r in resources_db
            ]

            item_result = {**item, "resources": resources_list}
            recommendation_results.append(item_result)

        db.commit()
        logger.info(f"Generated and saved {len(recommendation_results)} recommendations for student {student_id}")

        # Weak topics detected for response summary
        weak_topics = recommender.detect_weak_topics(attempts_history)
        weak_topic_names = [topic_map[w].name for w in weak_topics if w in topic_map]

        return {
            "student_id": student_id,
            "student_name": user.name,
            "preferred_difficulty": preferred_difficulty,
            "weak_topics_detected": weak_topic_names,
            "recommendations": recommendation_results,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_all_topics(self, db: Session) -> List[Dict[str, Any]]:
        """Return catalog of all available topics."""
        topics = db.query(Topic).all()
        return [
            {
                "id": t.id,
                "subject": t.subject,
                "name": t.name,
                "difficulty": t.difficulty,
                "prerequisites": t.prerequisites or [],
            }
            for t in topics
        ]


recommendation_service = RecommendationService()
