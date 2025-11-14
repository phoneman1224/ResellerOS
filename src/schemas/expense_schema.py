"""
Pydantic schemas for Expense validation and serialization.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class ExpenseBase(BaseModel):
    """Base expense schema with common fields."""

    title: str = Field(..., min_length=1, max_length=200, description="Expense title")
    description: Optional[str] = Field(None, description="Expense description")
    category: str = Field(..., max_length=100, description="Expense category")
    amount: float = Field(..., gt=0, description="Expense amount")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    payment_method: Optional[str] = Field(None, max_length=50, description="Payment method")
    receipt_number: Optional[str] = Field(None, max_length=100, description="Receipt number")
    vendor: Optional[str] = Field(None, max_length=200, description="Vendor name")
    date: datetime = Field(default_factory=datetime.utcnow, description="Expense date")
    is_recurring: bool = Field(default=False, description="Is this a recurring expense")
    recurring_period: Optional[str] = Field(None, description="Recurring period (monthly, yearly, etc.)")
    is_deductible: bool = Field(default=True, description="Is tax deductible")
    tax_category: Optional[str] = Field(None, max_length=100, description="Tax category")
    notes: Optional[str] = Field(None, description="Additional notes")

    @validator("category")
    def validate_category(cls, v):
        """Validate category field."""
        valid_categories = [
            "Inventory",
            "Shipping",
            "Supplies",
            "Fees",
            "Marketing",
            "Other",
        ]
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v

    @validator("currency")
    def validate_currency(cls, v):
        """Validate currency code."""
        if len(v) != 3:
            raise ValueError("Currency must be a 3-letter code (e.g., USD, EUR, GBP)")
        return v.upper()


class ExpenseCreate(ExpenseBase):
    """Schema for creating a new expense."""
    pass


class ExpenseUpdate(BaseModel):
    """Schema for updating an expense (all fields optional)."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=3)
    payment_method: Optional[str] = Field(None, max_length=50)
    receipt_number: Optional[str] = Field(None, max_length=100)
    vendor: Optional[str] = Field(None, max_length=200)
    date: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurring_period: Optional[str] = None
    is_deductible: Optional[bool] = None
    tax_category: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

    @validator("category")
    def validate_category(cls, v):
        """Validate category field."""
        if v is None:
            return v
        valid_categories = [
            "Inventory",
            "Shipping",
            "Supplies",
            "Fees",
            "Marketing",
            "Other",
        ]
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
        return v


class ExpenseResponse(ExpenseBase):
    """Schema for expense response."""

    id: int
    receipt_photo: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExpenseListResponse(BaseModel):
    """Schema for paginated expense list response."""

    expenses: List[ExpenseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ExpenseFilter(BaseModel):
    """Schema for filtering expenses."""

    category: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    is_recurring: Optional[bool] = None
    is_deductible: Optional[bool] = None
    vendor: Optional[str] = None
    search: Optional[str] = None


class ExpenseSummary(BaseModel):
    """Schema for expense summary/analytics."""

    total_expenses: float
    expense_count: int
    by_category: dict[str, float]
    by_month: dict[str, float]
    deductible_total: float
    non_deductible_total: float
