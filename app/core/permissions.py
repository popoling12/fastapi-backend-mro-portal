from enum import Enum
from typing import List, Dict, Set
from app.models.user import UserRole

class Permission(str, Enum):
    """System permissions for Solar Platform"""
    
    # User Management
    USER_READ = "user:read"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_ADMIN = "user:admin"
    
    # Asset Management
    ASSET_READ = "asset:read"
    ASSET_CREATE = "asset:create"
    ASSET_UPDATE = "asset:update"
    ASSET_DELETE = "asset:delete"
    ASSET_ASSIGN = "asset:assign"
    ASSET_MAINTENANCE = "asset:maintenance"
    
    # Work Order Management
    WORK_ORDER_READ = "work_order:read"
    WORK_ORDER_CREATE = "work_order:create"
    WORK_ORDER_UPDATE = "work_order:update"
    WORK_ORDER_DELETE = "work_order:delete"
    WORK_ORDER_ASSIGN = "work_order:assign"
    WORK_ORDER_APPROVE = "work_order:approve"
    WORK_ORDER_CLOSE = "work_order:close"
    
    # Analytics & Reporting
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_ADVANCED = "analytics:advanced"
    REPORT_GENERATE = "report:generate"
    REPORT_EXPORT = "report:export"
    DASHBOARD_CUSTOMIZE = "dashboard:customize"
    
    # System Administration
    SYSTEM_CONFIG = "system:config"
    SYSTEM_MAINTENANCE = "system:maintenance"
    AUDIT_LOG_READ = "audit:read"
    
    # Plant/Site Management
    PLANT_MANAGE = "plant:manage"
    SITE_SUPERVISE = "site:supervise"
    
    # Real-time Operations
    REALTIME_MONITOR = "realtime:monitor"
    REALTIME_CONTROL = "realtime:control"
    ALARM_MANAGE = "alarm:manage"

# Role-Permission Mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.SUPER_ADMIN: {
        # Full system access
        Permission.USER_READ, Permission.USER_CREATE, Permission.USER_UPDATE, 
        Permission.USER_DELETE, Permission.USER_ADMIN,
        Permission.ASSET_READ, Permission.ASSET_CREATE, Permission.ASSET_UPDATE, 
        Permission.ASSET_DELETE, Permission.ASSET_ASSIGN, Permission.ASSET_MAINTENANCE,
        Permission.WORK_ORDER_READ, Permission.WORK_ORDER_CREATE, Permission.WORK_ORDER_UPDATE, 
        Permission.WORK_ORDER_DELETE, Permission.WORK_ORDER_ASSIGN, Permission.WORK_ORDER_APPROVE, 
        Permission.WORK_ORDER_CLOSE,
        Permission.ANALYTICS_READ, Permission.ANALYTICS_ADVANCED, Permission.REPORT_GENERATE, 
        Permission.REPORT_EXPORT, Permission.DASHBOARD_CUSTOMIZE,
        Permission.SYSTEM_CONFIG, Permission.SYSTEM_MAINTENANCE, Permission.AUDIT_LOG_READ,
        Permission.PLANT_MANAGE, Permission.SITE_SUPERVISE,
        Permission.REALTIME_MONITOR, Permission.REALTIME_CONTROL, Permission.ALARM_MANAGE,
    },
    
    UserRole.ADMIN: {
        # Platform administration
        Permission.USER_READ, Permission.USER_CREATE, Permission.USER_UPDATE, Permission.USER_ADMIN,
        Permission.ASSET_READ, Permission.ASSET_CREATE, Permission.ASSET_UPDATE, 
        Permission.ASSET_ASSIGN, Permission.ASSET_MAINTENANCE,
        Permission.WORK_ORDER_READ, Permission.WORK_ORDER_CREATE, Permission.WORK_ORDER_UPDATE, 
        Permission.WORK_ORDER_ASSIGN, Permission.WORK_ORDER_APPROVE, Permission.WORK_ORDER_CLOSE,
        Permission.ANALYTICS_READ, Permission.ANALYTICS_ADVANCED, Permission.REPORT_GENERATE, 
        Permission.REPORT_EXPORT, Permission.DASHBOARD_CUSTOMIZE,
        Permission.AUDIT_LOG_READ, Permission.PLANT_MANAGE,
        Permission.REALTIME_MONITOR, Permission.REALTIME_CONTROL, Permission.ALARM_MANAGE,
    },
    
    UserRole.PLANT_MANAGER: {
        # Plant-level management
        Permission.USER_READ,
        Permission.ASSET_READ, Permission.ASSET_UPDATE, Permission.ASSET_ASSIGN, Permission.ASSET_MAINTENANCE,
        Permission.WORK_ORDER_READ, Permission.WORK_ORDER_CREATE, Permission.WORK_ORDER_UPDATE, 
        Permission.WORK_ORDER_ASSIGN, Permission.WORK_ORDER_APPROVE, Permission.WORK_ORDER_CLOSE,
        Permission.ANALYTICS_READ, Permission.ANALYTICS_ADVANCED, Permission.REPORT_GENERATE, 
        Permission.REPORT_EXPORT, Permission.DASHBOARD_CUSTOMIZE,
        Permission.PLANT_MANAGE, Permission.SITE_SUPERVISE,
        Permission.REALTIME_MONITOR, Permission.REALTIME_CONTROL, Permission.ALARM_MANAGE,
    },
    
    UserRole.SITE_SUPERVISOR: {
        # Site supervision
        Permission.USER_READ,
        Permission.ASSET_READ, Permission.ASSET_UPDATE, Permission.ASSET_MAINTENANCE,
        Permission.WORK_ORDER_READ, Permission.WORK_ORDER_CREATE, Permission.WORK_ORDER_UPDATE, 
        Permission.WORK_ORDER_ASSIGN, Permission.WORK_ORDER_CLOSE,
        Permission.ANALYTICS_READ, Permission.REPORT_GENERATE, Permission.DASHBOARD_CUSTOMIZE,
        Permission.SITE_SUPERVISE,
        Permission.REALTIME_MONITOR, Permission.ALARM_MANAGE,
    },
    
    UserRole.TECHNICIAN: {
        # Field work
        Permission.USER_READ,
        Permission.ASSET_READ, Permission.ASSET_MAINTENANCE,
        Permission.WORK_ORDER_READ, Permission.WORK_ORDER_CREATE, Permission.WORK_ORDER_UPDATE,
        Permission.ANALYTICS_READ, Permission.DASHBOARD_CUSTOMIZE,
        Permission.REALTIME_MONITOR,
    },
    
    UserRole.OPERATOR: {
        # Control room operations
        Permission.USER_READ,
        Permission.ASSET_READ,
        Permission.WORK_ORDER_READ, Permission.WORK_ORDER_CREATE,
        Permission.ANALYTICS_READ, Permission.DASHBOARD_CUSTOMIZE,
        Permission.REALTIME_MONITOR, Permission.REALTIME_CONTROL, Permission.ALARM_MANAGE,
    },
    
    UserRole.ANALYST: {
        # Data analysis
        Permission.USER_READ,
        Permission.ASSET_READ,
        Permission.WORK_ORDER_READ,
        Permission.ANALYTICS_READ, Permission.ANALYTICS_ADVANCED, Permission.REPORT_GENERATE, 
        Permission.REPORT_EXPORT, Permission.DASHBOARD_CUSTOMIZE,
        Permission.REALTIME_MONITOR,
    },
    
    UserRole.VIEWER: {
        # Read-only access
        Permission.USER_READ,
        Permission.ASSET_READ,
        Permission.WORK_ORDER_READ,
        Permission.ANALYTICS_READ, Permission.DASHBOARD_CUSTOMIZE,
        Permission.REALTIME_MONITOR,
    },
    
    UserRole.CUSTOMER: {
        # Customer access
        Permission.ASSET_READ,  # Only their assets
        Permission.ANALYTICS_READ,  # Only their data
        Permission.DASHBOARD_CUSTOMIZE,
        Permission.REALTIME_MONITOR,  # Only their systems
    },
    
    UserRole.CONTRACTOR: {
        # External contractor
        Permission.ASSET_READ,  # Assigned assets only
        Permission.WORK_ORDER_READ, Permission.WORK_ORDER_UPDATE,  # Assigned work orders only
        Permission.REALTIME_MONITOR,  # Limited access
    },
}

class PermissionChecker:
    """Utility class for checking user permissions"""
    
    @staticmethod
    def has_permission(user_role: UserRole, permission: Permission) -> bool:
        """Check if a role has a specific permission"""
        return permission in ROLE_PERMISSIONS.get(user_role, set())
    
    @staticmethod
    def get_user_permissions(user_role: UserRole) -> Set[Permission]:
        """Get all permissions for a user role"""
        return ROLE_PERMISSIONS.get(user_role, set())
    
    @staticmethod
    def can_access_resource(user_role: UserRole, resource: str, action: str) -> bool:
        """Check if user can perform action on resource"""
        permission_str = f"{resource}:{action}"
        try:
            permission = Permission(permission_str)
            return PermissionChecker.has_permission(user_role, permission)
        except ValueError:
            return False
    
    @staticmethod
    def get_manageable_roles(user_role: UserRole) -> List[UserRole]:
        """Get roles that this user can manage"""
        if user_role == UserRole.SUPER_ADMIN:
            return list(UserRole)
        elif user_role == UserRole.ADMIN:
            return [UserRole.PLANT_MANAGER, UserRole.SITE_SUPERVISOR, UserRole.TECHNICIAN, 
                   UserRole.OPERATOR, UserRole.ANALYST, UserRole.VIEWER, UserRole.CUSTOMER, 
                   UserRole.CONTRACTOR]
        elif user_role == UserRole.PLANT_MANAGER:
            return [UserRole.SITE_SUPERVISOR, UserRole.TECHNICIAN, UserRole.OPERATOR]
        elif user_role == UserRole.SITE_SUPERVISOR:
            return [UserRole.TECHNICIAN]
        else:
            return []

# Permission decorators and dependencies will be implemented in deps.py