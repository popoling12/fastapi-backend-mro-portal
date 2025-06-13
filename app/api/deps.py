from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError # Though decode_access_token handles JWTError internally
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.crud.crud_user import get_user # Assuming crud_user directly
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.token import TokenPayload

# OAuth2PasswordBearer scheme
# The tokenUrl should point to the endpoint that provides the token
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)

# --- Dependency to get DB session ---
def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a SQLAlchemy database session.
    Ensures the session is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Dependency to get current user ---
def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """
    Dependency to get the current authenticated user.
    Decodes the JWT token, retrieves the user from the database.
    Raises HTTPException if authentication fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_access_token(token)

    if not token_data or not token_data.sub:
        raise credentials_exception

    try:
        user_id = int(token_data.sub)
    except ValueError:
        # If 'sub' is not a valid integer (e.g., it was an email, which it shouldn't be if we store ID)
        raise credentials_exception

    user = get_user(db, user_id=user_id)

    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get the current authenticated user and check if they are active.
    Raises HTTPException if the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
