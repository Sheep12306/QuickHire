from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from security import verify_token

security_scheme = HTTPBearer()


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
    return user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None
    return get_current_user(credentials, db)
