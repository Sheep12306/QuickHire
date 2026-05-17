from typing import Optional
from sqlalchemy import desc
from sqlalchemy.orm import Session
from models import ResumeVersion


class ResumeService:

    @staticmethod
    def save_resume(
        db: Session,
        user_id: int,
        original_content: str,
        target_position: str = "",
        optimized_content: Optional[str] = None,
        optimization_style: Optional[str] = None,
        analysis_result: Optional[str] = None,
    ) -> int:
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

    @staticmethod
    def update_analysis(db: Session, user_id: int, analysis_result: str):
        latest = (
            db.query(ResumeVersion)
            .filter(ResumeVersion.user_id == user_id, ResumeVersion.is_current == True)
            .first()
        )
        if latest:
            latest.analysis_result = analysis_result
            db.commit()

    @staticmethod
    def get_resume_history(db: Session, user_id: int) -> list:
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

    @staticmethod
    def get_latest_resume(db: Session, user_id: int) -> Optional[dict]:
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

    @staticmethod
    def set_current_version(db: Session, user_id: int, resume_id: int):
        db.query(ResumeVersion).filter(
            ResumeVersion.user_id == user_id, ResumeVersion.is_current == True
        ).update({"is_current": False})
        db.query(ResumeVersion).filter(
            ResumeVersion.id == resume_id, ResumeVersion.user_id == user_id
        ).update({"is_current": True})
        db.commit()
