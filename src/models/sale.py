"""
Sale model for tracking completed sales.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index
from datetime import datetime
from typing import Optional

from src.core.database import Base


class Sale(Base):
    """Sales transaction model."""

    __tablename__ = "sales"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Item reference
    item_id = Column(Integer, ForeignKey("items.id", ondelete="SET NULL"), index=True)
    item_title = Column(String(200), nullable=False)  # Cached for historical records
    item_sku = Column(String(100))

    # Sale information
    sale_price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    currency = Column(String(3), default="USD")

    # Costs
    item_cost = Column(Float, default=0.0)
    shipping_cost = Column(Float, default=0.0)
    ebay_fees = Column(Float, default=0.0)
    payment_fees = Column(Float, default=0.0)
    other_fees = Column(Float, default=0.0)

    # Platform information
    platform = Column(String(50), default="eBay", index=True)  # eBay, Poshmark, Mercari, etc.
    platform_order_id = Column(String(100), unique=True, index=True)
    platform_transaction_id = Column(String(100))

    # Buyer information
    buyer_username = Column(String(100))
    buyer_location = Column(String(200))

    # Shipping information
    shipping_method = Column(String(100))
    tracking_number = Column(String(100))
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)

    # Status
    status = Column(String(50), default="Pending", nullable=False, index=True)
    # Pending, Paid, Shipped, Delivered, Completed, Cancelled, Refunded

    # Payment information
    payment_method = Column(String(50))
    payment_date = Column(DateTime)

    # Notes
    notes = Column(Text)

    # Timestamps
    sale_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_sale_date_platform', 'sale_date', 'platform'),
        Index('idx_status_sale_date', 'status', 'sale_date'),
    )

    @property
    def total_revenue(self) -> float:
        """Calculate total revenue.

        Returns:
            Total revenue (sale_price * quantity)
        """
        return self.sale_price * self.quantity

    @property
    def total_costs(self) -> float:
        """Calculate total costs.

        Returns:
            Sum of all costs
        """
        return (
            (self.item_cost * self.quantity) +
            (self.shipping_cost or 0.0) +
            (self.ebay_fees or 0.0) +
            (self.payment_fees or 0.0) +
            (self.other_fees or 0.0)
        )

    @property
    def profit(self) -> float:
        """Calculate profit.

        Returns:
            Profit (revenue - costs)
        """
        return self.total_revenue - self.total_costs

    @property
    def profit_margin(self) -> float:
        """Calculate profit margin percentage.

        Returns:
            Profit margin as percentage (0-100)
        """
        if self.total_revenue == 0:
            return 0.0
        return (self.profit / self.total_revenue) * 100

    @property
    def roi(self) -> float:
        """Calculate return on investment.

        Returns:
            ROI as percentage
        """
        total_item_cost = self.item_cost * self.quantity
        if total_item_cost == 0:
            return 0.0
        return (self.profit / total_item_cost) * 100

    def calculate_ebay_fees(self) -> float:
        """Calculate estimated eBay fees (13% of sale price).

        Returns:
            Estimated eBay fees
        """
        return self.total_revenue * 0.13

    def calculate_payment_fees(self, rate: float = 0.029, fixed: float = 0.30) -> float:
        """Calculate PayPal/payment processor fees.

        Args:
            rate: Percentage rate (default 2.9%)
            fixed: Fixed fee per transaction (default $0.30)

        Returns:
            Estimated payment fees
        """
        return (self.total_revenue * rate) + fixed

    def to_dict(self) -> dict:
        """Convert sale to dictionary.

        Returns:
            Dictionary representation of sale
        """
        return {
            "id": self.id,
            "item_id": self.item_id,
            "item_title": self.item_title,
            "item_sku": self.item_sku,
            "sale_price": self.sale_price,
            "quantity": self.quantity,
            "currency": self.currency,
            "item_cost": self.item_cost,
            "shipping_cost": self.shipping_cost,
            "ebay_fees": self.ebay_fees,
            "payment_fees": self.payment_fees,
            "other_fees": self.other_fees,
            "platform": self.platform,
            "platform_order_id": self.platform_order_id,
            "platform_transaction_id": self.platform_transaction_id,
            "buyer_username": self.buyer_username,
            "buyer_location": self.buyer_location,
            "shipping_method": self.shipping_method,
            "tracking_number": self.tracking_number,
            "shipped_at": self.shipped_at.isoformat() if self.shipped_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "status": self.status,
            "payment_method": self.payment_method,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "notes": self.notes,
            "sale_date": self.sale_date.isoformat() if self.sale_date else None,
            "total_revenue": self.total_revenue,
            "total_costs": self.total_costs,
            "profit": self.profit,
            "profit_margin": self.profit_margin,
            "roi": self.roi,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<Sale(id={self.id}, item='{self.item_title}', price=${self.sale_price:.2f})>"
