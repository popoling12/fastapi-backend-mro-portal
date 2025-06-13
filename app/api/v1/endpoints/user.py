from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud.crud_user import (
    get_users, get_user, get_user_by_email, create_user, 
    update_user, update_user_role, change_password, 
    soft_delete_user, restore_user, authenticate_user
)
from app.core.permissions import PermissionChecker, Permission
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import (
    UserCreate, UserUpdate, UserPublic, UserProfile, UserDetail, 
    UserAdmin, UserListItem, UserPasswordChange, UserRoleUpdate,
    UserResponse, UserListResponse, UserCreateResponse
)

router = APIRouter()

# ===== PUBLIC/AUTH ENDPOINTS =====

@router.post("/", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create new user (Admin only)
    """
    # Check permissions
    if not PermissionChecker.has_permission(current_user.role, Permission.USER_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create users"
        )
    
    # Check if user with email already exists
    if get_user_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )
    
    # Check if current user can create this role
    manageable_roles = PermissionChecker.get_manageable_roles(current_user.role)
    if user_in.role not in manageable_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot create user with role: {user_in.role}"
        )
    
    try:
        user = create_user(db=db, user=user_in, created_by_id=current_user.id)
        return UserCreateResponse(
            success=True,
            message="User created successfully",
            data=UserPublic.model_validate(user)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=UserListResponse)
def read_users(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    status: Optional[UserStatus] = Query(None, description="Filter by user status"),
    search: Optional[str] = Query(None, description="Search in name, email, username, employee_id"),
    department: Optional[str] = Query(None, description="Filter by department")
) -> Any:
    """
    Retrieve users with filtering and pagination
    """
    # Check permissions
    if not PermissionChecker.has_permission(current_user.role, Permission.USER_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to read users"
        )
    
    users = get_users(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        status=status,
        search=search,
        department=department
    )
    
    # Convert to UserListItem format
    user_items = [UserListItem.model_validate(user) for user in users]
    
    # Get total count (simplified for demo)
    total = len(users)  # In production, implement proper count query
    
    return UserListResponse(
        success=True,
        message="Users retrieved successfully",
        data=user_items,
        total=total,
        page=(skip // limit) + 1,
        per_page=limit
    )

@router.get("/me", response_model=UserProfile)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get current user profile
    """
    return UserProfile.model_validate(current_user)

@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update current user profile
    """
    try:
        user = update_user(
            db=db, 
            user_id=current_user.id, 
            user_update=user_in,
            updated_by_id=current_user.id
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            success=True,
            message="Profile updated successfully",
            data=UserPublic.model_validate(user)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/me/change-password", response_model=UserResponse)
def change_user_password(
    *,
    db: Session = Depends(deps.get_db),
    password_data: UserPasswordChange,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Change current user password
    """
    from app.core.security import verify_password
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Change password
    user = change_password(db=db, user_id=current_user.id, new_password=password_data.new_password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        success=True,
        message="Password changed successfully",
        data=UserPublic.model_validate(user)
    )

# ===== ADMIN ENDPOINTS =====

@router.get("/{user_id}", response_model=UserDetail)
def read_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get user by ID (Admin or Manager only)
    """
    # Check permissions
    if not PermissionChecker.has_permission(current_user.role, Permission.USER_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to read user details"
        )
    
    user = get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Return appropriate detail level based on permissions
    if PermissionChecker.has_permission(current_user.role, Permission.USER_ADMIN):
        return UserAdmin.model_validate(user)
    else:
        return UserDetail.model_validate(user)

@router.put("/{user_id}", response_model=UserResponse)
def update_user_by_id(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update user by ID (Admin only)
    """
    # Check permissions
    if not PermissionChecker.has_permission(current_user.role, Permission.USER_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update users"
        )
    
    user = get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        updated_user = update_user(
            db=db, 
            user_id=user_id, 
            user_update=user_in,
            updated_by_id=current_user.id
        )
        
        return UserResponse(
            success=True,
            message="User updated successfully",
            data=UserPublic.model_validate(updated_user)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role_by_id(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    role_update: UserRoleUpdate,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update user role and status (Admin only)
    """
    # Check permissions
    if not PermissionChecker.has_permission(current_user.role, Permission.USER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update user roles"
        )
    
    user = get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if current user can assign this role
    manageable_roles = PermissionChecker.get_manageable_roles(current_user.role)
    if role_update.role not in manageable_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot assign role: {role_update.role}"
        )
    
    # Prevent users from changing their own role
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    updated_user = update_user_role(
        db=db, 
        user_id=user_id, 
        role_update=role_update,
        updated_by_id=current_user.id
    )
    
    return UserResponse(
        success=True,
        message="User role updated successfully",
        data=UserPublic.model_validate(updated_user)
    )

@router.post("/{user_id}/reset-password", response_model=UserResponse)
def reset_user_password(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Reset user password (Admin only)
    """
    # Check permissions
    if not PermissionChecker.has_permission(current_user.role, Permission.USER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to reset passwords"
        )
    
    user = get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate temporary password
    import secrets
    import string
    
    # Generate a secure temporary password
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))
    
    # Ensure password meets requirements
    temp_password = "Temp" + temp_password[:8] + "123!"
    
    updated_user = change_password(db=db, user_id=user_id, new_password=temp_password)
    
    return UserResponse(
        success=True,
        message=f"Password reset successfully. Temporary password: {temp_password}",
        data=UserPublic.model_validate(updated_user)
    )

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Soft delete user (Admin only)
    """
    # Check permissions
    if not PermissionChecker.has_permission(current_user.role, Permission.USER_DELETE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete users"
        )
    
    user = get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent users from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Prevent deleting super admin (if current user is not super admin)
    if user.role == UserRole.SUPER_ADMIN and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete super admin user"
        )
    
    deleted_user = soft_delete_user(db=db, user_id=user_id, deleted_by_id=current_user.id)
    
    return UserResponse(
        success=True,
        message="User deleted successfully",
        data=UserPublic.model_validate(deleted_user)
    )

@router.post("/{user_id}/restore", response_model=UserResponse)
def restore_deleted_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Restore soft-deleted user (Super Admin only)
    """
    # Check permissions - only super admin can restore users
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can restore deleted users"
        )
    
    restored_user = restore_user(db=db, user_id=user_id)
    
    if not restored_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or cannot be restored"
        )
    
    return UserResponse(
        success=True,
        message="User restored successfully",
        data=UserPublic.model_validate(restored_user)
    )

# ===== UTILITY ENDPOINTS =====

@router.get("/roles/available", response_model=List[str])
def get_available_roles(
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get roles that current user can assign
    """
    manageable_roles = PermissionChecker.get_manageable_roles(current_user.role)
    return [role.value for role in manageable_roles]

@router.get("/permissions/check", response_model=dict)
def check_user_permissions(
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get current user permissions
    """
    permissions = PermissionChecker.get_user_permissions(current_user.role)
    
    return {
        "user_id": current_user.id,
        "role": current_user.role,
        "permissions": [perm.value for perm in permissions],
        "can_manage_users": PermissionChecker.has_permission(current_user.role, Permission.USER_ADMIN),
        "can_create_users": PermissionChecker.has_permission(current_user.role, Permission.USER_CREATE),
        "can_update_users": PermissionChecker.has_permission(current_user.role, Permission.USER_UPDATE),
        "can_delete_users": PermissionChecker.has_permission(current_user.role, Permission.USER_DELETE),
        "manageable_roles": [role.value for role in PermissionChecker.get_manageable_roles(current_user.role)]
    }

@router.get("/stats/summary", response_model=dict)
def get_user_stats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get user statistics (Admin only)
    """
    # Check permissions
    if not PermissionChecker.has_permission(current_user.role, Permission.USER_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view user statistics"
        )
    
    from sqlalchemy import func, text
    
    try:
        # Get role distribution
        role_stats = db.execute(text("""
            SELECT role, COUNT(*) as count 
            FROM users 
            WHERE deleted_at IS NULL 
            GROUP BY role 
            ORDER BY role
        """)).fetchall()
        
        # Get status distribution  
        status_stats = db.execute(text("""
            SELECT status, COUNT(*) as count 
            FROM users 
            WHERE deleted_at IS NULL 
            GROUP BY status 
            ORDER BY status
        """)).fetchall()
        
        # Get department distribution
        dept_stats = db.execute(text("""
            SELECT department, COUNT(*) as count 
            FROM users 
            WHERE deleted_at IS NULL AND department IS NOT NULL
            GROUP BY department 
            ORDER BY count DESC
            LIMIT 10
        """)).fetchall()
        
        # Get total counts
        total_users = db.execute(text("SELECT COUNT(*) FROM users WHERE deleted_at IS NULL")).scalar()
        active_users = db.execute(text("SELECT COUNT(*) FROM users WHERE deleted_at IS NULL AND is_active = true")).scalar()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "role_distribution": [{"role": r[0], "count": r[1]} for r in role_stats],
            "status_distribution": [{"status": s[0], "count": s[1]} for s in status_stats],
            "department_distribution": [{"department": d[0], "count": d[1]} for d in dept_stats]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user statistics: {str(e)}"
        )