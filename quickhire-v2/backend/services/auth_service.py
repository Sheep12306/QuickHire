import re
from datetime import datetime
from sqlalchemy.orm import Session
from models import User
from security import hash_password, verify_password
from config import MIN_PASSWORD_LENGTH


class AuthError(Exception):
    pass


class AuthService:

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
    def register(
        db: Session,
        email: str,
        phone: str,
        password: str,
        display_name: str = "",
    ) -> User:
        if not email and not phone:
            raise AuthError("请至少提供邮箱或手机号")
        if email and not AuthService.validate_email(email):
            raise AuthError("邮箱格式不正确")
        if phone and not AuthService.validate_phone(phone):
            raise AuthError("手机号格式不正确")
        valid, msg = AuthService.validate_password(password)
        if not valid:
            raise AuthError(msg)

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
            password_hash=hash_password(password),
            display_name=display_name or email or phone or "用户",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, credential: str, password: str) -> User:
        if not credential or not password:
            raise AuthError("请输入账号和密码")

        user = db.query(User).filter(
            (User.email == credential) | (User.phone == credential)
        ).first()

        if not user:
            raise AuthError("账号不存在")
        if not user.is_active:
            raise AuthError("账号已被停用")
        if not verify_password(password, user.password_hash):
            raise AuthError("密码错误")

        user.last_login_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
