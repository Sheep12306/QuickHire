import json
from datetime import datetime
from typing import Optional

from sqlalchemy import desc
from database import SessionLocal
from models import (
    User,
    ResumeVersion,
    InterviewQuestionBank,
    InterviewAnswer,
    JobApplication,
    ApplicationFeedback,
    UserSettings,
)


class ResumeService:

    @staticmethod
    def save_resume(
        user_id: int,
        original_content: str,
        target_position: str = "",
        optimized_content: Optional[str] = None,
        optimization_style: Optional[str] = None,
        analysis_result: Optional[str] = None,
    ) -> int:
        db = SessionLocal()
        try:
            latest = (
                db.query(ResumeVersion)
                .filter(ResumeVersion.user_id == user_id)
                .order_by(desc(ResumeVersion.version_number))
                .first()
            )
            next_version = (latest.version_number + 1) if latest else 1

            db.query(ResumeVersion).filter(
                ResumeVersion.user_id == user_id, ResumeVersion.is_current == True
            ).update({"is_current": False})

            rv = ResumeVersion(
                user_id=user_id,
                original_content=original_content,
                optimized_content=optimized_content,
                target_position=target_position,
                optimization_style=optimization_style,
                analysis_result=analysis_result,
                version_number=next_version,
                is_current=True,
            )
            db.add(rv)
            db.commit()
            db.refresh(rv)
            return rv.id
        finally:
            db.close()

    @staticmethod
    def update_analysis(user_id: int, analysis_result: str):
        db = SessionLocal()
        try:
            latest = (
                db.query(ResumeVersion)
                .filter(ResumeVersion.user_id == user_id, ResumeVersion.is_current == True)
                .first()
            )
            if latest:
                latest.analysis_result = analysis_result
                db.commit()
        finally:
            db.close()

    @staticmethod
    def get_resume_history(user_id: int) -> list:
        db = SessionLocal()
        try:
            versions = (
                db.query(ResumeVersion)
                .filter(ResumeVersion.user_id == user_id)
                .order_by(desc(ResumeVersion.created_at))
                .all()
            )
            return [
                {
                    "id": v.id,
                    "version_number": v.version_number,
                    "original_content": v.original_content,
                    "optimized_content": v.optimized_content,
                    "target_position": v.target_position,
                    "optimization_style": v.optimization_style,
                    "analysis_result": v.analysis_result,
                    "is_current": v.is_current,
                    "created_at": v.created_at.isoformat() if v.created_at else None,
                }
                for v in versions
            ]
        finally:
            db.close()

    @staticmethod
    def get_latest_resume(user_id: int) -> Optional[dict]:
        db = SessionLocal()
        try:
            v = (
                db.query(ResumeVersion)
                .filter(ResumeVersion.user_id == user_id, ResumeVersion.is_current == True)
                .first()
            )
            if not v:
                return None
            return {
                "id": v.id,
                "version_number": v.version_number,
                "original_content": v.original_content,
                "optimized_content": v.optimized_content,
                "target_position": v.target_position,
                "optimization_style": v.optimization_style,
                "analysis_result": v.analysis_result,
                "is_current": v.is_current,
                "created_at": v.created_at.isoformat() if v.created_at else None,
            }
        finally:
            db.close()

    @staticmethod
    def set_current_version(user_id: int, resume_id: int):
        db = SessionLocal()
        try:
            db.query(ResumeVersion).filter(
                ResumeVersion.user_id == user_id, ResumeVersion.is_current == True
            ).update({"is_current": False})
            db.query(ResumeVersion).filter(
                ResumeVersion.id == resume_id, ResumeVersion.user_id == user_id
            ).update({"is_current": True})
            db.commit()
        finally:
            db.close()


class InterviewService:

    @staticmethod
    def save_question_bank(
        user_id: int,
        questions_json: str,
        resume_version_id: Optional[int] = None,
        difficulty: str = "",
        question_types: str = "",
        scope: str = "",
        question_count: int = 0,
    ) -> int:
        db = SessionLocal()
        try:
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
        finally:
            db.close()

    @staticmethod
    def get_question_banks(user_id: int) -> list:
        db = SessionLocal()
        try:
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
        finally:
            db.close()

    @staticmethod
    def save_answer(
        user_id: int,
        question_text: str,
        user_answer: str,
        question_bank_id: Optional[int] = None,
        ai_score: Optional[float] = None,
        ai_feedback: Optional[str] = None,
    ) -> int:
        db = SessionLocal()
        try:
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
        finally:
            db.close()

    @staticmethod
    def get_answers(user_id: int, question_bank_id: Optional[int] = None) -> list:
        db = SessionLocal()
        try:
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
        finally:
            db.close()


class ApplicationService:

    @staticmethod
    def add_application(
        user_id: int,
        company: str,
        position: str,
        status: str = "applied",
        notes: str = "",
    ) -> int:
        db = SessionLocal()
        try:
            app = JobApplication(
                user_id=user_id,
                company_name=company,
                position=position,
                status=status,
                notes=notes,
            )
            db.add(app)
            db.commit()
            db.refresh(app)
            return app.id
        finally:
            db.close()

    @staticmethod
    def update_status(application_id: int, user_id: int, status: str):
        db = SessionLocal()
        try:
            app = (
                db.query(JobApplication)
                .filter(
                    JobApplication.id == application_id,
                    JobApplication.user_id == user_id,
                )
                .first()
            )
            if app:
                app.status = status
                db.commit()
        finally:
            db.close()

    @staticmethod
    def get_applications(user_id: int, status_filter: Optional[str] = None) -> list:
        db = SessionLocal()
        try:
            q = db.query(JobApplication).filter(JobApplication.user_id == user_id)
            if status_filter:
                q = q.filter(JobApplication.status == status_filter)
            apps = q.order_by(desc(JobApplication.created_at)).all()
            return [
                {
                    "id": a.id,
                    "company_name": a.company_name,
                    "position": a.position,
                    "status": a.status,
                    "applied_at": a.applied_at.isoformat() if a.applied_at else None,
                    "notes": a.notes,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in apps
            ]
        finally:
            db.close()

    @staticmethod
    def add_feedback(application_id: int, feedback_type: str, content: str) -> int:
        db = SessionLocal()
        try:
            fb = ApplicationFeedback(
                application_id=application_id,
                feedback_type=feedback_type,
                content=content,
            )
            db.add(fb)
            db.commit()
            db.refresh(fb)
            return fb.id
        finally:
            db.close()

    @staticmethod
    def get_stats(user_id: int) -> dict:
        db = SessionLocal()
        try:
            apps = (
                db.query(JobApplication)
                .filter(JobApplication.user_id == user_id)
                .all()
            )
            total = len(apps)
            status_counts = {}
            for a in apps:
                status_counts[a.status] = status_counts.get(a.status, 0) + 1
            interview_count = status_counts.get("interview", 0) + status_counts.get("offer", 0) + status_counts.get("accepted", 0)
            offer_count = status_counts.get("offer", 0) + status_counts.get("accepted", 0)
            return {
                "total": total,
                "status_counts": status_counts,
                "interview_rate": round(interview_count / total * 100, 1) if total > 0 else 0,
                "offer_rate": round(offer_count / total * 100, 1) if total > 0 else 0,
            }
        finally:
            db.close()


class UserSettingsService:

    @staticmethod
    def get_preferences(user_id: int) -> dict:
        db = SessionLocal()
        try:
            s = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            if s and s.preferences:
                try:
                    return json.loads(s.preferences)
                except json.JSONDecodeError:
                    return {}
            return {}
        finally:
            db.close()

    @staticmethod
    def save_preferences(user_id: int, preferences: dict):
        db = SessionLocal()
        try:
            s = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            if s:
                s.preferences = json.dumps(preferences, ensure_ascii=False)
            else:
                s = UserSettings(user_id=user_id, preferences=json.dumps(preferences, ensure_ascii=False))
                db.add(s)
            db.commit()
        finally:
            db.close()

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str):
        from auth_service import AuthService

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("用户不存在")
            if not AuthService.verify_password(old_password, user.password_hash):
                raise ValueError("原密码错误")
            user.password_hash = AuthService.hash_password(new_password)
            db.commit()
        finally:
            db.close()

    @staticmethod
    def update_profile(user_id: int, display_name: str = None, email: str = None, phone: str = None):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                if display_name is not None:
                    user.display_name = display_name
                if email is not None:
                    user.email = email
                if phone is not None:
                    user.phone = phone
                db.commit()
        finally:
            db.close()
