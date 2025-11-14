"""
Pydantic schemas for Item validation and serialization.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class ItemBase(BaseModel):
    """Base item schema with common fields."""

    title: str = Field(..., min_length=1, max_length=200, description="Item title")
    category: Optional[str] = Field(None, max_length=100, description="Item category")
    description: Optional[str] = Field(None, description="Item description")
    notes: Optional[str] = Field(None, description="Internal notes")
    cost: float = Field(default=0.0, ge=0, description="Item cost")
    price: Optional[float] = Field(None, ge=0, description="Listing price")
    shipping_cost: Optional[float] = Field(default=0.0, ge=0, description="Shipping cost")
    status: str = Field(default="Draft", description="Item status")
    condition: Optional[str] = Field(None, description="Item condition")
    quantity: int = Field(default=1, ge=1, description="Quantity available")
    location: Optional[str] = Field(None, max_length=100, description="Storage location")
    sku: Optional[str] = Field(None, max_length=100, description="SKU")

    @validator("status")
    def validate_status(cls, v):
        """Validate status field."""
        valid_statuses = ["Draft", "Ready", "Listed", "Sold", "Archived"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

    @validator("condition")
    def validate_condition(cls, v):
        """Validate condition field."""
        if v is None:
            return v
        valid_conditions = ["New", "Like New", "Good", "Fair", "Poor"]
        if v not in valid_conditions:
            raise ValueError(f"Condition must be one of: {', '.join(valid_conditions)}")
        return v


class ItemCreate(ItemBase):
    """Schema for creating a new item."""
    pass


class ItemUpdate(BaseModel):
    """Schema for updating an item (all fields optional)."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    notes: Optional[str] = None
    cost: Optional[float] = Field(None, ge=0)
    price: Optional[float] = Field(None, ge=0)
    shipping_cost: Optional[float] = Field(None, ge=0)
    status: Optional[str] = None
    condition: Optional[str] = None
    quantity: Optional[int] = Field(None, ge=1)
    location: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    ebay_id: Optional[str] = None
    ebay_listing_url: Optional[str] = None
    ebay_status: Optional[str] = None
    ai_title: Optional[str] = None
    ai_description: Optional[str] = None
    ai_price: Optional[float] = None
    ai_category: Optional[str] = None
    seo_score: Optional[float] = None

    @validator("status")
    def validate_status(cls, v):
        """Validate status field."""
        if v is None:
            return v
        valid_statuses = ["Draft", "Ready", "Listed", "Sold", "Archived"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v


class ItemResponse(ItemBase):
    """Schema for item response."""

    id: int
    photos: List[str] = []
    ebay_id: Optional[str] = None
    ebay_listing_url: Optional[str] = None
    ebay_status: Optional[str] = None
    ai_title: Optional[str] = None
    ai_description: Optional[str] = None
    ai_price: Optional[float] = None
    ai_category: Optional[str] = None
    seo_score: Optional[float] = None
    profit: float
    profit_margin: float
    net_profit: float
    created_at: datetime
    updated_at: datetime
    listed_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    """Schema for paginated item list response."""

    items: List[ItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ItemFilter(BaseModel):
    """Schema for filtering items."""

    status: Optional[str] = None
    category: Optional[str] = None
    min_cost: Optional[float] = None
    max_cost: Optional[float] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search: Optional[str] = None
    has_photos: Optional[bool] = None
    listed_after: Optional[datetime] = None
    listed_before: Optional[datetime] = None


class AIPricingSuggestion(BaseModel):
    """Schema for AI pricing suggestions."""

    suggested_price: float = Field(..., ge=0, description="AI suggested price")
    reasoning: str = Field(..., description="Reasoning for the suggestion")
    confidence: str = Field(..., description="Confidence level (high/medium/low)")
    comparable_items: Optional[List[dict]] = Field(default=[], description="Comparable items from market research")


class AITitleSuggestion(BaseModel):
    """Schema for AI title suggestions."""

    suggested_title: str = Field(..., max_length=80, description="AI suggested title")
    seo_score: float = Field(..., ge=0, le=100, description="SEO score (0-100)")
    reasoning: str = Field(..., description="Reasoning for the suggestion")
    improvements: List[str] = Field(default=[], description="List of improvements made")
