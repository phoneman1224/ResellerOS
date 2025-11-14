"""
Security utilities for encryption and secure credential storage.
"""
import os
import json
import base64
from datetime import datetime, timedelta
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

from src.core.exceptions import AuthenticationError

logger = logging.getLogger(__name__)


class SecureStorage:
    """Secure storage for sensitive data like API tokens."""

    def __init__(self, key: Optional[str] = None):
        """Initialize secure storage with encryption key.

        Args:
            key: Optional encryption key. If not provided, generates one.
        """
        if key:
            self.key = key.encode() if isinstance(key, str) else key
        else:
            # Generate key from environment or create new one
            self.key = self._get_or_create_key()

        self.fernet = Fernet(self.key)
        self.storage_file = ".secure_storage.enc"

    def _get_or_create_key(self) -> bytes:
        """Get existing encryption key or create a new one."""
        key_file = ".encryption_key"

        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            # Store it securely
            with open(key_file, "wb") as f:
                f.write(key)
            # Make it read-only
            os.chmod(key_file, 0o600)
            logger.info("Generated new encryption key")
            return key

    def _load_storage(self) -> dict:
        """Load encrypted storage file."""
        if not os.path.exists(self.storage_file):
            return {}

        try:
            with open(self.storage_file, "rb") as f:
                encrypted_data = f.read()

            if not encrypted_data:
                return {}

            decrypted_data = self.fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Failed to load secure storage: {e}")
            return {}

    def _save_storage(self, data: dict):
        """Save data to encrypted storage file."""
        try:
            json_data = json.dumps(data).encode()
            encrypted_data = self.fernet.encrypt(json_data)

            with open(self.storage_file, "wb") as f:
                f.write(encrypted_data)

            # Make it read-only
            os.chmod(self.storage_file, 0o600)
        except Exception as e:
            logger.error(f"Failed to save secure storage: {e}")
            raise

    def store_ebay_token(
        self, access_token: str, refresh_token: str, expires_in: int
    ) -> bool:
        """Store eBay OAuth tokens securely.

        Args:
            access_token: eBay access token
            refresh_token: eBay refresh token
            expires_in: Token expiration time in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            storage = self._load_storage()

            storage["ebay"] = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            self._save_storage(storage)
            logger.info("eBay tokens stored securely")
            return True
        except Exception as e:
            logger.error(f"Failed to store eBay tokens: {e}")
            return False

    def get_ebay_token(self) -> Optional[dict]:
        """Retrieve eBay OAuth tokens.

        Returns:
            Dictionary with access_token, refresh_token, and expires_at,
            or None if not found or expired
        """
        try:
            storage = self._load_storage()
            ebay_data = storage.get("ebay")

            if not ebay_data:
                return None

            # Check if token is expired
            expires_at = datetime.fromisoformat(ebay_data["expires_at"])
            if datetime.utcnow() >= expires_at:
                logger.warning("eBay token has expired")
                return None

            return ebay_data
        except Exception as e:
            logger.error(f"Failed to retrieve eBay tokens: {e}")
            return None

    def delete_ebay_token(self) -> bool:
        """Delete stored eBay tokens.

        Returns:
            True if successful, False otherwise
        """
        try:
            storage = self._load_storage()
            if "ebay" in storage:
                del storage["ebay"]
                self._save_storage(storage)
                logger.info("eBay tokens deleted")
            return True
        except Exception as e:
            logger.error(f"Failed to delete eBay tokens: {e}")
            return False

    def store_value(self, key: str, value: str) -> bool:
        """Store an arbitrary encrypted value.

        Args:
            key: Storage key
            value: Value to store

        Returns:
            True if successful, False otherwise
        """
        try:
            storage = self._load_storage()
            storage[key] = {
                "value": value,
                "updated_at": datetime.utcnow().isoformat(),
            }
            self._save_storage(storage)
            logger.info(f"Stored value for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to store value for key {key}: {e}")
            return False

    def get_value(self, key: str) -> Optional[str]:
        """Retrieve an encrypted value.

        Args:
            key: Storage key

        Returns:
            Stored value or None if not found
        """
        try:
            storage = self._load_storage()
            data = storage.get(key)
            if data:
                return data.get("value")
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve value for key {key}: {e}")
            return None

    def delete_value(self, key: str) -> bool:
        """Delete a stored value.

        Args:
            key: Storage key

        Returns:
            True if successful, False otherwise
        """
        try:
            storage = self._load_storage()
            if key in storage:
                del storage[key]
                self._save_storage(storage)
                logger.info(f"Deleted value for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete value for key {key}: {e}")
            return False


def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
    """Hash a password using PBKDF2.

    Args:
        password: Plain text password
        salt: Optional salt bytes. If not provided, generates random salt.

    Returns:
        Tuple of (hashed_password, salt) as base64 encoded strings
    """
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )

    key = kdf.derive(password.encode())

    hashed = base64.b64encode(key).decode()
    salt_b64 = base64.b64encode(salt).decode()

    return hashed, salt_b64


def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify a password against its hash.

    Args:
        password: Plain text password to verify
        hashed: Base64 encoded hashed password
        salt: Base64 encoded salt

    Returns:
        True if password matches, False otherwise
    """
    try:
        salt_bytes = base64.b64decode(salt.encode())
        new_hash, _ = hash_password(password, salt_bytes)
        return new_hash == hashed
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False
