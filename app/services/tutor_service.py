"""Tutor Service orchestrating student context, struggle prediction, and Socratic LLM tutoring."""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db.models import User, StudentProfile, Topic, QuizAttempt
from app.services.prediction_service import prediction_service
from ml.llm.tutor_engine import tutor_engine

# In-memory chat storage per student
CHAT_MEMORIES: Dict[int, List[Dict[str, str]]] = {}


class TutorService:
    """Service providing personalized Socratic LLM tutoring sessions for students."""

    def chat_with_tutor(
        self,
        db: Session,
        student_id: int,
        user_message: str,
        topic_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Process user message, incorporate ML struggle risk diagnosis, invoke LLM tutor, and maintain conversation log."""
        user = db.query(User).filter(User.id == student_id).first()
        if not user:
            raise ValueError(f"Student ID {student_id} not found.")

        # Default or specified topic
        target_topic = None
        if topic_id:
            target_topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not target_topic:
            target_topic = db.query(Topic).filter(Topic.id == 12).first() or db.query(Topic).first()

        topic_name = target_topic.name if target_topic else "Machine Learning Basics"
        subject = target_topic.subject if target_topic else "Machine Learning"

        # Safely parse topic prerequisites
        raw_prereqs = target_topic.prerequisites or [] if target_topic else []
        if isinstance(raw_prereqs, str):
            try:
                raw_prereqs = json.loads(raw_prereqs)
            except Exception:
                raw_prereqs = []
        if not isinstance(raw_prereqs, list):
            raw_prereqs = []

        all_topics = db.query(Topic).all()
        topic_dict = {t.id: t.name for t in all_topics}
        prereq_names = [topic_dict[p] for p in raw_prereqs if p in topic_dict]

        # Fetch recent quiz score for target topic
        attempts = db.query(QuizAttempt).filter(
            QuizAttempt.student_id == student_id, QuizAttempt.topic_id == (target_topic.id if target_topic else 1)
        ).all()
        recent_score = float(attempts[-1].score) if attempts else None

        # Predict struggle risk using prediction service
        struggle_risk = "low"
        try:
            pred = prediction_service.predict_from_db(
                db=db, student_id=student_id, topic_id=target_topic.id if target_topic else 1
            )
            struggle_risk = pred.get("risk_level", "low")
        except Exception:
            struggle_risk = "low"

        # Retrieve existing chat memory for student
        history = CHAT_MEMORIES.setdefault(student_id, [])

        # Generate response from tutor engine
        tutor_result = tutor_engine.generate_tutor_response(
            student_name=user.name,
            topic_name=topic_name,
            subject=subject,
            user_message=user_message,
            chat_history=history,
            recent_score=recent_score,
            struggle_risk=struggle_risk,
            weak_topics=[topic_name] if recent_score and recent_score < 70 else [],
            prerequisites=prereq_names,
        )

        # Update chat memory
        history.append({"role": "user", "content": user_message, "timestamp": datetime.utcnow().isoformat()})
        history.append({"role": "assistant", "content": tutor_result["tutor_response"], "timestamp": datetime.utcnow().isoformat()})

        logger.info(f"Generated tutor response for student {student_id} on topic '{topic_name}' via {tutor_result['provider']}")

        return {
            "student_id": student_id,
            "student_name": user.name,
            "topic_id": target_topic.id if target_topic else None,
            "topic_name": topic_name,
            "subject": subject,
            "struggle_risk_level": struggle_risk,
            "recent_score": recent_score,
            "user_message": user_message,
            "tutor_response": tutor_result["tutor_response"],
            "provider": tutor_result["provider"],
            "model_used": tutor_result["model_used"],
            "chat_history": history[-10:],
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_student_tutor_history(self, db: Session, student_id: int) -> Dict[str, Any]:
        """Retrieve historical chat conversation for a student."""
        user = db.query(User).filter(User.id == student_id).first()
        if not user:
            raise ValueError(f"Student ID {student_id} not found.")

        history = CHAT_MEMORIES.get(student_id, [])
        return {
            "student_id": student_id,
            "student_name": user.name,
            "total_messages": len(history),
            "chat_history": history,
        }


tutor_service = TutorService()
