from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate

# --- User CRUD Functions ---

def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieves a user by their ID.

    :param db: The database session.
    :param user_id: The ID of the user to retrieve.
    :return: The User object if found, otherwise None.
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieves a user by their email address.

    :param db: The database session.
    :param email: The email address of the user to retrieve.
    :return: The User object if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    """
    Creates a new user in the database.

    :param db: The database session.
    :param user: The UserCreate schema containing user details (email, password).
    :return: The created User object.
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password
        # is_active defaults to True in the model
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Placeholder for future CRUD operations:
# def update_user(...):
#     pass

# def delete_user(...):
#     pass
