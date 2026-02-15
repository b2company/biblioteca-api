"""
Loan management endpoints for biblioteca.
Handles book lending, returns, and loan tracking with full business rule validation.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from pydantic import BaseModel

from backend.database import get_db
from backend.models import Loan, Book, User, LoanStatus, UserRole
from backend.schemas import LoanWithDetails
from backend.auth import get_current_active_user

router = APIRouter(prefix="/loans", tags=["Loans"])


# Request/Response Schemas
class LoanCreateRequest(BaseModel):
    """Schema for creating a loan (simplified)."""
    book_id: int


class LoanListResponse(BaseModel):
    """Schema for paginated loan list response."""
    total: int
    page: int
    limit: int
    loans: List[LoanWithDetails]


# Business Rules Constants
LOAN_DURATION_DAYS = 14
MAX_ACTIVE_LOANS = 3


def check_user_can_borrow(db: Session, user_id: int) -> None:
    """
    Validate if user can borrow a new book.

    Rules:
    - User cannot have >= 3 active loans
    - User cannot have any overdue loans

    Args:
        db: Database session
        user_id: User ID to check

    Raises:
        HTTPException 400: If user has too many active loans or overdue loans
    """
    # Check active loans count
    active_loans_count = db.query(Loan).filter(
        and_(
            Loan.user_id == user_id,
            Loan.status == LoanStatus.ACTIVE
        )
    ).count()

    if active_loans_count >= MAX_ACTIVE_LOANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User already has {MAX_ACTIVE_LOANS} active loans. Please return a book before borrowing another."
        )

    # Check for overdue loans
    now = datetime.utcnow()
    overdue_loans = db.query(Loan).filter(
        and_(
            Loan.user_id == user_id,
            Loan.status == LoanStatus.ACTIVE,
            Loan.due_date < now
        )
    ).first()

    if overdue_loans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has overdue loans. Please return overdue books before borrowing new ones."
        )


def check_book_available(db: Session, book_id: int) -> Book:
    """
    Validate if book exists and is available for loan.

    Args:
        db: Database session
        book_id: Book ID to check

    Returns:
        Book object if available

    Raises:
        HTTPException 404: If book not found
        HTTPException 400: If book not available
    """
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    if book.available <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book not available for loan"
        )

    return book


@router.get("", response_model=LoanListResponse)
def list_loans(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: active, returned, overdue"),
    user_id: Optional[int] = Query(None, description="Filter by user ID (admin/librarian only)"),
    book_id: Optional[int] = Query(None, description="Filter by book ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List loans with filtering and pagination.

    Access control:
    - Admin/Librarian: Can see all loans, can filter by user_id
    - Member: Can only see their own loans

    Filters:
    - status: active, returned, overdue
    - user_id: Filter by user (admin/librarian only)
    - book_id: Filter by book

    Args:
        status_filter: Optional status filter
        user_id: Optional user ID filter (admin/librarian only)
        book_id: Optional book ID filter
        page: Page number (1-indexed)
        limit: Items per page (1-100)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Paginated list of loans with book and user details

    Raises:
        HTTPException 403: If member tries to filter by other user_id
    """
    query = db.query(Loan).options(
        joinedload(Loan.book).joinedload(Book.category),
        joinedload(Loan.user)
    )

    # Access control: members can only see their own loans
    if current_user.role == UserRole.MEMBER:
        if user_id and user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Members can only view their own loans"
            )
        query = query.filter(Loan.user_id == current_user.id)
    elif user_id:
        # Admin/librarian can filter by user_id
        query = query.filter(Loan.user_id == user_id)

    # Apply status filter
    if status_filter:
        if status_filter == "overdue":
            # Overdue = active status AND due_date < now
            now = datetime.utcnow()
            query = query.filter(
                and_(
                    Loan.status == LoanStatus.ACTIVE,
                    Loan.due_date < now
                )
            )
        elif status_filter in ["active", "returned"]:
            query = query.filter(Loan.status == status_filter)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter. Use: active, returned, or overdue"
            )

    # Apply book_id filter
    if book_id:
        query = query.filter(Loan.book_id == book_id)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    loans = query.order_by(Loan.loan_date.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "loans": loans
    }


@router.get("/my-loans", response_model=LoanListResponse)
def get_my_loans(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get loans for the current authenticated user.

    Args:
        page: Page number (1-indexed)
        limit: Items per page (1-100)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Paginated list of user's loans with book details
    """
    query = db.query(Loan).options(
        joinedload(Loan.book).joinedload(Book.category),
        joinedload(Loan.user)
    ).filter(Loan.user_id == current_user.id)

    total = query.count()

    offset = (page - 1) * limit
    loans = query.order_by(Loan.loan_date.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "loans": loans
    }


@router.get("/overdue", response_model=LoanListResponse)
def list_overdue_loans(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all overdue loans.

    Overdue = status is ACTIVE and due_date < now
    Requires admin or librarian role.

    Args:
        page: Page number (1-indexed)
        limit: Items per page (1-100)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Paginated list of overdue loans

    Raises:
        HTTPException 403: If user is not admin or librarian
    """
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and librarians can view overdue loans"
        )

    now = datetime.utcnow()

    query = db.query(Loan).options(
        joinedload(Loan.book).joinedload(Book.category),
        joinedload(Loan.user)
    ).filter(
        and_(
            Loan.status == LoanStatus.ACTIVE,
            Loan.due_date < now
        )
    )

    total = query.count()

    offset = (page - 1) * limit
    loans = query.order_by(Loan.due_date.asc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "loans": loans
    }


@router.post("", response_model=LoanWithDetails, status_code=status.HTTP_201_CREATED)
def create_loan(
    loan_data: LoanCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new book loan.

    Business rules:
    1. Book must exist and have available > 0
    2. User cannot have >= 3 active loans
    3. User cannot have any overdue loans

    Actions:
    1. Create loan with status "active", due_date = today + 14 days
    2. Decrement book.available -= 1

    Args:
        loan_data: Loan creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created loan with book and user details

    Raises:
        HTTPException 404: If book not found
        HTTPException 400: If book not available or user cannot borrow
    """
    # Validation 1: Check book exists and is available
    book = check_book_available(db, loan_data.book_id)

    # Validation 2 & 3: Check user can borrow
    check_user_can_borrow(db, current_user.id)

    # Calculate due date
    loan_date = datetime.utcnow()
    due_date = loan_date + timedelta(days=LOAN_DURATION_DAYS)

    # Create loan
    new_loan = Loan(
        book_id=loan_data.book_id,
        user_id=current_user.id,
        loan_date=loan_date,
        due_date=due_date,
        status=LoanStatus.ACTIVE
    )

    # Decrement book availability
    book.available -= 1

    # Save to database
    db.add(new_loan)
    db.commit()

    # Reload with relationships
    db.refresh(new_loan)
    loan_with_details = db.query(Loan).options(
        joinedload(Loan.book).joinedload(Book.category),
        joinedload(Loan.user)
    ).filter(Loan.id == new_loan.id).first()

    return loan_with_details


@router.put("/{loan_id}/return", response_model=LoanWithDetails)
def return_loan(
    loan_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Return a borrowed book.

    Access control:
    - Member: Can only return their own loans
    - Admin/Librarian: Can return any loan

    Validations:
    1. Loan must exist and be active
    2. Members can only return their own loans

    Actions:
    1. Update loan: status = "returned", return_date = now
    2. Increment book.available += 1

    Args:
        loan_id: ID of the loan to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated loan with book and user details

    Raises:
        HTTPException 404: If loan not found
        HTTPException 400: If loan is not active
        HTTPException 403: If member tries to return another user's loan
    """
    # Get loan with relationships
    loan = db.query(Loan).options(
        joinedload(Loan.book).joinedload(Book.category),
        joinedload(Loan.user)
    ).filter(Loan.id == loan_id).first()

    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Loan not found"
        )

    # Validation: Loan must be active
    if loan.status != LoanStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Loan is not active (current status: {loan.status})"
        )

    # Access control: Members can only return their own loans
    if current_user.role == UserRole.MEMBER and loan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only return your own loans"
        )

    # Update loan status
    loan.status = LoanStatus.RETURNED
    loan.return_date = datetime.utcnow()

    # Increment book availability
    loan.book.available += 1

    # Save changes
    db.commit()
    db.refresh(loan)

    return loan
