"""SQLAlchemy ORM models for EduSense AI."""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
import enum
from app.db.session import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    role = Column(String(20), default=UserRole.STUDENT.value, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user")
    learning_events = relationship("LearningEvent", back_populates="user")
    feedbacks = relationship("StudentFeedback", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    learning_paths = relationship("LearningPath", back_populates="user")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    education_level = Column(String(50), nullable=True)  # e.g., "High School", "Undergraduate", "Graduate"
    goals = Column(Text, nullable=True)                  # e.g., "Master Data Structures & ML"
    preferred_difficulty = Column(String(20), default="medium") # "easy", "medium", "hard"
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(100), nullable=False, index=True) # e.g., "Machine Learning", "Mathematics"
    name = Column(String(150), nullable=False, index=True)    # e.g., "Logistic Regression"
    difficulty = Column(String(20), default="medium")          # "easy", "medium", "hard"
    prerequisites = Column(JSON, default=list)                 # List of topic IDs or names

    resources = relationship("LearningResource", back_populates="topic")
    quiz_attempts = relationship("QuizAttempt", back_populates="topic")
    learning_events = relationship("LearningEvent", back_populates="topic")
    feedbacks = relationship("StudentFeedback", back_populates="topic")
    recommendations = relationship("Recommendation", back_populates="topic")


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    type = Column(String(50), nullable=False)     # "article", "video", "exercise", "quiz"
    title = Column(String(200), nullable=False)
    url_or_path = Column(String(500), nullable=True)
    difficulty = Column(String(20), default="medium")

    topic = relationship("Topic", back_populates="resources")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    score = Column(Float, nullable=False)          # Percentage or points 0-100
    time_spent = Column(Integer, nullable=False)   # Duration in seconds
    attempts = Column(Integer, default=1)           # Attempt number
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="quiz_attempts")
    topic = relationship("Topic", back_populates="quiz_attempts")


class LearningEvent(Base):
    __tablename__ = "learning_events"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    event_type = Column(String(50), nullable=False) # "view_resource", "complete_lesson", "search"
    duration = Column(Integer, default=0)            # Seconds spent
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="learning_events")
    topic = relationship("Topic", back_populates="learning_events")


class StudentFeedback(Base):
    __tablename__ = "student_feedback"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="feedbacks")
    topic = relationship("Topic", back_populates="feedbacks")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    score = Column(Float, nullable=False)
    reason = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="recommendations")
    topic = relationship("Topic", back_populates="recommendations")


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ordered_topics = Column(JSON, nullable=False) # List of dicts or topic IDs
    status = Column(String(20), default="active") # "active", "completed", "archived"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="learning_paths")


class ModelRun(Base):
    __tablename__ = "model_runs"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False) # e.g., "struggle_predictor_rf"
    version = Column(String(50), nullable=False)     # e.g., "v1.0.0"
    metrics = Column(JSON, nullable=False)           # {"accuracy": 0.85, "recall": 0.88, ...}
    trained_at = Column(DateTime, default=datetime.utcnow, nullable=False)
