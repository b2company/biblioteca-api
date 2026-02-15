"""
User management router for biblioteca system.
Handles user listing, details, role management, and statistics.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from backend.database import get_db
from backend.models import User, UserRole, Loan, LoanStatus
from backend.schemas import UserResponse
from backend.auth import get_current_active_user
from pydantic import BaseModel, Field


# ==================== Helper Schemas ====================

class RoleUpdate(BaseModel):
    """Schema for updating user role."""
    role: UserRole


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    total: int
    page: int
    limit: int
    users: list[UserResponse]


class UserStatsResponse(BaseModel):
    """Schema for user statistics response."""
    active_loans: int
    total_loans: int
    overdue_loans: int
    can_borrow: bool


# ==================== Authorization Helpers ====================

def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to ensure current user is admin.

    Args:
        current_user: Current authenticated user

    Returns:
        User object if admin

    Raises:
        HTTPException: 403 if user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_admin_or_librarian(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency to ensure current user is admin or librarian.

    Args:
        current_user: Current authenticated user

    Returns:
        User object if admin or librarian

    Raises:
        HTTPException: 403 if user is neither admin nor librarian
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Librarian access required"
        )
    return current_user


# ==================== Router Setup ====================

router = APIRouter()


# ==================== Endpoints ====================

@router.get("/users", response_model=UserListResponse)
def list_users(
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    List all users with pagination and optional role filtering.

    Only admin users can access this endpoint.

    Args:
        role: Optional filter by user role
        page: Page number (starts at 1)
        limit: Number of items per page (max 100)
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        Paginated list of users
    """
    # Build query
    query = db.query(User)

    # Apply role filter if provided
    if role is not None:
        query = query.filter(User.role == role)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    users = query.offset(offset).limit(limit).all()

    return UserListResponse(
        total=total,
        page=page,
        limit=limit,
        users=users
    )


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get details of a specific user.

    Admin users can view any user.
    Non-admin users can only view their own profile.

    Args:
        user_id: ID of the user to retrieve
        db: Database session
        current_user: Current authenticated user

    Returns:
        User details

    Raises:
        HTTPException: 403 if non-admin tries to view another user
        HTTPException: 404 if user not found
    """
    # Check authorization
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile"
        )

    # Get user
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    return user


@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update a user's role.

    Only admin users can change roles.

    Args:
        user_id: ID of the user to update
        role_update: New role data
        db: Database session
        current_user: Current authenticated admin user

    Returns:
        Updated user details

    Raises:
        HTTPException: 404 if user not found
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Update role
    user.role = role_update.role
    db.commit()
    db.refresh(user)

    return user


@router.get("/users/{user_id}/stats", response_model=UserStatsResponse)
def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get statistics for a specific user.

    Admin and librarian users can view stats for any user.
    Member users can only view their own stats.

    Args:
        user_id: ID of the user to get stats for
        db: Database session
        current_user: Current authenticated user

    Returns:
        User statistics including loan counts and borrowing eligibility

    Raises:
        HTTPException: 403 if member tries to view another user's stats
        HTTPException: 404 if user not found
    """
    # Check authorization
    if current_user.role == UserRole.MEMBER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own statistics"
        )

    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Get active loans count
    active_loans = db.query(func.count(Loan.id)).filter(
        Loan.user_id == user_id,
        Loan.status == LoanStatus.ACTIVE
    ).scalar()

    # Get total loans count
    total_loans = db.query(func.count(Loan.id)).filter(
        Loan.user_id == user_id
    ).scalar()

    # Get overdue loans count (active loans with due_date in the past)
    now = datetime.utcnow()
    overdue_loans = db.query(func.count(Loan.id)).filter(
        Loan.user_id == user_id,
        Loan.status == LoanStatus.ACTIVE,
        Loan.due_date < now
    ).scalar()

    # Determine if user can borrow (no overdue loans and less than 3 active loans)
    can_borrow = (overdue_loans == 0) and (active_loans < 3)

    return UserStatsResponse(
        active_loans=active_loans,
        total_loans=total_loans,
        overdue_loans=overdue_loans,
        can_borrow=can_borrow
    )
