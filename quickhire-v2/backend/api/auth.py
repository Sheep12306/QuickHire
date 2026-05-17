from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from dependencies import get_db, get_current_user
from services.auth_service import AuthService, AuthError
from security import create_access_token
from models import User

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

    token = create_access_token({"sub": str(user.id)})
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

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
