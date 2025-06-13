from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
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
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200))  # Computed field
    phone = Column(String(20))
    mobile = Column(String(20))
    avatar_url = Column(String(500))
    
    # Role & Permissions
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Work Information
    employee_id = Column(String(50), unique=True, index=True)
    department = Column(String(100))
    position = Column(String(100))
    supervisor_id = Column(Integer, ForeignKey('users.id'))
    company = Column(String(200))
    
    # Location & Access
    timezone = Column(String(50), default='UTC')
    language = Column(String(10), default='en')
    country = Column(String(100))
    city = Column(String(100))
    
    # Security & Session
    last_login = Column(DateTime(timezone=True))
    login_count = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime(timezone=True))
    password_changed_at = Column(DateTime(timezone=True), default=func.now())
    two_factor_enabled = Column(Boolean, default=False)
    
    # Preferences & Settings
    preferences = Column(JSON, default=dict)  # UI preferences, dashboard settings
    notification_settings = Column(JSON, default=dict)  # Email, SMS, push notifications
    dashboard_config = Column(JSON, default=dict)  # Custom dashboard layout
    
    # API & Integration
    api_key = Column(String(255), unique=True, index=True)
    api_rate_limit = Column(Integer, default=1000)  # Requests per hour
    api_last_used = Column(DateTime(timezone=True))
    
    # Audit & Compliance
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey('users.id'))
    updated_by_id = Column(Integer, ForeignKey('users.id'))
    
    # Additional Information
    notes = Column(Text)  # Admin notes
    emergency_contact = Column(JSON)  # Emergency contact information
    certifications = Column(JSON)  # Professional certifications
    skills = Column(JSON)  # Technical skills for work assignment
    
    # Soft Delete
    deleted_at = Column(DateTime(timezone=True))
    deleted_by_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    supervisor = relationship("User", remote_side=[id], foreign_keys=[supervisor_id])
    subordinates = relationship("User", foreign_keys=[supervisor_id])
    created_by = relationship("User", remote_side=[id], foreign_keys=[created_by_id])
    updated_by = relationship("User", remote_side=[id], foreign_keys=[updated_by_id])
    deleted_by = relationship("User", remote_side=[id], foreign_keys=[deleted_by_id])
    
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