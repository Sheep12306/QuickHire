import json
from sqlalchemy.orm import Session
from models import User, UserSettings
from security import hash_password, verify_password


class UserSettingsService:

    @staticmethod
    def get_preferences(db: Session, user_id: int) -> dict:
        s = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if s and s.preferences:
            try:
                return json.loads(s.preferences)
            except json.JSONDecodeError:
                return {}
        return {}

    @staticmethod
    def save_preferences(db: Session, user_id: int, preferences: dict):
        s = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if s:
            s.preferences = json.dumps(preferences, ensure_ascii=False)
        else:
            s = UserSettings(
                user_id=user_id,
                preferences=json.dumps(preferences, ensure_ascii=False),
            )
            db.add(s)
        db.commit()

    @staticmethod
    def change_password(
        db: Session, user_id: int, old_password: str, new_password: str
    ):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")
        if not verify_password(old_password, user.password_hash):
            raise ValueError("原密码错误")
        user.password_hash = hash_password(new_password)
        db.commit()

    @staticmethod
    def update_profile(
        db: Session,
        user_id: int,
        display_name: str = None,
        email: str = None,
        phone: str = None,
        job_preference: str = None,
        city: str = None,
        target_city: str = None,
    ):
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            if display_name is not None:
                user.display_name = display_name
            if email is not None:
                user.email = email
            if phone is not None:
                user.phone = phone
            if job_preference is not None:
                user.job_preference = job_preference
            if city is not None:
                user.city = city
            if target_city is not None:
                user.target_city = target_city
            db.commit()
