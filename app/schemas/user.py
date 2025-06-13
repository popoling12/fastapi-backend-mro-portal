from typing import Optional

from pydantic import BaseModel, EmailStr

# Shared properties
class UserBase(BaseModel):
    email: EmailStr

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update
class UserUpdate(UserBase):
    email: Optional[EmailStr] = None # Allow email updates if desired
    password: Optional[str] = None
    is_active: Optional[bool] = None

# Base model for properties stored in DB, includes id
class UserInDBBase(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True  # Pydantic v2 equivalent of orm_mode

# Properties to return to client (main response model)
class User(UserInDBBase):
    pass

# Properties stored in DB, including hashed_password (for internal use)
class UserInDB(UserInDBBase):
    hashed_password: str
