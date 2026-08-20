"""Personalization Service: Adaptive difficulty, learning path generation, and profile updates."""

import json
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from collections import deque
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db.models import User, StudentProfile, Topic, QuizAttempt, LearningPath


class PersonalizationService:
    """Service handling adaptive difficulty scaling, topological learning paths, and quiz attempt updates."""

    def compute_adaptive_difficulty(
        self, current_difficulty: str, attempts_history: List[Dict[str, Any]]
    ) -> Tuple[str, str]:
        """
        Adapt student target difficulty level based on recent performance and trend.
        Rules:
        - If recent avg >= 85% and score trend > +3 pts -> Shift UP (easy -> medium -> hard)
        - If recent avg < 60% or score trend < -5 pts -> Shift DOWN (hard -> medium -> easy)
        - Otherwise -> Keep CURRENT difficulty
        """
        diff_levels = ["easy", "medium", "hard"]
        curr_idx = diff_levels.index(current_difficulty.lower()) if current_difficulty.lower() in diff_levels else 1

        if not attempts_history or len(attempts_history) < 2:
            return diff_levels[curr_idx], "Insufficient attempt history; maintaining baseline difficulty level."

        scores = [a["score"] for a in attempts_history]
        recent_avg = float(np.mean(scores[-3:]))
        overall_avg = float(np.mean(scores))
        trend = recent_avg - overall_avg

        if recent_avg >= 85.0 and trend >= -2.0 and curr_idx < 2:
            new_diff = diff_levels[curr_idx + 1]
            return new_diff, f"Excellent recent average ({recent_avg:.1f}%)! Difficulty automatically scaled UP from '{diff_levels[curr_idx]}' to '{new_diff}'."

        if (recent_avg < 60.0 or trend < -5.0) and curr_idx > 0:
            new_diff = diff_levels[curr_idx - 1]
            return new_diff, f"Recent score drop detected (avg {recent_avg:.1f}%, trend {trend:.1f} pts). Difficulty adjusted DOWN from '{diff_levels[curr_idx]}' to '{new_diff}' to reinforce core concepts."

        return diff_levels[curr_idx], f"Performance stable (recent avg {recent_avg:.1f}%). Maintaining '{diff_levels[curr_idx]}' difficulty level."

    def generate_learning_path(
        self, db: Session, student_id: int, target_subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a topologically sorted DAG learning path for a student.
        Prerequisite topics come before advanced topics.
        """
        user = db.query(User).filter(User.id == student_id).first()
        if not user:
            raise ValueError(f"Student ID {student_id} not found.")

        profile = db.query(StudentProfile).filter(StudentProfile.user_id == student_id).first()
        current_diff = profile.preferred_difficulty if profile else "medium"

        # Load topics from DB
        query = db.query(Topic)
        if target_subject and target_subject.strip():
            query = query.filter(Topic.subject.ilike(f"%{target_subject.strip()}%"))
        db_topics = query.all()
        if not db_topics:
            db_topics = db.query(Topic).all()

        topic_map = {t.id: t for t in db_topics}
        topic_ids = set(topic_map.keys())

        # Load student attempts to check mastery
        attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).all()
        attempts_by_topic = {}
        for a in attempts:
            attempts_by_topic.setdefault(a.topic_id, []).append(a.score)

        # Compute topological sort (Kahn's algorithm) for prerequisites
        in_degree = {t_id: 0 for t_id in topic_ids}
        adj = {t_id: [] for t_id in topic_ids}

        for t_id, topic in topic_map.items():
            prereqs = topic.prerequisites or []
            if isinstance(prereqs, str):
                try:
                    prereqs = json.loads(prereqs)
                except Exception:
                    prereqs = []
            if not isinstance(prereqs, list):
                prereqs = []

            for p in prereqs:
                if p in topic_ids:
                    adj[p].append(t_id)
                    in_degree[t_id] += 1

        queue = deque([t_id for t_id in topic_ids if in_degree[t_id] == 0])
        sorted_topic_ids = []
        while queue:
            curr = queue.popleft()
            sorted_topic_ids.append(curr)
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Fallback for remaining topics if any cycle or unreached
        for t_id in topic_ids:
            if t_id not in sorted_topic_ids:
                sorted_topic_ids.append(t_id)

        # Build step-by-step learning path
        steps = []
        completed_count = 0
        total_est_minutes = 0

        for step_no, t_id in enumerate(sorted_topic_ids, 1):
            t = topic_map[t_id]
            scores = attempts_by_topic.get(t_id, [])
            best_score = max(scores) if scores else None
            is_completed = best_score is not None and best_score >= 80.0
            if is_completed:
                completed_count += 1

            # Estimate completion time based on difficulty (easy: 30m, medium: 45m, hard: 60m)
            est_mins = 30 if t.difficulty == "easy" else (45 if t.difficulty == "medium" else 60)
            total_est_minutes += est_mins

            t_prereqs = t.prerequisites or []
            if isinstance(t_prereqs, str):
                try:
                    t_prereqs = json.loads(t_prereqs)
                except Exception:
                    t_prereqs = []
            if not isinstance(t_prereqs, list):
                t_prereqs = []

            steps.append({
                "step_number": step_no,
                "topic_id": t.id,
                "subject": t.subject,
                "topic_name": t.name,
                "difficulty": t.difficulty,
                "prerequisites": [topic_map[p].name for p in t_prereqs if p in topic_map],
                "status": "completed" if is_completed else ("in_progress" if scores else "locked"),
                "best_score": best_score,
                "estimated_minutes": est_mins,
            })

        # Save or update learning path in database
        db.query(LearningPath).filter(LearningPath.student_id == student_id).delete()

        lp_db = LearningPath(
            student_id=student_id,
            ordered_topics={"steps": steps, "completed_count": completed_count, "total_steps": len(steps), "target_goal": target_subject or (profile.goals if profile else "Master Curriculum")},
            status="active",
            created_at=datetime.utcnow(),
        )
        db.add(lp_db)
        db.commit()

        logger.info(f"Generated learning path with {len(steps)} steps for student {student_id}")

        return {
            "student_id": student_id,
            "student_name": user.name,
            "target_goal": target_subject or (profile.goals if profile else "Master Curriculum"),
            "current_preferred_difficulty": current_diff,
            "total_steps": len(steps),
            "completed_steps": completed_count,
            "completion_percentage": round((completed_count / len(steps) * 100), 1) if steps else 0.0,
            "estimated_total_hours": round(total_est_minutes / 60.0, 1),
            "steps": steps,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def process_quiz_attempt(
        self, db: Session, student_id: int, topic_id: int, score: float, time_spent: int
    ) -> Dict[str, Any]:
        """Record quiz attempt, execute adaptive difficulty adjustment, and update student profile."""
        user = db.query(User).filter(User.id == student_id).first()
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not user:
            raise ValueError(f"Student ID {student_id} not found.")
        if not topic:
            raise ValueError(f"Topic ID {topic_id} not found.")

        # Count prior attempts on this topic
        prior_attempts = db.query(QuizAttempt).filter(
            QuizAttempt.student_id == student_id, QuizAttempt.topic_id == topic_id
        ).count()

        attempt = QuizAttempt(
            student_id=student_id,
            topic_id=topic_id,
            score=score,
            time_spent=time_spent,
            attempts=prior_attempts + 1,
            timestamp=datetime.utcnow(),
        )
        db.add(attempt)
        db.commit()

        # Load overall student history for adaptive difficulty check
        all_attempts = db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).all()
        history_dicts = [{"score": a.score} for a in all_attempts]

        profile = db.query(StudentProfile).filter(StudentProfile.user_id == student_id).first()
        current_diff = profile.preferred_difficulty if profile else "medium"

        new_diff, diff_reason = self.compute_adaptive_difficulty(current_diff, history_dicts)

        # Update profile if difficulty changed
        if profile and new_diff != profile.preferred_difficulty:
            profile.preferred_difficulty = new_diff
            db.commit()
            logger.info(f"Student {student_id} preferred difficulty updated to {new_diff}")

        return {
            "student_id": student_id,
            "topic_id": topic_id,
            "topic_name": topic.name,
            "score": score,
            "attempt_number": prior_attempts + 1,
            "previous_difficulty": current_diff,
            "new_difficulty": new_diff,
            "adaptive_reason": diff_reason,
            "difficulty_changed": new_diff != current_diff,
            "recorded_at": datetime.utcnow().isoformat(),
        }


personalization_service = PersonalizationService()
