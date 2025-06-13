from typing import Optional

from pydantic import BaseModel, EmailStr

# Schema for token response
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for token payload (data encoded in the JWT)
class TokenPayload(BaseModel):
    sub: Optional[str] = None  # Subject of the token (e.g., user ID or email)

# Schema for the data expected from the token request form (login)
# FastAPI's OAuth2PasswordRequestForm typically expects 'username' and 'password'.
# We use EmailStr for username to align with our User model.
class TokenRequestForm(BaseModel):
    username: EmailStr
    password: str
    # scope: str = "" # Optional: if using scopes
    # client_id: Optional[str] = None # Optional: for OAuth2 client credentials flow
    # client_secret: Optional[str] = None # Optional: for OAuth2 client credentials flow
