from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey, event
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from enum import Enum
import uuid

from app.db.base import Base

class UserRole(str, Enum):
    """User roles for solar platform"""
    SUPER_ADMIN = "super_admin"          # System administrator
    ADMIN = "admin"                      # Platform administrator
    PLANT_MANAGER = "plant_manager"      # Solar plant manager
    SITE_SUPERVISOR = "site_supervisor"  # On-site supervisor
    TECHNICIAN = "technician"            # Field technician
    OPERATOR = "operator"                # Control room operator
    ANALYST = "analyst"                  # Data analyst
    VIEWER = "viewer"                    # Read-only user
    CUSTOMER = "customer"                # End customer
    CONTRACTOR = "contractor"            # External contractor

class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class User(Base):
    """
    Comprehensive User Model for Solar Platform
    Supports: Asset Management, Work-Order Management, Real-time Analytics
    """
    __tablename__ = "users"

    # Primary Information
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Personal Information - Make required fields non-nullable
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), nullable=True)  # Will be computed automatically
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Role & Permissions
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Work Information
    employee_id = Column(String(50), unique=True, index=True, nullable=True)
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    supervisor_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    company = Column(String(200), nullable=True)
    
    # Location & Access
    timezone = Column(String(50), default='UTC', nullable=False)
    language = Column(String(10), default='en', nullable=False)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Security & Session
    last_login = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_failed_login = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), default=func.now(), nullable=True)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    
    # Preferences & Settings
    preferences = Column(JSON, default=dict, nullable=True)  # UI preferences, dashboard settings
    notification_settings = Column(JSON, default=dict, nullable=True)  # Email, SMS, push notifications
    dashboard_config = Column(JSON, default=dict, nullable=True)  # Custom dashboard layout
    
    # API & Integration
    api_key = Column(String(255), unique=True, index=True, nullable=True)
    api_rate_limit = Column(Integer, default=1000, nullable=False)  # Requests per hour
    api_last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Audit & Compliance
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    updated_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Additional Information
    notes = Column(Text, nullable=True)  # Admin notes
    emergency_contact = Column(JSON, nullable=True)  # Emergency contact information
    certifications = Column(JSON, nullable=True)  # Professional certifications
    skills = Column(JSON, nullable=True)  # Technical skills for work assignment
    
    # Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    supervisor = relationship("User", remote_side=[id], foreign_keys=[supervisor_id], post_update=True)
    subordinates = relationship("User", foreign_keys=[supervisor_id], back_populates="supervisor")
    created_by = relationship("User", remote_side=[id], foreign_keys=[created_by_id], post_update=True)
    updated_by = relationship("User", remote_side=[id], foreign_keys=[updated_by_id], post_update=True)
    deleted_by = relationship("User", remote_side=[id], foreign_keys=[deleted_by_id], post_update=True)
    
    # Related entities (to be defined in other models)
    # assigned_assets = relationship("Asset", back_populates="assigned_user")
    # created_work_orders = relationship("WorkOrder", foreign_keys="WorkOrder.created_by_id")
    # assigned_work_orders = relationship("WorkOrder", foreign_keys="WorkOrder.assigned_to_id")
    # user_sessions = relationship("UserSession", back_populates="user")
    # audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    @property
    def is_admin(self):
        return self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]
    
    @property
    def can_manage_assets(self):
        return self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PLANT_MANAGER, UserRole.SITE_SUPERVISOR]
    
    @property
    def can_create_work_orders(self):
        return self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.PLANT_MANAGER, UserRole.SITE_SUPERVISOR, UserRole.TECHNICIAN]
    
    @property
    def can_view_analytics(self):
        return self.role != UserRole.VIEWER or self.role == UserRole.ANALYST

# SQLAlchemy event listeners to automatically compute full_name
@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def compute_full_name(mapper, connection, target):
    """Automatically compute full_name from first_name and last_name"""
    if target.first_name and target.last_name:
        target.full_name = f"{target.first_name} {target.last_name}".strip()
    elif target.first_name:
        target.full_name = target.first_name.strip()
    elif target.last_name:
        target.full_name = target.last_name.strip()
    else:
        target.full_name = None

# Constraint validation
@event.listens_for(User, 'before_insert')
@event.listens_for(User, 'before_update')
def validate_user_data(mapper, connection, target):
    """Validate user data before insert/update"""
    # Ensure email is lowercase
    if target.email:
        target.email = target.email.lower()
    
    # Ensure username is lowercase if provided
    if target.username:
        target.username = target.username.lower()
    
    # Validate timezone
    valid_timezones = [
        'UTC', 'America/New_York', 'America/Los_Angeles', 'America/Chicago', 
        'Europe/London', 'Europe/Paris', 'Asia/Tokyo', 'Asia/Bangkok'
    ]
    if target.timezone not in valid_timezones:
        target.timezone = 'UTC'
    
    # Validate language
    valid_languages = ['en', 'th', 'es', 'fr', 'de', 'ja', 'zh']
    if target.language not in valid_languages:
        target.language = 'en'
    
    # Set default preferences if empty
    if not target.preferences:
        target.preferences = {
            "theme": "light",
            "dashboard_layout": "grid",
            "notifications_enabled": True
        }
    
    # Set default notification settings if empty
    if not target.notification_settings:
        target.notification_settings = {
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": True,
            "work_order_notifications": True,
            "asset_alerts": True,
            "system_maintenance": True,
            "daily_reports": False
        }