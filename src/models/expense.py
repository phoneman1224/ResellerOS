"""
Expense model for tracking business expenses.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from datetime import datetime
from typing import Optional

from src.core.database import Base


class Expense(Base):
    """Business expense model."""

    __tablename__ = "expenses"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Basic information
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False, index=True)
    # Categories: Inventory, Shipping, Supplies, Fees, Marketing, Other

    # Financial information
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")

    # Payment information
    payment_method = Column(String(50))  # Cash, Credit Card, PayPal, etc.
    receipt_number = Column(String(100))
    vendor = Column(String(200))

    # Metadata
    date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    is_recurring = Column(Integer, default=0)  # 0=No, 1=Yes (using Integer for SQLite)
    recurring_period = Column(String(20))  # monthly, yearly, etc.

    # Tax information
    is_deductible = Column(Integer, default=1)  # 1=Yes, 0=No
    tax_category = Column(String(100))

    # Notes and attachments
    notes = Column(Text)
    receipt_photo = Column(String(500))  # Filename of receipt photo

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_category_date', 'category', 'date'),
        Index('idx_date_amount', 'date', 'amount'),
    )

    def to_dict(self) -> dict:
        """Convert expense to dictionary.

        Returns:
            Dictionary representation of expense
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "amount": self.amount,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "receipt_number": self.receipt_number,
            "vendor": self.vendor,
            "date": self.date.isoformat() if self.date else None,
            "is_recurring": bool(self.is_recurring),
            "recurring_period": self.recurring_period,
            "is_deductible": bool(self.is_deductible),
            "tax_category": self.tax_category,
            "notes": self.notes,
            "receipt_photo": self.receipt_photo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @property
    def is_recurring_expense(self) -> bool:
        """Check if this is a recurring expense.

        Returns:
            True if recurring, False otherwise
        """
        return bool(self.is_recurring)

    @property
    def is_tax_deductible(self) -> bool:
        """Check if this expense is tax deductible.

        Returns:
            True if deductible, False otherwise
        """
        return bool(self.is_deductible)

    def __repr__(self) -> str:
        return f"<Expense(id={self.id}, title='{self.title}', amount=${self.amount:.2f})>"
