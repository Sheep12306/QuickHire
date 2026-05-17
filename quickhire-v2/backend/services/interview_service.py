from typing import Optional
from sqlalchemy import desc
from sqlalchemy.orm import Session
from models import InterviewQuestionBank, InterviewAnswer


class InterviewService:

    @staticmethod
    def save_question_bank(
        db: Session,
        user_id: int,
        questions_json: str,
        resume_version_id: Optional[int] = None,
        difficulty: str = "",
        question_types: str = "",
        scope: str = "",
        question_count: int = 0,
    ) -> int:
        bank = InterviewQuestionBank(
            user_id=user_id,
            resume_version_id=resume_version_id,
            questions_json=questions_json,
            difficulty=difficulty,
            question_types=question_types,
            scope=scope,
            question_count=question_count,
        )
        db.add(bank)
        db.commit()
        db.refresh(bank)
        return bank.id

    @staticmethod
    def get_question_banks(db: Session, user_id: int) -> list:
        banks = (
            db.query(InterviewQuestionBank)
            .filter(InterviewQuestionBank.user_id == user_id)
            .order_by(desc(InterviewQuestionBank.created_at))
            .all()
        )
        return [
            {
                "id": b.id,
                "user_id": b.user_id,
                "resume_version_id": b.resume_version_id,
                "questions_json": b.questions_json,
                "difficulty": b.difficulty,
                "question_types": b.question_types,
                "scope": b.scope,
                "question_count": b.question_count,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in banks
        ]

    @staticmethod
    def save_answer(
        db: Session,
        user_id: int,
        question_text: str,
        user_answer: str,
        question_bank_id: Optional[int] = None,
        ai_score: Optional[float] = None,
        ai_feedback: Optional[str] = None,
    ) -> int:
        ans = InterviewAnswer(
            user_id=user_id,
            question_bank_id=question_bank_id,
            question_text=question_text,
            user_answer=user_answer,
            ai_score=ai_score,
            ai_feedback=ai_feedback,
        )
        db.add(ans)
        db.commit()
        db.refresh(ans)
        return ans.id

    @staticmethod
    def get_answers(
        db: Session, user_id: int, question_bank_id: Optional[int] = None
    ) -> list:
        q = db.query(InterviewAnswer).filter(InterviewAnswer.user_id == user_id)
        if question_bank_id:
            q = q.filter(InterviewAnswer.question_bank_id == question_bank_id)
        answers = q.order_by(desc(InterviewAnswer.created_at)).all()
        return [
            {
                "id": a.id,
                "user_id": a.user_id,
                "question_bank_id": a.question_bank_id,
                "question_text": a.question_text,
                "user_answer": a.user_answer,
                "ai_score": a.ai_score,
                "ai_feedback": a.ai_feedback,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in answers
        ]
