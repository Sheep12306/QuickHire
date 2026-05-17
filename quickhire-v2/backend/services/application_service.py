from typing import Optional
from sqlalchemy import desc
from sqlalchemy.orm import Session
from models import JobApplication, ApplicationFeedback


class ApplicationService:

    @staticmethod
    def add_application(
        db: Session,
        user_id: int,
        company: str,
        position: str,
        status: str = "applied",
        notes: str = "",
    ) -> int:
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

    @staticmethod
    def update_status(db: Session, application_id: int, user_id: int, status: str):
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

    @staticmethod
    def get_applications(
        db: Session, user_id: int, status_filter: Optional[str] = None
    ) -> list:
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

    @staticmethod
    def add_feedback(db: Session, application_id: int, feedback_type: str, content: str) -> int:
        fb = ApplicationFeedback(
            application_id=application_id,
            feedback_type=feedback_type,
            content=content,
        )
        db.add(fb)
        db.commit()
        db.refresh(fb)
        return fb.id

    @staticmethod
    def get_stats(db: Session, user_id: int) -> dict:
        apps = (
            db.query(JobApplication)
            .filter(JobApplication.user_id == user_id)
            .all()
        )
        total = len(apps)
        status_counts = {}
        for a in apps:
            status_counts[a.status] = status_counts.get(a.status, 0) + 1
        interview_count = (
            status_counts.get("interview", 0)
            + status_counts.get("offer", 0)
            + status_counts.get("accepted", 0)
        )
        offer_count = status_counts.get("offer", 0) + status_counts.get("accepted", 0)
        return {
            "total": total,
            "status_counts": status_counts,
            "interview_rate": round(interview_count / total * 100, 1) if total > 0 else 0,
            "offer_rate": round(offer_count / total * 100, 1) if total > 0 else 0,
        }
