"""
Item model for inventory management.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Index
from datetime import datetime
import json
from typing import List, Optional

from src.core.database import Base


class Item(Base):
    """Inventory item model."""

    __tablename__ = "items"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Basic information
    title = Column(String(200), nullable=False, index=True)
    category = Column(String(100), index=True)
    description = Column(Text)
    notes = Column(Text)

    # Financial information
    cost = Column(Float, default=0.0, nullable=False)
    price = Column(Float, default=0.0)
    shipping_cost = Column(Float, default=0.0)

    # Status tracking
    status = Column(
        String(50),
        default="Draft",
        nullable=False,
        index=True
    )  # Draft, Ready, Listed, Sold, Archived

    # Photos (JSON array of filenames)
    photos = Column(Text)

    # eBay integration
    ebay_id = Column(String(100), unique=True, index=True)
    ebay_listing_url = Column(String(500))
    ebay_status = Column(String(50))  # Active, Ended, Sold

    # AI suggestions
    ai_title = Column(String(200))
    ai_description = Column(Text)
    ai_price = Column(Float)
    ai_category = Column(String(100))
    seo_score = Column(Float)

    # Metadata
    sku = Column(String(100), unique=True, index=True)
    condition = Column(String(50))  # New, Like New, Good, Fair, Poor
    quantity = Column(Integer, default=1)
    location = Column(String(100))  # Storage location

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    listed_at = Column(DateTime)
    sold_at = Column(DateTime)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_category_status', 'category', 'status'),
    )

    def get_photos(self) -> List[str]:
        """Get list of photo filenames.

        Returns:
            List of photo filenames
        """
        if not self.photos:
            return []
        try:
            return json.loads(self.photos)
        except json.JSONDecodeError:
            return []

    def set_photos(self, photo_list: List[str]):
        """Set photo filenames.

        Args:
            photo_list: List of photo filenames
        """
        self.photos = json.dumps(photo_list) if photo_list else None

    def add_photo(self, filename: str):
        """Add a photo filename.

        Args:
            filename: Photo filename to add
        """
        photos = self.get_photos()
        if filename not in photos:
            photos.append(filename)
            self.set_photos(photos)

    def remove_photo(self, filename: str):
        """Remove a photo filename.

        Args:
            filename: Photo filename to remove
        """
        photos = self.get_photos()
        if filename in photos:
            photos.remove(filename)
            self.set_photos(photos)

    @property
    def profit(self) -> float:
        """Calculate profit for this item.

        Returns:
            Profit amount (price - cost - shipping_cost)
        """
        if not self.price:
            return 0.0
        return self.price - self.cost - (self.shipping_cost or 0.0)

    @property
    def profit_margin(self) -> float:
        """Calculate profit margin percentage.

        Returns:
            Profit margin as percentage (0-100)
        """
        if not self.price or self.price == 0:
            return 0.0
        return (self.profit / self.price) * 100

    @property
    def ebay_fees(self) -> float:
        """Estimate eBay fees (13% of final price).

        Returns:
            Estimated eBay fees
        """
        if not self.price:
            return 0.0
        return self.price * 0.13

    @property
    def net_profit(self) -> float:
        """Calculate net profit after eBay fees.

        Returns:
            Net profit after fees
        """
        return self.profit - self.ebay_fees

    def is_profitable(self, min_margin: float = 30.0) -> bool:
        """Check if item meets minimum profit margin.

        Args:
            min_margin: Minimum profit margin percentage (default 30%)

        Returns:
            True if profit margin meets or exceeds minimum
        """
        return self.profit_margin >= min_margin

    def to_dict(self) -> dict:
        """Convert item to dictionary.

        Returns:
            Dictionary representation of item
        """
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "description": self.description,
            "notes": self.notes,
            "cost": self.cost,
            "price": self.price,
            "shipping_cost": self.shipping_cost,
            "status": self.status,
            "photos": self.get_photos(),
            "ebay_id": self.ebay_id,
            "ebay_listing_url": self.ebay_listing_url,
            "ebay_status": self.ebay_status,
            "ai_title": self.ai_title,
            "ai_description": self.ai_description,
            "ai_price": self.ai_price,
            "ai_category": self.ai_category,
            "seo_score": self.seo_score,
            "sku": self.sku,
            "condition": self.condition,
            "quantity": self.quantity,
            "location": self.location,
            "profit": self.profit,
            "profit_margin": self.profit_margin,
            "net_profit": self.net_profit,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "listed_at": self.listed_at.isoformat() if self.listed_at else None,
            "sold_at": self.sold_at.isoformat() if self.sold_at else None,
        }

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, title='{self.title}', status='{self.status}')>"
