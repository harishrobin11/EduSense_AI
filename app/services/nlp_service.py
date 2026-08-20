"""NLP Service connecting DB student_feedback table and NLPFeedbackAnalyzer."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import Counter
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db.models import User, Topic, StudentFeedback
from ml.nlp.feedback_analyzer import nlp_analyzer


class NLPService:
    """Service handling feedback text processing, sentiment scoring, and database analytics."""

    def process_and_save_feedback(
        self,
        db: Session,
        student_id: int,
        text: str,
        topic_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Analyze text feedback, extract themes, save to DB, and return structured result."""
        user = db.query(User).filter(User.id == student_id).first()
        if not user:
            raise ValueError(f"Student ID {student_id} not found.")

        topic_name = None
        if topic_id:
            topic = db.query(Topic).filter(Topic.id == topic_id).first()
            if topic:
                topic_name = topic.name

        # Perform NLP analysis
        cleaned_text = nlp_analyzer.clean_text(text)
        sentiment_score, sentiment_label = nlp_analyzer.analyze_sentiment(text)
        extracted_keywords = nlp_analyzer.extract_keywords_and_themes(text, top_n=5)

        # Save into student_feedback table
        feedback_db = StudentFeedback(
            student_id=student_id,
            topic_id=topic_id,
            text=text,
            timestamp=datetime.utcnow(),
        )
        db.add(feedback_db)
        db.commit()

        logger.info(f"Recorded feedback ID {feedback_db.id} for student {student_id} (Sentiment: {sentiment_label})")

        return {
            "feedback_id": feedback_db.id,
            "student_id": student_id,
            "student_name": user.name,
            "topic_id": topic_id,
            "topic_name": topic_name,
            "original_text": text,
            "cleaned_text": cleaned_text,
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "keywords_extracted": extracted_keywords,
            "submitted_at": datetime.utcnow().isoformat(),
        }

    def get_student_sentiment_summary(
        self, db: Session, student_id: int
    ) -> Dict[str, Any]:
        """Aggregate student sentiment profile, sentiment distribution, and recurring themes."""
        user = db.query(User).filter(User.id == student_id).first()
        if not user:
            raise ValueError(f"Student ID {student_id} not found.")

        feedbacks = db.query(StudentFeedback).filter(StudentFeedback.student_id == student_id).all()
        if not feedbacks:
            return {
                "student_id": student_id,
                "student_name": user.name,
                "total_feedback_count": 0,
                "average_sentiment_score": 0.0,
                "overall_sentiment_status": "neutral",
                "sentiment_breakdown": {"positive": 0, "neutral": 0, "negative": 0},
                "recurring_themes": [],
                "recent_feedbacks": [],
            }

        scores = []
        labels = []
        all_keywords = []
        recent_feedbacks = []

        for f in feedbacks:
            score, label = nlp_analyzer.analyze_sentiment(f.text)
            keywords = nlp_analyzer.extract_keywords_and_themes(f.text)

            scores.append(score)
            labels.append(label)
            all_keywords.extend(keywords)

            recent_feedbacks.append({
                "feedback_id": f.id,
                "topic_id": f.topic_id,
                "text": f.text,
                "sentiment_score": score,
                "sentiment_label": label,
                "timestamp": f.timestamp.isoformat() if f.timestamp else datetime.utcnow().isoformat(),
            })

        avg_score = round(sum(scores) / len(scores), 2)
        if avg_score >= 0.15:
            overall_status = "positive"
        elif avg_score <= -0.15:
            overall_status = "negative"
        else:
            overall_status = "neutral"

        counts = Counter(labels)
        theme_counts = Counter(all_keywords)
        top_recurring_themes = [kw for kw, _ in theme_counts.most_common(5)]

        return {
            "student_id": student_id,
            "student_name": user.name,
            "total_feedback_count": len(feedbacks),
            "average_sentiment_score": avg_score,
            "overall_sentiment_status": overall_status,
            "sentiment_breakdown": {
                "positive": counts.get("positive", 0),
                "neutral": counts.get("neutral", 0),
                "negative": counts.get("negative", 0),
            },
            "recurring_themes": top_recurring_themes,
            "recent_feedbacks": sorted(recent_feedbacks, key=lambda x: x["timestamp"], reverse=True)[:10],
        }


nlp_service = NLPService()
