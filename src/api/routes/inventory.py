"""
Inventory API routes.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import logging
import os
import uuid
from pathlib import Path

from src.services.inventory_service import InventoryService
from src.schemas.item_schema import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    ItemFilter,
)
from src.core.exceptions import NotFoundError, ValidationError, DuplicateError
from src.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()
inventory_service = InventoryService()


@router.post("/items", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    """Create a new inventory item.

    Args:
        item: Item creation data

    Returns:
        Created item

    Raises:
        HTTPException: If creation fails
    """
    try:
        created_item = inventory_service.create_item(item)
        return created_item.to_dict()
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create item: {e}")
        raise HTTPException(status_code=500, detail="Failed to create item")


@router.get("/items", response_model=List[ItemResponse])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
):
    """List inventory items with filters.

    Args:
        skip: Number of items to skip
        limit: Maximum items to return
        status: Filter by status
        category: Filter by category
        search: Search query

    Returns:
        List of items
    """
    try:
        items = inventory_service.list_items(
            skip=skip,
            limit=limit,
            status=status,
            category=category,
            search=search,
        )
        return [item.to_dict() for item in items]
    except Exception as e:
        logger.error(f"Failed to list items: {e}")
        raise HTTPException(status_code=500, detail="Failed to list items")


@router.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    """Get item by ID.

    Args:
        item_id: Item ID

    Returns:
        Item details

    Raises:
        HTTPException: If item not found
    """
    try:
        item = inventory_service.get_item(item_id)
        return item.to_dict()
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Failed to get item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get item")


@router.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: ItemUpdate):
    """Update an item.

    Args:
        item_id: Item ID
        item: Update data

    Returns:
        Updated item

    Raises:
        HTTPException: If update fails
    """
    try:
        updated_item = inventory_service.update_item(item_id, item)
        return updated_item.to_dict()
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except DuplicateError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update item")


@router.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """Delete an item.

    Args:
        item_id: Item ID

    Returns:
        Success message

    Raises:
        HTTPException: If deletion fails
    """
    try:
        inventory_service.delete_item(item_id)
        return {"success": True, "message": "Item deleted successfully"}
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Failed to delete item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete item")


@router.post("/items/{item_id}/photos")
async def upload_photo(item_id: int, file: UploadFile = File(...)):
    """Upload a photo for an item.

    Args:
        item_id: Item ID
        file: Image file

    Returns:
        Success message with filename

    Raises:
        HTTPException: If upload fails
    """
    try:
        # Validate file type
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )

        # Generate unique filename
        filename = f"{uuid.uuid4()}{file_ext}"
        filepath = os.path.join(settings.upload_dir, filename)

        # Save file
        with open(filepath, "wb") as f:
            content = await file.read()
            # Check file size
            if len(content) > settings.max_upload_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Max size: {settings.max_upload_size / 1024 / 1024}MB"
                )
            f.write(content)

        # Add photo to item
        inventory_service.add_photo(item_id, filename)

        return {
            "success": True,
            "filename": filename,
            "message": "Photo uploaded successfully"
        }

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload photo for item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload photo")


@router.delete("/items/{item_id}/photos/{filename}")
async def delete_photo(item_id: int, filename: str):
    """Delete a photo from an item.

    Args:
        item_id: Item ID
        filename: Photo filename

    Returns:
        Success message

    Raises:
        HTTPException: If deletion fails
    """
    try:
        # Remove from item
        inventory_service.remove_photo(item_id, filename)

        # Delete file
        filepath = os.path.join(settings.upload_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        return {"success": True, "message": "Photo deleted successfully"}

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Failed to delete photo {filename} from item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete photo")


@router.put("/items/{item_id}/status")
async def update_status(item_id: int, status: str):
    """Update item status.

    Args:
        item_id: Item ID
        status: New status

    Returns:
        Updated item

    Raises:
        HTTPException: If update fails
    """
    try:
        updated_item = inventory_service.update_status(item_id, status)
        return updated_item.to_dict()
    except NotFoundError:
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        logger.error(f"Failed to update status for item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update status")


@router.get("/statistics")
async def get_statistics():
    """Get inventory statistics.

    Returns:
        Statistics data
    """
    try:
        stats = inventory_service.get_statistics()
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")
