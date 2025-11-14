"""
UserSettings model for application preferences and configuration.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
import json
from typing import Any, Optional

from src.core.database import Base


class UserSettings(Base):
    """User settings and preferences model."""

    __tablename__ = "user_settings"

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Setting key (unique identifier)
    key = Column(String(100), unique=True, nullable=False, index=True)

    # Setting value (JSON encoded)
    value = Column(Text)

    # Setting type for validation
    type = Column(String(50))  # string, integer, float, boolean, json

    # Description
    description = Column(String(500))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def get_value(self) -> Any:
        """Get the setting value with type conversion.

        Returns:
            Value converted to appropriate type
        """
        if self.value is None:
            return None

        if self.type == "integer":
            return int(self.value)
        elif self.type == "float":
            return float(self.value)
        elif self.type == "boolean":
            return self.value.lower() in ("true", "1", "yes")
        elif self.type == "json":
            try:
                return json.loads(self.value)
            except json.JSONDecodeError:
                return None
        else:  # string
            return self.value

    def set_value(self, value: Any):
        """Set the setting value with type conversion.

        Args:
            value: Value to set
        """
        if value is None:
            self.value = None
        elif isinstance(value, (dict, list)):
            self.value = json.dumps(value)
            self.type = "json"
        elif isinstance(value, bool):
            self.value = str(value)
            self.type = "boolean"
        elif isinstance(value, int):
            self.value = str(value)
            self.type = "integer"
        elif isinstance(value, float):
            self.value = str(value)
            self.type = "float"
        else:
            self.value = str(value)
            self.type = "string"

    def to_dict(self) -> dict:
        """Convert setting to dictionary.

        Returns:
            Dictionary representation of setting
        """
        return {
            "id": self.id,
            "key": self.key,
            "value": self.get_value(),
            "type": self.type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<UserSettings(key='{self.key}', type='{self.type}')>"


# Default settings to initialize on first run
DEFAULT_SETTINGS = {
    "ebay_auto_sync": {
        "value": True,
        "type": "boolean",
        "description": "Automatically sync with eBay",
    },
    "ebay_sync_interval": {
        "value": 3600,  # 1 hour
        "type": "integer",
        "description": "eBay sync interval in seconds",
    },
    "auto_backup": {
        "value": True,
        "type": "boolean",
        "description": "Enable automatic backups",
    },
    "backup_interval": {
        "value": 86400,  # 24 hours
        "type": "integer",
        "description": "Backup interval in seconds",
    },
    "backup_retention": {
        "value": 30,
        "type": "integer",
        "description": "Number of days to retain backups",
    },
    "ollama_enabled": {
        "value": True,
        "type": "boolean",
        "description": "Enable Ollama AI features",
    },
    "default_profit_margin": {
        "value": 30.0,
        "type": "float",
        "description": "Target profit margin percentage",
    },
    "currency": {
        "value": "USD",
        "type": "string",
        "description": "Default currency",
    },
    "theme": {
        "value": "light",
        "type": "string",
        "description": "UI theme (light/dark)",
    },
    "default_condition": {
        "value": "Good",
        "type": "string",
        "description": "Default item condition",
    },
    "categories": {
        "value": [
            "Clothing",
            "Electronics",
            "Collectibles",
            "Books",
            "Toys",
            "Home & Garden",
            "Sports",
            "Vintage",
            "Other",
        ],
        "type": "json",
        "description": "Available item categories",
    },
    "expense_categories": {
        "value": [
            "Inventory",
            "Shipping",
            "Supplies",
            "Fees",
            "Marketing",
            "Other",
        ],
        "type": "json",
        "description": "Available expense categories",
    },
}
