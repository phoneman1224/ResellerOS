"""
Inventory service for business logic operations.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from src.repositories.item_repository import ItemRepository
from src.models.item import Item
from src.schemas.item_schema import ItemCreate, ItemUpdate
from src.core.exceptions import NotFoundError, ValidationError, DuplicateError
from src.core.database import get_db

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for inventory management."""

    def __init__(self):
        self.repository = ItemRepository()

    def create_item(self, item_data: ItemCreate) -> Item:
        """Create a new inventory item.

        Args:
            item_data: Item creation data

        Returns:
            Created item

        Raises:
            ValidationError: If data is invalid
            DuplicateError: If SKU already exists
        """
        try:
            with get_db() as db:
                # Check for duplicate SKU
                if item_data.sku:
                    existing = self.repository.get_by_sku(db, item_data.sku)
                    if existing:
                        raise DuplicateError(f"Item with SKU '{item_data.sku}' already exists")

                # Create item
                item = self.repository.create(db, **item_data.model_dump())
                logger.info(f"Created item: {item.id} - {item.title}")
                return item
        except DuplicateError:
            raise
        except Exception as e:
            logger.error(f"Failed to create item: {e}")
            raise ValidationError(f"Failed to create item: {str(e)}")

    def get_item(self, item_id: int) -> Item:
        """Get item by ID.

        Args:
            item_id: Item ID

        Returns:
            Item

        Raises:
            NotFoundError: If item not found
        """
        try:
            with get_db() as db:
                return self.repository.get_by_id_or_fail(db, item_id)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get item {item_id}: {e}")
            raise

    def update_item(self, item_id: int, item_data: ItemUpdate) -> Item:
        """Update an item.

        Args:
            item_id: Item ID
            item_data: Update data

        Returns:
            Updated item

        Raises:
            NotFoundError: If item not found
            ValidationError: If update fails
        """
        try:
            with get_db() as db:
                # Get existing item
                item = self.repository.get_by_id_or_fail(db, item_id)

                # Check for SKU conflict
                if item_data.sku and item_data.sku != item.sku:
                    existing = self.repository.get_by_sku(db, item_data.sku)
                    if existing and existing.id != item_id:
                        raise DuplicateError(f"Item with SKU '{item_data.sku}' already exists")

                # Update only provided fields
                update_dict = item_data.model_dump(exclude_unset=True)
                updated_item = self.repository.update(db, item_id, **update_dict)
                logger.info(f"Updated item: {item_id}")
                return updated_item
        except (NotFoundError, DuplicateError):
            raise
        except Exception as e:
            logger.error(f"Failed to update item {item_id}: {e}")
            raise ValidationError(f"Failed to update item: {str(e)}")

    def delete_item(self, item_id: int) -> bool:
        """Delete an item.

        Args:
            item_id: Item ID

        Returns:
            True if deleted

        Raises:
            NotFoundError: If item not found
        """
        try:
            with get_db() as db:
                self.repository.delete(db, item_id)
                logger.info(f"Deleted item: {item_id}")
                return True
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete item {item_id}: {e}")
            raise

    def list_items(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Item]:
        """List items with filters.

        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            status: Filter by status
            category: Filter by category
            search: Search query

        Returns:
            List of items
        """
        try:
            with get_db() as db:
                if search:
                    return self.repository.search(
                        db, search, status=status, category=category, skip=skip, limit=limit
                    )
                elif status or category:
                    query = db.query(Item)
                    if status:
                        query = query.filter(Item.status == status)
                    if category:
                        query = query.filter(Item.category == category)
                    return query.order_by(Item.created_at.desc()).offset(skip).limit(limit).all()
                else:
                    return self.repository.get_all(
                        db, skip=skip, limit=limit, order_by="created_at", order_desc=True
                    )
        except Exception as e:
            logger.error(f"Failed to list items: {e}")
            return []

    def add_photo(self, item_id: int, filename: str) -> Item:
        """Add a photo to an item.

        Args:
            item_id: Item ID
            filename: Photo filename

        Returns:
            Updated item

        Raises:
            NotFoundError: If item not found
        """
        try:
            with get_db() as db:
                item = self.repository.get_by_id_or_fail(db, item_id)
                item.add_photo(filename)
                db.flush()
                db.refresh(item)
                logger.info(f"Added photo to item {item_id}: {filename}")
                return item
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to add photo to item {item_id}: {e}")
            raise

    def remove_photo(self, item_id: int, filename: str) -> Item:
        """Remove a photo from an item.

        Args:
            item_id: Item ID
            filename: Photo filename

        Returns:
            Updated item

        Raises:
            NotFoundError: If item not found
        """
        try:
            with get_db() as db:
                item = self.repository.get_by_id_or_fail(db, item_id)
                item.remove_photo(filename)
                db.flush()
                db.refresh(item)
                logger.info(f"Removed photo from item {item_id}: {filename}")
                return item
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to remove photo from item {item_id}: {e}")
            raise

    def update_status(self, item_id: int, new_status: str) -> Item:
        """Update item status.

        Args:
            item_id: Item ID
            new_status: New status

        Returns:
            Updated item

        Raises:
            NotFoundError: If item not found
        """
        try:
            with get_db() as db:
                item = self.repository.get_by_id_or_fail(db, item_id)

                # Update timestamps based on status
                if new_status == "Listed" and not item.listed_at:
                    item.listed_at = datetime.utcnow()
                elif new_status == "Sold" and not item.sold_at:
                    item.sold_at = datetime.utcnow()

                updated_item = self.repository.update(db, item_id, status=new_status)
                logger.info(f"Updated item {item_id} status to {new_status}")
                return updated_item
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update status for item {item_id}: {e}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """Get inventory statistics.

        Returns:
            Dictionary with statistics
        """
        try:
            with get_db() as db:
                total_items = self.repository.count(db)
                by_status = self.repository.count_by_status(db)
                by_category = self.repository.count_by_category(db)
                inventory_value = self.repository.get_inventory_value(db)

                return {
                    "total_items": total_items,
                    "by_status": by_status,
                    "by_category": by_category,
                    "inventory_value": inventory_value,
                }
        except Exception as e:
            logger.error(f"Failed to get inventory statistics: {e}")
            return {
                "total_items": 0,
                "by_status": {},
                "by_category": {},
                "inventory_value": {},
            }

    def get_recent_items(self, days: int = 7, limit: int = 50) -> List[Item]:
        """Get recently created items.

        Args:
            days: Number of days to look back
            limit: Maximum number of items

        Returns:
            List of recent items
        """
        try:
            with get_db() as db:
                return self.repository.get_recent_items(db, days=days, limit=limit)
        except Exception as e:
            logger.error(f"Failed to get recent items: {e}")
            return []
