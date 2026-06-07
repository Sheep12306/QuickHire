import smtplib
import random
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
from models import VerificationCode


CODE_EXPIRE_MINUTES = 5
RATE_LIMIT_SECONDS = 60


class EmailError(Exception):
    pass


class EmailService:

    @staticmethod
    def send_verification_code(db: Session, email: str):
        if not SMTP_USER or not SMTP_PASSWORD:
            raise EmailError("邮件服务未配置，请联系管理员")

        # Rate limit: check last send time
        cutoff = datetime.utcnow() - timedelta(seconds=RATE_LIMIT_SECONDS)
        recent = (
            db.query(VerificationCode)
            .filter(
                VerificationCode.email == email,
                VerificationCode.created_at >= cutoff,
            )
            .first()
        )
        if recent:
            raise EmailError("验证码已发送，请60秒后重试")

        # Generate 6-digit code
        code = f"{random.randint(100000, 999999)}"
        expires_at = datetime.utcnow() + timedelta(minutes=CODE_EXPIRE_MINUTES)

        # Send email
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = email
        msg["Subject"] = "QuickHire 登录验证码"

        body = f"""您的验证码是：{code}

验证码 {CODE_EXPIRE_MINUTES} 分钟内有效，请勿泄露给他人。

如非本人操作，请忽略此邮件。

QuickHire 团队"""

        msg.attach(MIMEText(body, "plain", "utf-8"))

        try:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, email, msg.as_string())
            server.quit()
        except Exception as e:
            raise EmailError(f"邮件发送失败: {str(e)}")

        # Save to DB
        record = VerificationCode(email=email, code=code, expires_at=expires_at)
        db.add(record)
        db.commit()

    @staticmethod
    def verify_code(db: Session, email: str, code: str) -> bool:
        record = (
            db.query(VerificationCode)
            .filter(
                VerificationCode.email == email,
                VerificationCode.code == code,
                VerificationCode.used == False,
            )
            .order_by(VerificationCode.created_at.desc())
            .first()
        )
        if not record:
            return False
        if datetime.utcnow() > record.expires_at:
            return False
        # Mark as used
        record.used = True
        db.commit()
        return True
