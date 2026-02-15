"""
Category endpoints for managing book categories.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from backend.database import get_db
from backend.models import Category, Book, User, UserRole
from backend.auth import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])


# Pydantic schemas
class CategoryCreate(BaseModel):
    """Schema for creating a category."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CategoryResponse(BaseModel):
    """Schema for category response."""
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class CategoryWithBooks(BaseModel):
    """Schema for category with book count."""
    id: int
    name: str
    description: Optional[str]
    book_count: int

    class Config:
        from_attributes = True


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
@router.get("", response_model=List[CategoryWithBooks])
def list_categories(db: Session = Depends(get_db)):
    """
    List all categories with book count.

    Public endpoint - no authentication required.

    Args:
        db: Database session

    Returns:
        List of categories with book counts
    """
    categories = db.query(Category).all()

    result = []
    for category in categories:
        result.append({
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "book_count": len(category.books)
        })

    return result


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Get category details by ID.

    Public endpoint - no authentication required.

    Args:
        category_id: Category ID
        db: Database session

    Returns:
        Category details

    Raises:
        HTTPException 404: If category not found
    """
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )

    return category


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_librarian)
):
    """
    Create a new category.

    Requires authentication - admin or librarian only.

    Args:
        category_data: Category data to create
        db: Database session
        current_user: Current authenticated user (admin or librarian)

    Returns:
        Created category

    Raises:
        HTTPException 400: If category name already exists
        HTTPException 403: If user is not admin or librarian
    """
    # Check if category name already exists
    existing_category = db.query(Category).filter(
        Category.name == category_data.name
    ).first()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category_data.name}' already exists"
        )

    # Create new category
    new_category = Category(
        name=category_data.name,
        description=category_data.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_librarian)
):
    """
    Update a category.

    Requires authentication - admin or librarian only.

    Args:
        category_id: Category ID to update
        category_data: Updated category data
        db: Database session
        current_user: Current authenticated user (admin or librarian)

    Returns:
        Updated category

    Raises:
        HTTPException 404: If category not found
        HTTPException 400: If new name conflicts with existing category
        HTTPException 403: If user is not admin or librarian
    """
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )

    # If updating name, check for conflicts
    if category_data.name and category_data.name != category.name:
        existing_category = db.query(Category).filter(
            Category.name == category_data.name
        ).first()

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category_data.name}' already exists"
            )

        category.name = category_data.name

    # Update description if provided
    if category_data.description is not None:
        category.description = category_data.description

    db.commit()
    db.refresh(category)

    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a category.

    Requires authentication - admin only.
    Category can only be deleted if no books are linked to it.

    Args:
        category_id: Category ID to delete
        db: Database session
        current_user: Current authenticated user (admin)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 404: If category not found
        HTTPException 400: If category has linked books
        HTTPException 403: If user is not admin
    """
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )

    # Check if category has linked books
    book_count = db.query(Book).filter(Book.category_id == category_id).count()

    if book_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category. {book_count} book(s) are linked to this category"
        )

    db.delete(category)
    db.commit()

    return None
