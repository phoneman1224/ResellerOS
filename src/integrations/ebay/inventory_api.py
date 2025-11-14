"""
eBay Inventory API client.
"""
import requests
import logging
from typing import Dict, Any, Optional, List

from src.config.settings import settings
from src.integrations.ebay.auth import EbayAuth
from src.integrations.ebay.rate_limiter import RateLimiter, RequestTracker
from src.core.exceptions import EbayAPIError, EbayAuthError, EbayRateLimitError

logger = logging.getLogger(__name__)


class EbayInventoryAPI:
    """Client for eBay Inventory API."""

    def __init__(self):
        """Initialize eBay Inventory API client."""
        self.auth = EbayAuth()
        self.base_url = f"{settings.ebay_api_base_url}/sell/inventory/v1"
        self.rate_limiter = RateLimiter(calls_per_second=5, burst=10)
        self.request_tracker = RequestTracker()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API request.

        Returns:
            Headers dictionary

        Raises:
            EbayAuthError: If not authenticated
        """
        access_token = self.auth.get_access_token()
        if not access_token:
            raise EbayAuthError("Not authenticated with eBay. Please login first.")

        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make API request with rate limiting.

        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request body data
            params: Query parameters

        Returns:
            Response data

        Raises:
            EbayAPIError: If request fails
            EbayRateLimitError: If rate limit exceeded
        """
        if not self.rate_limiter.acquire():
            raise EbayRateLimitError("eBay API rate limit exceeded. Please try again later.")

        url = f"{self.base_url}/{endpoint}"

        try:
            headers = self._get_headers()

            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=30,
            )

            # Track request
            self.request_tracker.record_request(endpoint, response.status_code)

            # Handle response
            if response.status_code == 204:
                return {}
            elif 200 <= response.status_code < 300:
                return response.json() if response.text else {}
            elif response.status_code == 401:
                # Try to refresh token and retry once
                logger.warning("Access token expired, attempting refresh...")
                self.auth.refresh_access_token()
                headers = self._get_headers()

                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                    params=params,
                    timeout=30,
                )

                if 200 <= response.status_code < 300:
                    return response.json() if response.text else {}
                else:
                    raise EbayAuthError("Authentication failed after token refresh")
            elif response.status_code == 429:
                raise EbayRateLimitError("eBay API rate limit exceeded")
            else:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get("errors", [{}])[0].get("message", error_msg)
                except:
                    pass

                raise EbayAPIError(f"eBay API error ({response.status_code}): {error_msg}")

        except (EbayAPIError, EbayAuthError, EbayRateLimitError):
            raise
        except requests.RequestException as e:
            logger.error(f"eBay API request failed: {e}")
            raise EbayAPIError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in eBay API request: {e}")
            raise EbayAPIError(f"Unexpected error: {str(e)}")

    def create_inventory_item(self, sku: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update inventory item.

        Args:
            sku: Item SKU
            item_data: Item data following eBay schema

        Returns:
            Response data

        Raises:
            EbayAPIError: If creation fails
        """
        try:
            logger.info(f"Creating eBay inventory item with SKU: {sku}")
            result = self._make_request("PUT", f"inventory_item/{sku}", data=item_data)
            logger.info(f"Successfully created inventory item: {sku}")
            return result
        except Exception as e:
            logger.error(f"Failed to create inventory item {sku}: {e}")
            raise

    def get_inventory_item(self, sku: str) -> Dict[str, Any]:
        """Get inventory item by SKU.

        Args:
            sku: Item SKU

        Returns:
            Item data

        Raises:
            EbayAPIError: If retrieval fails
        """
        try:
            return self._make_request("GET", f"inventory_item/{sku}")
        except Exception as e:
            logger.error(f"Failed to get inventory item {sku}: {e}")
            raise

    def delete_inventory_item(self, sku: str) -> bool:
        """Delete inventory item.

        Args:
            sku: Item SKU

        Returns:
            True if successful

        Raises:
            EbayAPIError: If deletion fails
        """
        try:
            logger.info(f"Deleting eBay inventory item: {sku}")
            self._make_request("DELETE", f"inventory_item/{sku}")
            logger.info(f"Successfully deleted inventory item: {sku}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete inventory item {sku}: {e}")
            raise

    def create_offer(self, offer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create listing offer.

        Args:
            offer_data: Offer data following eBay schema

        Returns:
            Offer response with offer_id

        Raises:
            EbayAPIError: If creation fails
        """
        try:
            logger.info("Creating eBay listing offer")
            result = self._make_request("POST", "offer", data=offer_data)
            offer_id = result.get("offerId")
            logger.info(f"Successfully created offer: {offer_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to create offer: {e}")
            raise

    def publish_offer(self, offer_id: str) -> Dict[str, Any]:
        """Publish an offer (create listing).

        Args:
            offer_id: Offer ID to publish

        Returns:
            Listing details

        Raises:
            EbayAPIError: If publishing fails
        """
        try:
            logger.info(f"Publishing eBay offer: {offer_id}")
            result = self._make_request("POST", f"offer/{offer_id}/publish")
            listing_id = result.get("listingId")
            logger.info(f"Successfully published offer {offer_id} as listing {listing_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to publish offer {offer_id}: {e}")
            raise

    def get_offers(self, sku: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get offers, optionally filtered by SKU.

        Args:
            sku: Optional SKU to filter by

        Returns:
            List of offers

        Raises:
            EbayAPIError: If retrieval fails
        """
        try:
            params = {"sku": sku} if sku else {}
            result = self._make_request("GET", "offer", params=params)
            return result.get("offers", [])
        except Exception as e:
            logger.error(f"Failed to get offers: {e}")
            raise

    def get_inventory_items(
        self, limit: int = 25, offset: int = 0
    ) -> Dict[str, Any]:
        """Get inventory items.

        Args:
            limit: Number of items to return
            offset: Offset for pagination

        Returns:
            Inventory items response

        Raises:
            EbayAPIError: If retrieval fails
        """
        try:
            params = {"limit": limit, "offset": offset}
            return self._make_request("GET", "inventory_item", params=params)
        except Exception as e:
            logger.error(f"Failed to get inventory items: {e}")
            raise

    def bulk_create_or_replace_inventory(
        self, items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Bulk create or replace inventory items.

        Args:
            items: List of inventory item requests

        Returns:
            Bulk response

        Raises:
            EbayAPIError: If bulk operation fails
        """
        try:
            logger.info(f"Bulk creating {len(items)} inventory items")
            data = {"requests": items}
            result = self._make_request("POST", "bulk_create_or_replace_inventory_item", data=data)
            logger.info(f"Bulk creation completed")
            return result
        except Exception as e:
            logger.error(f"Bulk inventory creation failed: {e}")
            raise

    def get_api_stats(self) -> Dict[str, Any]:
        """Get API usage statistics.

        Returns:
            Statistics dictionary
        """
        return self.request_tracker.get_stats()
