"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from backend.models import UserRole, LoanStatus


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base User schema with common fields."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserRole = UserRole.MEMBER


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=6, max_length=100)


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Category Schemas ====================

class CategoryBase(BaseModel):
    """Base Category schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass


class CategoryResponse(CategoryBase):
    """Schema for category response."""
    id: int

    model_config = ConfigDict(from_attributes=True)


# ==================== Book Schemas ====================

class BookBase(BaseModel):
    """Base Book schema with common fields."""
    isbn: str = Field(..., min_length=10, max_length=13)
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    publisher: Optional[str] = Field(None, max_length=255)
    year: Optional[int] = Field(None, ge=1000, le=9999)
    category_id: int
    quantity: int = Field(default=1, ge=1)
    available: int = Field(default=1, ge=0)


class BookCreate(BookBase):
    """Schema for creating a new book."""
    pass


class BookResponse(BookBase):
    """Schema for book response."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== Loan Schemas ====================

class LoanBase(BaseModel):
    """Base Loan schema with common fields."""
    book_id: int
    user_id: int
    due_date: datetime
    status: LoanStatus = LoanStatus.ACTIVE


class LoanCreate(BaseModel):
    """Schema for creating a new loan."""
    book_id: int
    user_id: int
    due_date: datetime


class LoanResponse(LoanBase):
    """Schema for loan response."""
    id: int
    loan_date: datetime
    return_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LoanWithDetails(LoanResponse):
    """Schema for loan response with book and user details."""
    book: BookResponse
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)
