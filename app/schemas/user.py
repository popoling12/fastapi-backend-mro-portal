from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator, Field, ConfigDict
from enum import Enum

# Import enums from models - Keep in sync with model
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    PLANT_MANAGER = "plant_manager"
    SITE_SUPERVISOR = "site_supervisor"
    TECHNICIAN = "technician"
    OPERATOR = "operator"
    ANALYST = "analyst"
    VIEWER = "viewer"
    CUSTOMER = "customer"
    CONTRACTOR = "contractor"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

# ===== BASE SCHEMAS =====

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    username: Optional[str] = None
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)

class EmergencyContact(BaseModel):
    """Emergency contact information"""
    name: str = Field(..., min_length=1, max_length=200)
    relationship: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=1, max_length=20)
    email: Optional[EmailStr] = None

class NotificationSettings(BaseModel):
    """User notification preferences"""
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    work_order_notifications: bool = True
    asset_alerts: bool = True
    system_maintenance: bool = True
    daily_reports: bool = False

class UserPreferences(BaseModel):
    """User UI preferences"""
    theme: str = Field("light", pattern="^(light|dark)$")
    dashboard_layout: str = Field("grid", pattern="^(grid|list|card)$")
    notifications_enabled: bool = True
    language: str = Field("en", pattern="^(en|th|es|fr|de|ja|zh)$")
    timezone: str = "UTC"

# ===== INPUT SCHEMAS =====

class UserCreate(UserBase):
    """Schema for creating new user"""
    password: str = Field(..., min_length=8, max_length=128, description="Password must be at least 8 characters")
    role: UserRole = UserRole.VIEWER
    employee_id: Optional[str] = Field(None, max_length=50)
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    supervisor_id: Optional[int] = None
    company: Optional[str] = Field(None, max_length=200)
    timezone: str = Field("UTC", max_length=50)
    language: str = Field("en", max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    emergency_contact: Optional[EmergencyContact] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        return v.lower()
    
    @validator('username')
    def validate_username(cls, v):
        if v:
            return v.lower()
        return v
    
    @validator('timezone')
    def validate_timezone(cls, v):
        valid_timezones = [
            'UTC', 'America/New_York', 'America/Los_Angeles', 'America/Chicago', 
            'Europe/London', 'Europe/Paris', 'Asia/Tokyo', 'Asia/Bangkok'
        ]
        if v not in valid_timezones:
            return 'UTC'
        return v

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, max_length=100)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    mobile: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    supervisor_id: Optional[int] = None
    company: Optional[str] = Field(None, max_length=200)
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, max_length=10)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    emergency_contact: Optional[EmergencyContact] = None
    notification_settings: Optional[NotificationSettings] = None
    preferences: Optional[UserPreferences] = None

class UserPasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class UserRoleUpdate(BaseModel):
    """Schema for updating user role (admin only)"""
    role: UserRole
    status: Optional[UserStatus] = None

# ===== OUTPUT SCHEMAS =====

class UserPublic(UserBase):
    """Public user information (safe for general viewing)"""
    id: int
    uuid: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: UserRole
    status: UserStatus
    department: Optional[str] = None
    position: Optional[str] = None
    company: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserProfile(UserPublic):
    """Extended user profile (for own profile or authorized viewing)"""
    employee_id: Optional[str] = None
    timezone: str
    language: str
    country: Optional[str] = None
    city: Optional[str] = None
    last_login: Optional[datetime] = None
    two_factor_enabled: bool
    emergency_contact: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

class UserDetail(UserProfile):
    """Detailed user information (for managers/supervisors)"""
    supervisor_id: Optional[int] = None
    login_count: int
    certifications: Optional[Dict[str, Any]] = None
    skills: Optional[Dict[str, Any]] = None
    updated_at: datetime

class UserAdmin(UserDetail):
    """Complete user information (admin only)"""
    is_verified: bool
    failed_login_attempts: int
    last_failed_login: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    api_key: Optional[str] = None
    api_rate_limit: int
    api_last_used: Optional[datetime] = None
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None
    notes: Optional[str] = None
    deleted_at: Optional[datetime] = None

# ===== SPECIALIZED SCHEMAS =====

class UserListItem(BaseModel):
    """Minimal user info for lists/dropdowns"""
    id: int
    uuid: str
    full_name: str
    email: EmailStr
    role: UserRole
    status: UserStatus
    avatar_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserAssignment(BaseModel):
    """User info for work order/asset assignments"""
    id: int
    uuid: str
    full_name: str
    role: UserRole
    department: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    skills: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)

# ===== API RESPONSE SCHEMAS =====

class UserResponse(BaseModel):
    """Standard API response for user operations"""
    success: bool = True
    message: str
    data: Optional[UserPublic] = None

class UserListResponse(BaseModel):
    """Response for user list endpoints"""
    success: bool = True
    message: str
    data: List[UserListItem]
    total: int
    page: int = 1
    per_page: int = 10

class UserCreateResponse(UserResponse):
    """Response for user creation"""
    data: Optional[UserPublic] = None
    temporary_password: Optional[str] = None

# ===== INTERNAL SCHEMAS =====

class UserInDB(UserBase):
    """Internal user schema with hashed password"""
    id: int
    uuid: str
    hashed_password: str
    full_name: Optional[str] = None
    role: UserRole
    status: UserStatus
    is_active: bool
    is_verified: bool
    employee_id: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    supervisor_id: Optional[int] = None
    company: Optional[str] = None
    timezone: str
    language: str
    country: Optional[str] = None
    city: Optional[str] = None
    avatar_url: Optional[str] = None
    last_login: Optional[datetime] = None
    login_count: int = 0
    failed_login_attempts: int = 0
    last_failed_login: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    two_factor_enabled: bool = False
    preferences: Optional[Dict[str, Any]] = None
    notification_settings: Optional[Dict[str, Any]] = None
    dashboard_config: Optional[Dict[str, Any]] = None
    api_key: Optional[str] = None
    api_rate_limit: int = 1000
    api_last_used: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    updated_by_id: Optional[int] = None
    notes: Optional[str] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    certifications: Optional[Dict[str, Any]] = None
    skills: Optional[Dict[str, Any]] = None
    deleted_at: Optional[datetime] = None
    deleted_by_id: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)