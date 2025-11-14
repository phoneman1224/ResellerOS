"""
eBay OAuth authentication handler.
"""
import webbrowser
import base64
import requests
from urllib.parse import urlencode, parse_qs
import http.server
import socketserver
import ssl
import tempfile
import os
from threading import Thread
from typing import Optional
from pathlib import Path
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

    def _generate_self_signed_cert(self):
        """Generate self-signed certificate for HTTPS OAuth callback.

        Returns:
            Tuple of (cert_file_path, key_file_path)
        """
        cert_dir = Path.home() / ".reselleros" / "certs"
        cert_dir.mkdir(parents=True, exist_ok=True)

        cert_file = cert_dir / "oauth_cert.pem"
        key_file = cert_dir / "oauth_key.pem"

        # Check if certificate already exists and is valid
        if cert_file.exists() and key_file.exists():
            return str(cert_file), str(key_file)

        # Generate new self-signed certificate using openssl command
        try:
            import subprocess
            subprocess.run([
                "openssl", "req", "-x509", "-newkey", "rsa:4096",
                "-keyout", str(key_file),
                "-out", str(cert_file),
                "-days", "365", "-nodes",
                "-subj", "/CN=localhost"
            ], check=True, capture_output=True)

            logger.info(f"Generated self-signed certificate at {cert_file}")
            return str(cert_file), str(key_file)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(f"Could not generate certificate with openssl: {e}")
            # Fall back to Python's certificate generation
            return self._generate_cert_python(cert_file, key_file)

    def _generate_cert_python(self, cert_file, key_file):
        """Generate certificate using pure Python (cryptography library)."""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            import datetime

            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )

            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
            ])

            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(u"localhost"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())

            # Write certificate
            with open(cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))

            # Write private key
            with open(key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            logger.info(f"Generated self-signed certificate using cryptography library")
            return str(cert_file), str(key_file)

        except ImportError:
            raise EbayAuthError(
                "Cannot generate HTTPS certificate. Please install openssl or ensure cryptography library is available."
            )

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
            # Determine if HTTPS is needed
            use_https = self.redirect_uri.startswith('https://')
            protocol = 'https' if use_https else 'http'

            # Extract port from redirect URI, or use defaults
            # For external URLs (like Cloudflare tunnels), use default HTTPS port 8443
            if ':' in self.redirect_uri.split('/')[-1]:
                # Port is explicitly specified in URL
                port = int(self.redirect_uri.split(':')[-1].rstrip('/'))
            else:
                # No explicit port - use 8443 for HTTPS, 8080 for HTTP
                port = 8443 if use_https else 8080

            logger.info(f"Callback server will listen on local port {port}")

            # Generate certificate if HTTPS is needed
            cert_file = None
            key_file = None
            if use_https:
                try:
                    cert_file, key_file = self._generate_self_signed_cert()
                    logger.info("Using HTTPS for OAuth callback server")
                except Exception as e:
                    logger.error(f"Failed to generate certificate: {e}")
                    raise EbayAuthError(
                        "Failed to set up HTTPS for OAuth callback. "
                        "Please ensure openssl is installed or the cryptography library is available."
                    )

            # Create server with address reuse
            httpd = None
            for attempt_port in [port, port + 1, port + 2]:  # Try original port, +1, +2
                try:
                    httpd = ReusableTCPServer(("", attempt_port), CallbackHandler)
                    actual_port = httpd.server_address[1]

                    # Wrap with SSL if HTTPS
                    if use_https and cert_file and key_file:
                        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                        context.load_cert_chain(cert_file, key_file)
                        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

                    logger.info(f"OAuth callback server started on {protocol}://localhost:{actual_port}")

                    # Only update redirect URI if using localhost (not external tunnel)
                    if 'localhost' in self.redirect_uri or '127.0.0.1' in self.redirect_uri:
                        if actual_port != port:
                            original_redirect = self.redirect_uri
                            self.redirect_uri = f"{protocol}://localhost:{actual_port}"
                            logger.warning(
                                f"Using port {actual_port} instead of {port}. "
                                f"Make sure your eBay app redirect URI is set to {self.redirect_uri}"
                            )
                    else:
                        logger.info(f"Using external tunnel URL: {self.redirect_uri}")
                        logger.info(f"Local server listening on port {actual_port}, accessible via tunnel")

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
