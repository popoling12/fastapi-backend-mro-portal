from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.security import get_password_hash
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserCreate, UserUpdate, UserRoleUpdate

# --- User CRUD Functions ---

def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    Retrieves a user by their ID.
    """
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieves a user by their email address.
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Retrieves a user by their username.
    """
    return db.query(User).filter(User.username == username).first()

def get_user_by_employee_id(db: Session, employee_id: str) -> Optional[User]:
    """
    Retrieves a user by their employee ID.
    """
    return db.query(User).filter(User.employee_id == employee_id).first()

def create_user(db: Session, user: UserCreate, created_by_id: Optional[int] = None) -> User:
    """
    Creates a new user in the database with all required fields.
    """
    # Check if email already exists
    if get_user_by_email(db, user.email):
        raise ValueError(f"User with email {user.email} already exists")
    
    # Check if username already exists (if provided)
    if user.username and get_user_by_username(db, user.username):
        raise ValueError(f"User with username {user.username} already exists")
    
    # Check if employee_id already exists (if provided)
    if user.employee_id and get_user_by_employee_id(db, user.employee_id):
        raise ValueError(f"User with employee ID {user.employee_id} already exists")
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create full_name from first_name and last_name
    full_name = f"{user.first_name} {user.last_name}".strip()
    
    # Create user object with all fields
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=full_name,
        phone=user.phone,
        mobile=user.mobile,
        role=user.role,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_verified=False,  # Require email verification
        employee_id=user.employee_id,
        department=user.department,
        position=user.position,
        supervisor_id=user.supervisor_id,
        company=user.company,
        timezone=user.timezone,
        language=user.language,
        emergency_contact=user.emergency_contact.dict() if user.emergency_contact else None,
        notification_settings={
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": True,
            "work_order_notifications": True,
            "asset_alerts": True,
            "system_maintenance": True,
            "daily_reports": False
        },
        preferences={
            "theme": "light",
            "dashboard_layout": "grid",
            "notifications_enabled": True
        },
        created_by_id=created_by_id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(
    db: Session, 
    user_id: int, 
    user_update: UserUpdate, 
    updated_by_id: Optional[int] = None
) -> Optional[User]:
    """
    Updates user information.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Update fields if provided
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "emergency_contact" and value:
            setattr(db_user, field, value.dict() if hasattr(value, 'dict') else value)
        elif field == "notification_settings" and value:
            # Merge with existing settings
            current_settings = db_user.notification_settings or {}
            if hasattr(value, 'dict'):
                current_settings.update(value.dict())
            else:
                current_settings.update(value)
            setattr(db_user, field, current_settings)
        else:
            setattr(db_user, field, value)
    
    # Update full_name if first_name or last_name changed
    if "first_name" in update_data or "last_name" in update_data:
        db_user.full_name = f"{db_user.first_name} {db_user.last_name}".strip()
    
    # Set updated_by
    if updated_by_id:
        db_user.updated_by_id = updated_by_id
    
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_role(
    db: Session, 
    user_id: int, 
    role_update: UserRoleUpdate, 
    updated_by_id: Optional[int] = None
) -> Optional[User]:
    """
    Updates user role and status (admin only).
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.role = role_update.role
    if role_update.status:
        db_user.status = role_update.status
        # Update is_active based on status
        db_user.is_active = role_update.status == UserStatus.ACTIVE
    
    if updated_by_id:
        db_user.updated_by_id = updated_by_id
    
    db.commit()
    db.refresh(db_user)
    return db_user

def change_password(
    db: Session, 
    user_id: int, 
    new_password: str
) -> Optional[User]:
    """
    Changes user password.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.hashed_password = get_password_hash(new_password)
    # Update password_changed_at timestamp will be handled by SQLAlchemy
    
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    search: Optional[str] = None,
    department: Optional[str] = None
) -> List[User]:
    """
    Retrieves users with filtering and pagination.
    """
    query = db.query(User)
    
    # Apply filters
    if role:
        query = query.filter(User.role == role)
    
    if status:
        query = query.filter(User.status == status)
    
    if department:
        query = query.filter(User.department == department)
    
    if search:
        search_filter = or_(
            User.first_name.ilike(f"%{search}%"),
            User.last_name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.username.ilike(f"%{search}%"),
            User.employee_id.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Exclude soft-deleted users
    query = query.filter(User.deleted_at.is_(None))
    
    return query.offset(skip).limit(limit).all()

def soft_delete_user(
    db: Session, 
    user_id: int, 
    deleted_by_id: Optional[int] = None
) -> Optional[User]:
    """
    Soft deletes a user.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    from datetime import datetime
    db_user.deleted_at = datetime.utcnow()
    db_user.deleted_by_id = deleted_by_id
    db_user.is_active = False
    db_user.status = UserStatus.INACTIVE
    
    db.commit()
    db.refresh(db_user)
    return db_user

def restore_user(db: Session, user_id: int) -> Optional[User]:
    """
    Restores a soft-deleted user.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    db_user.deleted_at = None
    db_user.deleted_by_id = None
    db_user.is_active = True
    db_user.status = UserStatus.ACTIVE
    
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticates a user by email and password.
    """
    from app.core.security import verify_password
    
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    # Update login statistics
    from datetime import datetime
    user.last_login = datetime.utcnow()
    user.login_count = (user.login_count or 0) + 1
    user.failed_login_attempts = 0  # Reset failed attempts on successful login
    
    db.commit()
    return user