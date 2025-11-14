"""
Dashboard view displaying key metrics and recent activity.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGridLayout, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import requests
import logging

logger = logging.getLogger(__name__)


class StatCard(QFrame):
    """Card widget for displaying statistics."""

    def __init__(self, title: str, value: str, icon: str = ""):
        super().__init__()
        self.setObjectName("stat-card")
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            #stat-card {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(self)

        # Icon and title
        header_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_font = QFont()
            icon_font.setPointSize(24)
            icon_label.setFont(icon_font)
            header_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666; font-size: 12px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Value
        self.value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(28)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet("color: #2c3e50;")
        layout.addWidget(self.value_label)

    def update_value(self, value: str):
        """Update card value.

        Args:
            value: New value to display
        """
        self.value_label.setText(value)


class DashboardView(QWidget):
    """Dashboard view with key metrics and statistics."""

    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000/api"
        self.setup_ui()

        # Refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

        # Initial load
        self.refresh()

    def setup_ui(self):
        """Setup user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Header
        header = QLabel("Dashboard")
        header_font = QFont()
        header_font.setPointSize(28)
        header_font.setBold(True)
        header.setFont(header_font)
        main_layout.addWidget(header)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Stats cards
        stats_grid = QGridLayout()
        stats_grid.setSpacing(20)

        self.total_items_card = StatCard("Total Items", "0", "📦")
        self.draft_items_card = StatCard("Draft Items", "0", "📝")
        self.listed_items_card = StatCard("Listed Items", "0", "🛒")
        self.sold_items_card = StatCard("Sold Items", "0", "✅")

        stats_grid.addWidget(self.total_items_card, 0, 0)
        stats_grid.addWidget(self.draft_items_card, 0, 1)
        stats_grid.addWidget(self.listed_items_card, 0, 2)
        stats_grid.addWidget(self.sold_items_card, 0, 3)

        content_layout.addLayout(stats_grid)

        # Value cards
        value_grid = QGridLayout()
        value_grid.setSpacing(20)

        self.inventory_value_card = StatCard("Inventory Cost", "$0.00", "💵")
        self.potential_revenue_card = StatCard("Potential Revenue", "$0.00", "💰")
        self.potential_profit_card = StatCard("Potential Profit", "$0.00", "📈")

        value_grid.addWidget(self.inventory_value_card, 0, 0)
        value_grid.addWidget(self.potential_revenue_card, 0, 1)
        value_grid.addWidget(self.potential_profit_card, 0, 2)

        content_layout.addLayout(value_grid)

        # Status section
        status_label = QLabel("System Status")
        status_font = QFont()
        status_font.setPointSize(16)
        status_font.setBold(True)
        status_label.setFont(status_font)
        content_layout.addWidget(status_label)

        status_layout = QHBoxLayout()
        self.db_status = QLabel("Database: Checking...")
        self.ollama_status = QLabel("AI (Ollama): Checking...")
        self.ebay_status = QLabel("eBay: Checking...")

        status_layout.addWidget(self.db_status)
        status_layout.addWidget(self.ollama_status)
        status_layout.addWidget(self.ebay_status)
        status_layout.addStretch()

        content_layout.addLayout(status_layout)

        content_layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def refresh(self):
        """Refresh dashboard data."""
        try:
            self.load_statistics()
            self.check_system_status()
        except Exception as e:
            logger.error(f"Failed to refresh dashboard: {e}")

    def load_statistics(self):
        """Load inventory statistics."""
        try:
            response = requests.get(f"{self.api_url}/inventory/statistics", timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})

                # Update item counts
                total = data.get("total_items", 0)
                by_status = data.get("by_status", {})

                self.total_items_card.update_value(str(total))
                self.draft_items_card.update_value(str(by_status.get("Draft", 0)))
                self.listed_items_card.update_value(str(by_status.get("Listed", 0)))
                self.sold_items_card.update_value(str(by_status.get("Sold", 0)))

                # Update values
                inventory_value = data.get("inventory_value", {})
                self.inventory_value_card.update_value(
                    f"${inventory_value.get('total_cost', 0):.2f}"
                )
                self.potential_revenue_card.update_value(
                    f"${inventory_value.get('total_potential_revenue', 0):.2f}"
                )
                self.potential_profit_card.update_value(
                    f"${inventory_value.get('total_potential_profit', 0):.2f}"
                )
        except Exception as e:
            logger.error(f"Failed to load statistics: {e}")

    def check_system_status(self):
        """Check system component status."""
        # Database status
        try:
            response = requests.get(f"{self.api_url}/system/health", timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                db_status = data.get("database", "unknown")
                self.db_status.setText(f"Database: ✓ {db_status}")
                self.db_status.setStyleSheet("color: green;")
            else:
                self.db_status.setText("Database: ✗ Error")
                self.db_status.setStyleSheet("color: red;")
        except:
            self.db_status.setText("Database: ✗ Unreachable")
            self.db_status.setStyleSheet("color: red;")

        # Ollama status
        try:
            response = requests.get(f"{self.api_url}/assistant/ollama-status", timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                if data.get("available"):
                    self.ollama_status.setText("AI (Ollama): ✓ Online")
                    self.ollama_status.setStyleSheet("color: green;")
                else:
                    self.ollama_status.setText("AI (Ollama): ⚠ Offline (using fallback)")
                    self.ollama_status.setStyleSheet("color: orange;")
            else:
                self.ollama_status.setText("AI (Ollama): ⚠ Unknown")
                self.ollama_status.setStyleSheet("color: orange;")
        except:
            self.ollama_status.setText("AI (Ollama): ⚠ Offline")
            self.ollama_status.setStyleSheet("color: orange;")

        # eBay status
        try:
            response = requests.get(f"{self.api_url}/ebay/auth-status", timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                if data.get("authenticated"):
                    self.ebay_status.setText("eBay: ✓ Connected")
                    self.ebay_status.setStyleSheet("color: green;")
                else:
                    self.ebay_status.setText("eBay: ⚠ Not Connected")
                    self.ebay_status.setStyleSheet("color: orange;")
            else:
                self.ebay_status.setText("eBay: ✗ Error")
                self.ebay_status.setStyleSheet("color: red;")
        except:
            self.ebay_status.setText("eBay: ✗ Unreachable")
            self.ebay_status.setStyleSheet("color: red;")
