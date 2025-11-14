"""
eBay OAuth authentication handler.
"""
import webbrowser
import base64
import requests
from urllib.parse import urlencode, parse_qs
import http.server
import socketserver
from threading import Thread
from typing import Optional
import logging

from src.config.settings import settings
from src.core.security import SecureStorage
from src.core.exceptions import EbayAuthError

logger = logging.getLogger(__name__)


class EbayAuth:
    """eBay OAuth 2.0 authentication handler."""

    def __init__(self):
        """Initialize eBay auth handler."""
        self.secure_storage = SecureStorage()
        self._reload_settings()

    def _reload_settings(self):
        """Reload settings from .env file to get latest credentials."""
        # Force reload settings from .env file
        from src.config.settings import Settings
        fresh_settings = Settings()

        self.client_id = fresh_settings.ebay_client_id
        self.client_secret = fresh_settings.ebay_client_secret
        self.redirect_uri = fresh_settings.ebay_redirect_uri
        self.auth_url = fresh_settings.ebay_auth_url
        self.token_url = fresh_settings.ebay_token_url

    def get_authorization_url(self) -> str:
        """Generate OAuth authorization URL.

        Returns:
            Authorization URL for user to visit
        """
        if not self.client_id:
            raise EbayAuthError(
                "eBay Client ID is not configured. Please configure it in Settings."
            )

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join([
                "https://api.ebay.com/oauth/api_scope/sell.inventory",
                "https://api.ebay.com/oauth/api_scope/sell.account",
                "https://api.ebay.com/oauth/api_scope/sell.fulfillment",
            ])
        }

        # Log the URL for debugging
        logger.info(f"eBay OAuth Configuration:")
        logger.info(f"  Auth URL: {self.auth_url}")
        logger.info(f"  Redirect URI: {self.redirect_uri}")
        logger.info(f"  Environment: {'Sandbox' if 'sandbox' in self.auth_url else 'Production'}")
        logger.info(f"")
        logger.info(f"IMPORTANT: Make sure your eBay app has this redirect URI configured:")
        logger.info(f"  {self.redirect_uri}")
        logger.info(f"")

        return f"{self.auth_url}?{urlencode(params)}"

    def start_oauth_flow(self) -> bool:
        """Start OAuth flow with local callback server.

        Returns:
            True if authentication successful, False otherwise

        Raises:
            EbayAuthError: If authentication fails
        """
        # Reload settings to get latest credentials from .env
        self._reload_settings()

        if not self.client_id or not self.client_secret:
            raise EbayAuthError(
                "eBay API credentials not configured. "
                "Please configure them in Settings and try again."
            )

        authorization_code = [None]
        error = [None]

        class CallbackHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                try:
                    if '?' in self.path:
                        query = parse_qs(self.path.split('?')[1])
                        authorization_code[0] = query.get('code', [None])[0]
                        error[0] = query.get('error', [None])[0]

                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    if authorization_code[0]:
                        html = """
                        <html>
                        <body style="font-family: Arial; text-align: center; padding: 50px;">
                            <h1 style="color: green;">✓ Authorization Successful!</h1>
                            <p>You can close this window and return to ResellerOS.</p>
                        </body>
                        </html>
                        """
                    else:
                        html = """
                        <html>
                        <body style="font-family: Arial; text-align: center; padding: 50px;">
                            <h1 style="color: red;">✗ Authorization Failed</h1>
                            <p>Please try again or check your eBay credentials.</p>
                        </body>
                        </html>
                        """

                    self.wfile.write(html.encode())
                except Exception as e:
                    logger.error(f"Callback handler error: {e}")

            def log_message(self, format, *args):
                pass  # Suppress default logging

        # Custom TCPServer that allows address reuse
        class ReusableTCPServer(socketserver.TCPServer):
            allow_reuse_address = True

        try:
            # Start local callback server with socket reuse enabled
            port = int(self.redirect_uri.split(':')[-1].rstrip('/'))

            # Create server with address reuse
            httpd = None
            for attempt_port in [port, port + 1, port + 2]:  # Try original port, +1, +2
                try:
                    httpd = ReusableTCPServer(("", attempt_port), CallbackHandler)
                    actual_port = httpd.server_address[1]
                    logger.info(f"OAuth callback server started on port {actual_port}")

                    # Update redirect URI if using different port
                    if actual_port != port:
                        original_redirect = self.redirect_uri
                        self.redirect_uri = f"http://localhost:{actual_port}"
                        logger.warning(
                            f"Using port {actual_port} instead of {port}. "
                            f"Make sure your eBay app redirect URI is set to {self.redirect_uri}"
                        )

                    break
                except OSError as e:
                    if attempt_port == port + 2:  # Last attempt
                        raise EbayAuthError(
                            f"Could not start OAuth callback server. Ports {port}, {port+1}, and {port+2} are in use. "
                            f"Please close other applications or change EBAY_REDIRECT_URI in Settings."
                        )
                    continue

            if httpd is None:
                raise EbayAuthError("Could not start OAuth callback server")

            with httpd:
                server_thread = Thread(target=httpd.handle_request, daemon=True)
                server_thread.start()

                # Open browser for authorization
                auth_url = self.get_authorization_url()
                logger.info(f"Opening browser for eBay authorization...")
                webbrowser.open(auth_url)

                # Wait for callback (timeout after 2 minutes)
                server_thread.join(timeout=120)

            if error[0]:
                raise EbayAuthError(f"eBay authorization error: {error[0]}")

            if authorization_code[0]:
                # Exchange code for token
                return self.exchange_code_for_token(authorization_code[0])
            else:
                raise EbayAuthError("No authorization code received. Authentication timeout.")

        except EbayAuthError:
            raise
        except Exception as e:
            logger.error(f"OAuth flow failed: {e}")
            raise EbayAuthError(f"OAuth flow failed: {str(e)}")

    def exchange_code_for_token(self, code: str) -> bool:
        """Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            True if successful

        Raises:
            EbayAuthError: If token exchange fails
        """
        try:
            # Prepare auth header
            auth_header = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {auth_header}"
            }

            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri
            }

            logger.info("Exchanging authorization code for access token...")
            response = requests.post(self.token_url, headers=headers, data=data, timeout=30)

            if response.status_code == 200:
                token_data = response.json()

                # Store tokens securely
                success = self.secure_storage.store_ebay_token(
                    access_token=token_data["access_token"],
                    refresh_token=token_data["refresh_token"],
                    expires_in=token_data["expires_in"]
                )

                if success:
                    logger.info("eBay authentication successful!")
                    return True
                else:
                    raise EbayAuthError("Failed to store eBay tokens securely")
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("error_description", response.text)
                raise EbayAuthError(f"Token exchange failed: {error_msg}")

        except requests.RequestException as e:
            logger.error(f"Token exchange request failed: {e}")
            raise EbayAuthError(f"Token exchange failed: {str(e)}")
        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            raise EbayAuthError(f"Token exchange failed: {str(e)}")

    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token.

        Returns:
            True if successful

        Raises:
            EbayAuthError: If refresh fails
        """
        try:
            # Get stored tokens
            token_data = self.secure_storage.get_ebay_token()
            if not token_data:
                raise EbayAuthError("No eBay tokens found. Please authenticate first.")

            refresh_token = token_data.get("refresh_token")
            if not refresh_token:
                raise EbayAuthError("No refresh token available. Please re-authenticate.")

            # Prepare auth header
            auth_header = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {auth_header}"
            }

            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }

            logger.info("Refreshing eBay access token...")
            response = requests.post(self.token_url, headers=headers, data=data, timeout=30)

            if response.status_code == 200:
                new_token_data = response.json()

                # Store new tokens
                success = self.secure_storage.store_ebay_token(
                    access_token=new_token_data["access_token"],
                    refresh_token=new_token_data.get("refresh_token", refresh_token),
                    expires_in=new_token_data["expires_in"]
                )

                if success:
                    logger.info("Access token refreshed successfully")
                    return True
                else:
                    raise EbayAuthError("Failed to store refreshed tokens")
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("error_description", response.text)
                raise EbayAuthError(f"Token refresh failed: {error_msg}")

        except EbayAuthError:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise EbayAuthError(f"Token refresh failed: {str(e)}")

    def get_access_token(self) -> Optional[str]:
        """Get valid access token, refreshing if necessary.

        Returns:
            Access token or None if not authenticated

        Raises:
            EbayAuthError: If unable to get valid token
        """
        token_data = self.secure_storage.get_ebay_token()

        if not token_data:
            return None

        # Token is valid if not expired (handled by secure storage)
        access_token = token_data.get("access_token")
        if access_token:
            return access_token

        # Try to refresh if expired
        try:
            if self.refresh_access_token():
                token_data = self.secure_storage.get_ebay_token()
                return token_data.get("access_token") if token_data else None
        except EbayAuthError:
            return None

        return None

    def is_authenticated(self) -> bool:
        """Check if user is authenticated with eBay.

        Returns:
            True if authenticated and token is valid
        """
        try:
            return self.get_access_token() is not None
        except Exception:
            return False

    def logout(self) -> bool:
        """Logout and delete stored tokens.

        Returns:
            True if successful
        """
        return self.secure_storage.delete_ebay_token()
