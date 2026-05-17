import bcrypt
import re
from datetime import datetime, timedelta
import streamlit as st
from models import User
from database import SessionLocal
from config import BCRYPT_ROUNDS, MIN_PASSWORD_LENGTH, SESSION_EXPIRY_HOURS


class AuthError(Exception):
    pass


class AuthService:

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=BCRYPT_ROUNDS),
        ).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed.encode("utf-8"),
        )

    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        pattern = r"^1[3-9]\d{9}$"
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_password(password: str) -> tuple:
        if len(password) < MIN_PASSWORD_LENGTH:
            return False, f"密码长度不能少于{MIN_PASSWORD_LENGTH}位"
        return True, ""

    @staticmethod
    def register(email: str, phone: str, password: str, display_name: str = "") -> dict:
        if not email and not phone:
            raise AuthError("请至少提供邮箱或手机号")
        if email and not AuthService.validate_email(email):
            raise AuthError("邮箱格式不正确")
        if phone and not AuthService.validate_phone(phone):
            raise AuthError("手机号格式不正确")
        valid, msg = AuthService.validate_password(password)
        if not valid:
            raise AuthError(msg)

        db = SessionLocal()
        try:
            if email:
                existing = db.query(User).filter(User.email == email).first()
                if existing:
                    raise AuthError("该邮箱已被注册")
            if phone:
                existing = db.query(User).filter(User.phone == phone).first()
                if existing:
                    raise AuthError("该手机号已被注册")

            user = User(
                email=email or None,
                phone=phone or None,
                password_hash=AuthService.hash_password(password),
                display_name=display_name or email or phone or "用户",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            # Extract data before session closes
            return {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "display_name": user.display_name,
            }
        finally:
            db.close()

    @staticmethod
    def login(credential: str, password: str) -> dict:
        if not credential or not password:
            raise AuthError("请输入账号和密码")

        db = SessionLocal()
        try:
            user = db.query(User).filter(
                (User.email == credential) | (User.phone == credential)
            ).first()

            if not user:
                raise AuthError("账号不存在")
            if not user.is_active:
                raise AuthError("账号已被停用")
            if not AuthService.verify_password(password, user.password_hash):
                raise AuthError("密码错误")

            user.last_login_at = datetime.utcnow()
            db.commit()
            # Extract data before session closes
            return {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "display_name": user.display_name,
            }
        finally:
            db.close()

    @staticmethod
    def set_session(user: dict):
        st.session_state.user_id = user["id"]
        st.session_state.user_email = user.get("email")
        st.session_state.user_phone = user.get("phone")
        st.session_state.display_name = user.get("display_name")
        st.session_state.login_time = datetime.utcnow().isoformat()

    @staticmethod
    def clear_session():
        for key in ["user_id", "user_email", "user_phone", "display_name", "login_time"]:
            st.session_state.pop(key, None)

    @staticmethod
    def is_logged_in() -> bool:
        return bool(st.session_state.get("user_id"))

    @staticmethod
    def check_session_expiry() -> bool:
        login_time_str = st.session_state.get("login_time")
        if not login_time_str:
            return False
        login_time = datetime.fromisoformat(login_time_str)
        expiry = login_time + timedelta(hours=SESSION_EXPIRY_HOURS)
        if datetime.utcnow() > expiry:
            AuthService.clear_session()
            return False
        return True
