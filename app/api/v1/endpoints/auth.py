from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud.crud_user import authenticate_user, get_user_by_email
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserPublic

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/access-token")

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": security.create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token validity and return current user info
    """
    return current_user

@router.post("/password-recovery/{email}")
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery (placeholder implementation)
    In production, this would send a recovery email
    """
    user = get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )
    
    # In production, generate password reset token and send email
    # For now, return success message
    return {"message": "Password recovery email sent"}

@router.post("/reset-password/")
def reset_password(
    token: str, new_password: str, db: Session = Depends(deps.get_db)
) -> Any:
    """
    Reset password (placeholder implementation)
    In production, this would verify the reset token
    """
    # In production, decode and verify reset token
    # For now, return placeholder message
    return {"message": "Password has been reset successfully"}