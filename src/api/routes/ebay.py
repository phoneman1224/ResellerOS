"""
eBay integration API routes.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from src.integrations.ebay.auth import EbayAuth
from src.integrations.ebay.inventory_api import EbayInventoryAPI
from src.core.exceptions import EbayAuthError, EbayAPIError

logger = logging.getLogger(__name__)
router = APIRouter()

ebay_auth = EbayAuth()
ebay_api = EbayInventoryAPI()


@router.get("/auth-status")
async def get_auth_status():
    """Check eBay authentication status.

    Returns:
        Authentication status
    """
    try:
        is_authenticated = ebay_auth.is_authenticated()

        return {
            "success": True,
            "data": {
                "authenticated": is_authenticated,
                "status": "connected" if is_authenticated else "not_connected",
            },
        }
    except Exception as e:
        logger.error(f"Failed to check eBay auth status: {e}")
        return {
            "success": True,
            "data": {
                "authenticated": False,
                "status": "error",
                "error": str(e),
            },
        }


@router.post("/auth/start")
async def start_auth():
    """Start eBay OAuth flow.

    Returns:
        Authorization URL
    """
    try:
        auth_url = ebay_auth.get_authorization_url()

        return {
            "success": True,
            "data": {
                "auth_url": auth_url,
                "message": "Please visit the URL to authorize"
            },
        }
    except EbayAuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start eBay auth: {e}")
        raise HTTPException(status_code=500, detail="Failed to start authentication")


@router.post("/auth/login")
async def login():
    """Complete eBay OAuth flow.

    Returns:
        Success status
    """
    try:
        success = ebay_auth.start_oauth_flow()

        if success:
            return {
                "success": True,
                "message": "Successfully authenticated with eBay",
            }
        else:
            raise HTTPException(status_code=400, detail="Authentication failed")

    except EbayAuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"eBay login failed: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/auth/logout")
async def logout():
    """Logout from eBay.

    Returns:
        Success status
    """
    try:
        ebay_auth.logout()

        return {
            "success": True,
            "message": "Successfully logged out from eBay",
        }
    except Exception as e:
        logger.error(f"eBay logout failed: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")


@router.get("/inventory/items")
async def get_ebay_items(limit: int = 25, offset: int = 0):
    """Get eBay inventory items.

    Args:
        limit: Number of items to return
        offset: Offset for pagination

    Returns:
        eBay inventory items
    """
    try:
        result = ebay_api.get_inventory_items(limit=limit, offset=offset)

        return {
            "success": True,
            "data": result,
        }
    except EbayAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except EbayAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get eBay items: {e}")
        raise HTTPException(status_code=500, detail="Failed to get items")


@router.get("/inventory/item/{sku}")
async def get_ebay_item(sku: str):
    """Get eBay inventory item by SKU.

    Args:
        sku: Item SKU

    Returns:
        eBay item data
    """
    try:
        item = ebay_api.get_inventory_item(sku)

        return {
            "success": True,
            "data": item,
        }
    except EbayAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except EbayAPIError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get eBay item {sku}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get item")


@router.get("/stats")
async def get_ebay_stats():
    """Get eBay API usage statistics.

    Returns:
        API usage statistics
    """
    try:
        stats = ebay_api.get_api_stats()

        return {
            "success": True,
            "data": stats,
        }
    except Exception as e:
        logger.error(f"Failed to get eBay stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")
