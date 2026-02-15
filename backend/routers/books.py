"""
Book endpoints for managing library books.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from backend.database import get_db
from backend.models import Book, Category, Loan, LoanStatus, User, UserRole
from backend.auth import get_current_user

router = APIRouter(prefix="/books", tags=["Books"])


# Pydantic schemas
class BookCreate(BaseModel):
    """Schema for creating a book."""
    isbn: str = Field(..., min_length=10, max_length=13)
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    publisher: Optional[str] = Field(None, max_length=255)
    year: Optional[int] = Field(None, ge=1000, le=9999)
    category_id: int
    quantity: int = Field(..., ge=0)


class BookUpdate(BaseModel):
    """Schema for updating a book."""
    isbn: Optional[str] = Field(None, min_length=10, max_length=13)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    publisher: Optional[str] = Field(None, max_length=255)
    year: Optional[int] = Field(None, ge=1000, le=9999)
    category_id: Optional[int] = None
    quantity: Optional[int] = Field(None, ge=0)


class CategoryInBook(BaseModel):
    """Schema for category info in book response."""
    id: int
    name: str

    class Config:
        from_attributes = True


class BookResponse(BaseModel):
    """Schema for book response."""
    id: int
    isbn: str
    title: str
    author: str
    publisher: Optional[str]
    year: Optional[int]
    category_id: int
    category: CategoryInBook
    quantity: int
    available: int

    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    """Schema for paginated book list response."""
    total: int
    page: int
    limit: int
    books: List[BookResponse]


# Authorization dependencies
def require_admin_or_librarian(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure user is admin or librarian.

    Args:
        current_user: Current authenticated user

    Returns:
        User if authorized

    Raises:
        HTTPException 403: If user is not admin or librarian
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.LIBRARIAN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and librarians can perform this action"
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure user is admin.

    Args:
        current_user: Current authenticated user

    Returns:
        User if authorized

    Raises:
        HTTPException 403: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action"
        )
    return current_user


# Endpoints
@router.get("", response_model=BookListResponse)
def list_books(
    title: Optional[str] = Query(None, description="Search by title (partial match, case-insensitive)"),
    author: Optional[str] = Query(None, description="Search by author (partial match, case-insensitive)"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    available: Optional[bool] = Query(None, description="Filter by availability (true = has available copies)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List books with pagination and advanced filters.

    Public endpoint - no authentication required.

    Supports filtering by:
    - title (partial, case-insensitive)
    - author (partial, case-insensitive)
    - category_id
    - available (true/false)

    Args:
        title: Title search string
        author: Author search string
        category_id: Category ID to filter
        available: Filter by availability
        page: Page number (default 1)
        limit: Items per page (default 20, max 100)
        db: Database session

    Returns:
        Paginated list of books with total count
    """
    # Build query
    query = db.query(Book)

    # Apply filters
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))

    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))

    if category_id is not None:
        query = query.filter(Book.category_id == category_id)

    if available is not None:
        if available:
            query = query.filter(Book.available > 0)
        else:
            query = query.filter(Book.available == 0)

    # Get total count
    total = query.count()

    # Apply pagination
    skip = (page - 1) * limit
    books = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "books": books
    }


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """
    Get book details by ID.

    Public endpoint - no authentication required.
    Includes category information via relationship.

    Args:
        book_id: Book ID
        db: Database session

    Returns:
        Book details with category

    Raises:
        HTTPException 404: If book not found
    """
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )

    return book


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book_data: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_librarian)
):
    """
    Add a new book to the library.

    Requires authentication - admin or librarian only.
    Sets available = quantity initially.

    Args:
        book_data: Book data to create
        db: Database session
        current_user: Current authenticated user (admin or librarian)

    Returns:
        Created book

    Raises:
        HTTPException 400: If ISBN already exists or category not found
        HTTPException 403: If user is not admin or librarian
    """
    # Check if ISBN already exists
    existing_book = db.query(Book).filter(Book.isbn == book_data.isbn).first()

    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book with ISBN '{book_data.isbn}' already exists"
        )

    # Verify category exists
    category = db.query(Category).filter(Category.id == book_data.category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with id {book_data.category_id} not found"
        )

    # Create new book
    new_book = Book(
        isbn=book_data.isbn,
        title=book_data.title,
        author=book_data.author,
        publisher=book_data.publisher,
        year=book_data.year,
        category_id=book_data.category_id,
        quantity=book_data.quantity,
        available=book_data.quantity  # Initially, available = quantity
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_librarian)
):
    """
    Update a book.

    Requires authentication - admin or librarian only.
    Does NOT allow direct modification of 'available' field (controlled by loans).
    If quantity is updated, adjusts available proportionally.

    Args:
        book_id: Book ID to update
        book_data: Updated book data
        db: Database session
        current_user: Current authenticated user (admin or librarian)

    Returns:
        Updated book

    Raises:
        HTTPException 404: If book not found
        HTTPException 400: If ISBN conflicts or category not found
        HTTPException 403: If user is not admin or librarian
    """
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )

    # If updating ISBN, check for conflicts
    if book_data.isbn and book_data.isbn != book.isbn:
        existing_book = db.query(Book).filter(Book.isbn == book_data.isbn).first()

        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ISBN '{book_data.isbn}' already exists"
            )

        book.isbn = book_data.isbn

    # If updating category, verify it exists
    if book_data.category_id and book_data.category_id != book.category_id:
        category = db.query(Category).filter(Category.id == book_data.category_id).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {book_data.category_id} not found"
            )

        book.category_id = book_data.category_id

    # Update other fields
    if book_data.title:
        book.title = book_data.title

    if book_data.author:
        book.author = book_data.author

    if book_data.publisher is not None:
        book.publisher = book_data.publisher

    if book_data.year is not None:
        book.year = book_data.year

    # Handle quantity update: adjust available proportionally
    if book_data.quantity is not None and book_data.quantity != book.quantity:
        # Calculate difference
        quantity_diff = book_data.quantity - book.quantity

        # Adjust available, ensuring it doesn't go negative
        new_available = book.available + quantity_diff
        book.available = max(0, new_available)
        book.quantity = book_data.quantity

    db.commit()
    db.refresh(book)

    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a book.

    Requires authentication - admin only.
    Book can only be deleted if there are no active loans.

    Args:
        book_id: Book ID to delete
        db: Database session
        current_user: Current authenticated user (admin)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: If book not found
        HTTPException 400: If book has active loans
        HTTPException 403: If user is not admin
    """
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )

    # Check for active loans
    active_loan_count = db.query(Loan).filter(
        Loan.book_id == book_id,
        Loan.status == LoanStatus.ACTIVE
    ).count()

    if active_loan_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete book. {active_loan_count} active loan(s) exist for this book"
        )

    db.delete(book)
    db.commit()

    return None
