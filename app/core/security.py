from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.schemas.token import TokenPayload

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Password Hashing Functions ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

# --- JSON Web Token (JWT) Functions ---
def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Creates a new access token.

    :param data: Data to be encoded in the token (e.g., user identifier).
    :param expires_delta: Optional timedelta to set token expiration.
                          If None, uses default from settings.
    :return: The encoded JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> Optional[TokenPayload]:
    """
    Decodes an access token and returns its payload.

    :param token: The JWT token to decode.
    :return: TokenPayload if the token is valid and contains a subject, otherwise None.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        subject: Optional[str] = payload.get("sub")
        if subject is None:
            return None  # Or raise credentials_exception if preferred here
        return TokenPayload(sub=subject)
    except JWTError:
        return None  # Or raise credentials_exception
    except Exception: # Catch any other unexpected errors during decoding
        return None
