from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse, SendCodeRequest, VerifyCodeLoginRequest
from dependencies import get_db, get_current_user, get_current_user_allow_pw_change
from services.auth_service import AuthService, AuthError
from services.email_service import EmailService, EmailError
from security import create_access_token
from models import User
import logging, traceback

router = APIRouter()


@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = AuthService.register(
            db=db,
            email=req.email.strip(),
            phone=req.phone.strip(),
            password=req.password,
            display_name=req.display_name.strip(),
        )
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logging.error(f"Unexpected error in /register: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = AuthService.login(db=db, credential=req.credential, password=req.password)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logging.error(f"Unexpected error in /login: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/guest-login", response_model=TokenResponse)
def guest_login(db: Session = Depends(get_db)):
    try:
        user = AuthService.create_guest(db)
    except Exception as e:
        logging.error(f"Unexpected error in /guest-login: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/send-code")
def send_code(req: SendCodeRequest, db: Session = Depends(get_db)):
    if not AuthService.validate_email(req.email):
        raise HTTPException(status_code=400, detail="邮箱格式不正确")
    try:
        EmailService.send_verification_code(db, req.email)
    except EmailError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"ok": True, "message": "验证码已发送"}


@router.post("/verify-code-login", response_model=TokenResponse)
def verify_code_login(req: VerifyCodeLoginRequest, db: Session = Depends(get_db)):
    if not AuthService.validate_email(req.email):
        raise HTTPException(status_code=400, detail="邮箱格式不正确")
    if not EmailService.verify_code(db, req.email, req.code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    # Find or create user
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        user = User(
            email=req.email,
            password_hash="",  # verification-code-only users have no password
            display_name=req.email.split("@")[0],
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被停用")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user_allow_pw_change)):
    return UserResponse.model_validate(current_user)
