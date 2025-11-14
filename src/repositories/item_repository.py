"""
Repository for Item model operations.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta
import logging

from src.models.item import Item
from src.repositories.base_repository import BaseRepository
from src.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class ItemRepository(BaseRepository[Item]):
    """Repository for Item model with specialized queries."""

    def __init__(self):
        super().__init__(Item)

    def search(
        self,
        db: Session,
        query: str,
        status: Optional[str] = None,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Item]:
        """Search items by title, description, or SKU.

        Args:
            db: Database session
            query: Search query string
            status: Filter by status
            category: Filter by category
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching items
        """
        try:
            q = db.query(Item)

            # Search filter
            if query:
                search_filter = or_(
                    Item.title.ilike(f"%{query}%"),
                    Item.description.ilike(f"%{query}%"),
                    Item.sku.ilike(f"%{query}%"),
                )
                q = q.filter(search_filter)

            # Status filter
            if status:
                q = q.filter(Item.status == status)

            # Category filter
            if category:
                q = q.filter(Item.category == category)

            return q.order_by(Item.created_at.desc()).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to search items: {e}")
            raise DatabaseError(f"Search failed: {str(e)}")

    def get_by_status(
        self,
        db: Session,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Item]:
        """Get items by status.

        Args:
            db: Database session
            status: Item status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of items with specified status
        """
        return self.find_all(db, status=status)

    def get_by_category(
        self,
        db: Session,
        category: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Item]:
        """Get items by category.

        Args:
            db: Database session
            category: Item category
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of items in specified category
        """
        try:
            return (
                db.query(Item)
                .filter(Item.category == category)
                .order_by(Item.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(f"Failed to get items by category: {e}")
            raise DatabaseError(f"Failed to retrieve items: {str(e)}")

    def get_by_ebay_id(self, db: Session, ebay_id: str) -> Optional[Item]:
        """Get item by eBay ID.

        Args:
            db: Database session
            ebay_id: eBay listing ID

        Returns:
            Item or None
        """
        return self.find_one(db, ebay_id=ebay_id)

    def get_by_sku(self, db: Session, sku: str) -> Optional[Item]:
        """Get item by SKU.

        Args:
            db: Database session
            sku: Item SKU

        Returns:
            Item or None
        """
        return self.find_one(db, sku=sku)

    def get_recent_items(
        self,
        db: Session,
        days: int = 7,
        limit: int = 50,
    ) -> List[Item]:
        """Get recently created items.

        Args:
            db: Database session
            days: Number of days to look back
            limit: Maximum number of items to return

        Returns:
            List of recent items
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return (
                db.query(Item)
                .filter(Item.created_at >= cutoff_date)
                .order_by(Item.created_at.desc())
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(f"Failed to get recent items: {e}")
            raise DatabaseError(f"Failed to retrieve items: {str(e)}")

    def get_profitable_items(
        self,
        db: Session,
        min_margin: float = 30.0,
        limit: int = 100,
    ) -> List[Item]:
        """Get items with profit margin above threshold.

        Args:
            db: Database session
            min_margin: Minimum profit margin percentage
            limit: Maximum number of items to return

        Returns:
            List of profitable items
        """
        try:
            # Calculate profit margin: ((price - cost - shipping) / price) * 100
            items = (
                db.query(Item)
                .filter(
                    and_(
                        Item.price.isnot(None),
                        Item.price > 0,
                        Item.cost.isnot(None),
                    )
                )
                .all()
            )

            # Filter by profit margin
            profitable = [
                item for item in items if item.profit_margin >= min_margin
            ]

            # Sort by profit margin descending
            profitable.sort(key=lambda x: x.profit_margin, reverse=True)

            return profitable[:limit]
        except Exception as e:
            logger.error(f"Failed to get profitable items: {e}")
            raise DatabaseError(f"Failed to retrieve items: {str(e)}")

    def get_items_without_photos(
        self,
        db: Session,
        limit: int = 100,
    ) -> List[Item]:
        """Get items that don't have photos.

        Args:
            db: Database session
            limit: Maximum number of items to return

        Returns:
            List of items without photos
        """
        try:
            return (
                db.query(Item)
                .filter(or_(Item.photos.is_(None), Item.photos == "null", Item.photos == "[]"))
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(f"Failed to get items without photos: {e}")
            raise DatabaseError(f"Failed to retrieve items: {str(e)}")

    def count_by_status(self, db: Session) -> dict:
        """Count items grouped by status.

        Args:
            db: Database session

        Returns:
            Dictionary with status counts
        """
        try:
            result = (
                db.query(Item.status, func.count(Item.id))
                .group_by(Item.status)
                .all()
            )
            return {status: count for status, count in result}
        except Exception as e:
            logger.error(f"Failed to count items by status: {e}")
            raise DatabaseError(f"Failed to count items: {str(e)}")

    def count_by_category(self, db: Session) -> dict:
        """Count items grouped by category.

        Args:
            db: Database session

        Returns:
            Dictionary with category counts
        """
        try:
            result = (
                db.query(Item.category, func.count(Item.id))
                .group_by(Item.category)
                .all()
            )
            return {category or "Uncategorized": count for category, count in result}
        except Exception as e:
            logger.error(f"Failed to count items by category: {e}")
            raise DatabaseError(f"Failed to count items: {str(e)}")

    def get_inventory_value(self, db: Session, status: Optional[str] = None) -> dict:
        """Calculate total inventory value.

        Args:
            db: Database session
            status: Optional status filter

        Returns:
            Dictionary with inventory statistics
        """
        try:
            query = db.query(Item)
            if status:
                query = query.filter(Item.status == status)

            items = query.all()

            total_cost = sum(item.cost * item.quantity for item in items)
            total_potential_revenue = sum(
                (item.price or 0) * item.quantity for item in items if item.price
            )
            total_potential_profit = sum(item.profit for item in items if item.price)

            return {
                "total_items": len(items),
                "total_cost": round(total_cost, 2),
                "total_potential_revenue": round(total_potential_revenue, 2),
                "total_potential_profit": round(total_potential_profit, 2),
                "average_cost": round(total_cost / len(items), 2) if items else 0,
            }
        except Exception as e:
            logger.error(f"Failed to calculate inventory value: {e}")
            raise DatabaseError(f"Failed to calculate inventory value: {str(e)}")
