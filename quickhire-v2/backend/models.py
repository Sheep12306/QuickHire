from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    resume_versions = relationship("ResumeVersion", back_populates="user", lazy="dynamic")
    question_banks = relationship("InterviewQuestionBank", back_populates="user", lazy="dynamic")
    answers = relationship("InterviewAnswer", back_populates="user", lazy="dynamic")
    applications = relationship("JobApplication", back_populates="user", lazy="dynamic")


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_content = Column(Text, nullable=False)
    optimized_content = Column(Text, nullable=True)
    target_position = Column(String(200), nullable=True)
    optimization_style = Column(String(50), nullable=True)
    analysis_result = Column(Text, nullable=True)
    version_number = Column(Integer, nullable=False, default=1)
    is_current = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="resume_versions")


class InterviewQuestionBank(Base):
    __tablename__ = "interview_question_banks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_version_id = Column(Integer, ForeignKey("resume_versions.id"), nullable=True)
    questions_json = Column(Text, nullable=False)
    difficulty = Column(String(20), nullable=True)
    question_types = Column(String(100), nullable=True)
    scope = Column(String(20), nullable=True)
    question_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="question_banks")


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_bank_id = Column(Integer, ForeignKey("interview_question_banks.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=False)
    ai_score = Column(Float, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="answers")


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_name = Column(String(200), nullable=False)
    position = Column(String(200), nullable=False)
    status = Column(String(50), default="applied")
    applied_at = Column(DateTime, server_default=func.now())
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="applications")
    feedbacks = relationship("ApplicationFeedback", back_populates="application", lazy="dynamic")


class ApplicationFeedback(Base):
    __tablename__ = "application_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=False)
    feedback_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    application = relationship("JobApplication", back_populates="feedbacks")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    preferences = Column(Text, default="{}")


class PracticeQuestion(Base):
    __tablename__ = "practice_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    position = Column(String(200), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    answer_guide = Column(Text, nullable=True)
    question_type = Column(String(50), nullable=True)
    difficulty = Column(String(20), nullable=True)
    tags = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class QuestionFavorite(Base):
    __tablename__ = "question_favorites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("practice_questions.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
