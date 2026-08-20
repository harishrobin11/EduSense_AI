"""Quiz Service executing quiz generation and closed-loop state updates."""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db.models import User, StudentProfile, Topic, QuizAttempt
from app.services.prediction_service import prediction_service
from app.services.personalization_service import personalization_service
from app.services.recommendation_service import recommendation_service
from ml.generators.quiz_generator import quiz_generator

# In-memory storage for active quiz sessions
ACTIVE_QUIZZES: Dict[str, Dict[str, Any]] = {}


class QuizService:
    """Service generating quizzes and executing closed-loop learning state updates."""

    def generate_quiz_session(
        self,
        db: Session,
        student_id: int,
        topic_id: int,
        question_count: int = 3,
    ) -> Dict[str, Any]:
        """Generate dynamic quiz questions tailored to student target difficulty."""
        user = db.query(User).filter(User.id == student_id).first()
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not user:
            raise ValueError(f"Student ID {student_id} not found.")
        if not topic:
            raise ValueError(f"Topic ID {topic_id} not found.")

        profile = db.query(StudentProfile).filter(StudentProfile.user_id == student_id).first()
        target_diff = profile.preferred_difficulty if profile else "medium"

        # Generate questions
        questions = quiz_generator.generate_quiz(
            topic_name=topic.name,
            subject=topic.subject,
            difficulty=target_diff,
            question_count=question_count,
        )

        quiz_session_id = f"quiz_{student_id}_{topic_id}_{int(datetime.utcnow().timestamp())}"
        quiz_data = {
            "quiz_session_id": quiz_session_id,
            "student_id": student_id,
            "student_name": user.name,
            "topic_id": topic_id,
            "topic_name": topic.name,
            "subject": topic.subject,
            "difficulty": target_diff,
            "question_count": len(questions),
            "questions": questions,
            "generated_at": datetime.utcnow().isoformat(),
        }

        ACTIVE_QUIZZES[quiz_session_id] = quiz_data
        logger.info(f"Generated quiz {quiz_session_id} for student {student_id} on '{topic.name}'")

        # Sanitize questions for student view (remove correct_option_index)
        student_questions = []
        for q in questions:
            sq = q.copy()
            sq.pop("correct_option_index", None)
            sq.pop("explanation", None)
            student_questions.append(sq)

        return {
            "quiz_session_id": quiz_session_id,
            "student_id": student_id,
            "student_name": user.name,
            "topic_id": topic_id,
            "topic_name": topic.name,
            "subject": topic.subject,
            "difficulty": target_diff,
            "question_count": len(questions),
            "questions": student_questions,
            "generated_at": quiz_data["generated_at"],
        }

    def submit_quiz_and_run_closed_loop(
        self,
        db: Session,
        student_id: int,
        topic_id: int,
        quiz_session_id: str,
        user_answers: List[int],
        time_spent: int = 180,
    ) -> Dict[str, Any]:
        """
        Evaluate quiz, save attempt, and execute CLOSED LEARNING LOOP:
        1. Record attempt in DB.
        2. Recalculate struggle prediction risk.
        3. Trigger adaptive difficulty scaling.
        4. Regenerate learning path step status.
        5. Refresh recommendations.
        """
        # Fetch or recreate session questions
        quiz_session = ACTIVE_QUIZZES.get(quiz_session_id)
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise ValueError(f"Topic ID {topic_id} not found.")

        if quiz_session and "questions" in quiz_session:
            questions = quiz_session["questions"]
        else:
            profile = db.query(StudentProfile).filter(StudentProfile.user_id == student_id).first()
            diff = profile.preferred_difficulty if profile else "medium"
            questions = quiz_generator.generate_quiz(
                topic_name=topic.name, subject=topic.subject, difficulty=diff, question_count=len(user_answers) or 3
            )

        # Evaluate score
        score_pct, correct_count, breakdown = quiz_generator.evaluate_quiz_answers(
            questions=questions, user_answers=user_answers
        )

        # CLOSED LOOP STEP 1: Process quiz attempt & trigger adaptive difficulty update
        attempt_res = personalization_service.process_quiz_attempt(
            db=db,
            student_id=student_id,
            topic_id=topic_id,
            score=score_pct,
            time_spent=time_spent,
        )

        # CLOSED LOOP STEP 2: Recalculate ML Struggle Prediction Risk
        new_struggle_risk = "low"
        struggle_prob = 0.0
        try:
            pred = prediction_service.predict_from_db(db=db, student_id=student_id, topic_id=topic_id)
            new_struggle_risk = pred.get("risk_level", "low")
            struggle_prob = pred.get("struggle_probability", 0.0)
        except Exception:
            pass

        # CLOSED LOOP STEP 3: Refresh Learning Path step status
        lp_res = personalization_service.generate_learning_path(db=db, student_id=student_id)

        # CLOSED LOOP STEP 4: Refresh Recommendations
        try:
            recommendation_service.get_student_recommendations(db=db, student_id=student_id, top_n=5)
        except Exception:
            pass

        is_passed = score_pct >= 70.0
        logger.info(f"Closed learning loop executed for student {student_id} (Score: {score_pct}%, Risk: {new_struggle_risk})")

        return {
            "quiz_session_id": quiz_session_id,
            "student_id": student_id,
            "topic_id": topic_id,
            "topic_name": topic.name,
            "score_percentage": score_pct,
            "correct_answers": correct_count,
            "total_questions": len(questions),
            "is_passed": is_passed,
            "question_breakdown": breakdown,
            "closed_loop_updates": {
                "quiz_attempt_recorded": True,
                "struggle_risk_level": new_struggle_risk,
                "struggle_probability": struggle_prob,
                "previous_difficulty": attempt_res["previous_difficulty"],
                "new_difficulty": attempt_res["new_difficulty"],
                "adaptive_reason": attempt_res["adaptive_reason"],
                "difficulty_changed": attempt_res["difficulty_changed"],
                "learning_path_updated": True,
                "learning_path_completion_pct": lp_res.get("completion_percentage", 0.0),
            },
            "evaluated_at": datetime.utcnow().isoformat(),
        }


quiz_service = QuizService()
