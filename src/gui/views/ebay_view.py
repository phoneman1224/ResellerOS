"""
eBay integration view for managing listings and sync.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import requests
import logging

logger = logging.getLogger(__name__)


class StatusCard(QFrame):
    """Status card widget."""

    def __init__(self, title: str, status: str, icon: str = ""):
        super().__init__()
        self.setObjectName("status-card")
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            #status-card {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(self)

        # Icon and title
        header = QHBoxLayout()
        if icon:
            icon_label = QLabel(icon)
            icon_font = QFont()
            icon_font.setPointSize(24)
            icon_label.setFont(icon_font)
            header.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header.addWidget(title_label)
        header.addStretch()

        layout.addLayout(header)

        # Status
        self.status_label = QLabel(status)
        self.status_label.setStyleSheet("font-size: 16px; margin-top: 10px;")
        layout.addWidget(self.status_label)

    def update_status(self, status: str, style: str = ""):
        """Update status text and style."""
        self.status_label.setText(status)
        if style:
            self.status_label.setStyleSheet(f"font-size: 16px; margin-top: 10px; {style}")


class EbayView(QWidget):
    """eBay integration and management view."""

    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000/api/ebay"
        self.setup_ui()
        self.check_connection()

    def setup_ui(self):
        """Setup user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        main_layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("eBay Integration")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.check_connection)
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        # Connection status card
        self.connection_card = StatusCard("Connection Status", "Checking...", "🔗")
        layout.addWidget(self.connection_card)

        # Action buttons
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_group)

        # Connect button
        self.connect_btn = QPushButton("🔌 Connect eBay Account")
        self.connect_btn.clicked.connect(self.connect_ebay)
        actions_layout.addWidget(self.connect_btn)

        # Sync button
        self.sync_btn = QPushButton("🔄 Sync Inventory")
        self.sync_btn.clicked.connect(self.sync_inventory)
        self.sync_btn.setEnabled(False)
        actions_layout.addWidget(self.sync_btn)

        # Disconnect button
        self.disconnect_btn = QPushButton("❌ Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_ebay)
        self.disconnect_btn.setEnabled(False)
        actions_layout.addWidget(self.disconnect_btn)

        layout.addWidget(actions_group)

        # API Stats
        self.stats_group = QGroupBox("API Statistics")
        stats_layout = QVBoxLayout(self.stats_group)

        self.stats_label = QLabel("No data available")
        self.stats_label.setStyleSheet("padding: 15px; font-size: 13px;")
        stats_layout.addWidget(self.stats_label)

        layout.addWidget(self.stats_group)
        self.stats_group.hide()

        # eBay items table
        items_label = QLabel("Your eBay Listings")
        items_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(items_label)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels([
            "SKU", "Title", "Status", "Quantity"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.items_table.setAlternatingRowColors(True)
        layout.addWidget(self.items_table)
        self.items_table.hide()

        # Placeholder
        self.placeholder_label = QLabel(
            "Connect your eBay account to view and manage listings.\n\n"
            "You'll need eBay API credentials from developer.ebay.com"
        )
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #999; font-size: 14px; padding: 40px;")
        layout.addWidget(self.placeholder_label)

        # Progress bar for syncing
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        self.progress_bar.hide()

        layout.addStretch()

    def check_connection(self):
        """Check eBay connection status."""
        try:
            response = requests.get(f"{self.api_url}/auth-status", timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                if data.get("authenticated"):
                    self.connection_card.update_status(
                        "✓ Connected",
                        "color: green; font-weight: bold;"
                    )
                    self.connect_btn.setEnabled(False)
                    self.sync_btn.setEnabled(True)
                    self.disconnect_btn.setEnabled(True)
                    self.placeholder_label.hide()
                    self.load_api_stats()
                    self.load_ebay_items()
                else:
                    self.connection_card.update_status(
                        "✗ Not Connected",
                        "color: red;"
                    )
                    self.connect_btn.setEnabled(True)
                    self.sync_btn.setEnabled(False)
                    self.disconnect_btn.setEnabled(False)
                    self.items_table.hide()
                    self.placeholder_label.show()
            else:
                self.connection_card.update_status("Error checking status", "color: orange;")
        except Exception as e:
            logger.error(f"Failed to check eBay connection: {e}")
            self.connection_card.update_status("Error: Cannot reach API", "color: red;")

    def connect_ebay(self):
        """Connect eBay account."""
        reply = QMessageBox.question(
            self,
            "Connect eBay",
            "This will open your browser to authenticate with eBay.\n\n"
            "Make sure you have configured your eBay API credentials in Settings first.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Show progress
                self.progress_bar.show()
                self.progress_bar.setRange(0, 0)  # Indeterminate

                response = requests.post(f"{self.api_url}/auth/login", timeout=120)

                self.progress_bar.hide()

                if response.status_code == 200:
                    QMessageBox.information(
                        self, "Success",
                        "Successfully connected to eBay!"
                    )
                    self.check_connection()
                else:
                    error = response.json().get("detail", "Unknown error")
                    QMessageBox.critical(self, "Error", f"Failed to connect: {error}")
            except Exception as e:
                self.progress_bar.hide()
                logger.error(f"eBay connection failed: {e}")
                QMessageBox.critical(self, "Error", f"Failed to connect: {str(e)}")

    def disconnect_ebay(self):
        """Disconnect eBay account."""
        reply = QMessageBox.question(
            self,
            "Disconnect eBay",
            "Are you sure you want to disconnect from eBay?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                response = requests.post(f"{self.api_url}/auth/logout", timeout=10)
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", "Disconnected from eBay")
                    self.check_connection()
                else:
                    error = response.json().get("detail", "Unknown error")
                    QMessageBox.critical(self, "Error", f"Failed to disconnect: {error}")
            except Exception as e:
                logger.error(f"eBay disconnection failed: {e}")
                QMessageBox.critical(self, "Error", f"Failed to disconnect: {str(e)}")

    def sync_inventory(self):
        """Sync inventory with eBay."""
        QMessageBox.information(
            self,
            "Sync Inventory",
            "Inventory sync feature will be available soon.\n\n"
            "This will synchronize your local inventory with eBay listings."
        )

    def load_api_stats(self):
        """Load eBay API statistics."""
        try:
            response = requests.get(f"{self.api_url}/stats", timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})

                stats_text = f"""
Total Requests: {data.get('total_requests', 0)}
Success: {data.get('success_count', 0)}
Errors: {data.get('error_count', 0)}
Requests/min: {data.get('requests_per_minute', 0)}
                """.strip()

                self.stats_label.setText(stats_text)
                self.stats_group.show()
        except Exception as e:
            logger.error(f"Failed to load API stats: {e}")

    def load_ebay_items(self):
        """Load eBay items."""
        try:
            response = requests.get(f"{self.api_url}/inventory/items?limit=50", timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", {})
                items = data.get("inventoryItems", [])

                if items:
                    self.items_table.show()
                    self.items_table.setRowCount(len(items))

                    for row, item in enumerate(items):
                        self.items_table.setItem(row, 0, QTableWidgetItem(item.get("sku", "")))
                        self.items_table.setItem(row, 1, QTableWidgetItem(
                            item.get("product", {}).get("title", "")
                        ))
                        self.items_table.setItem(row, 2, QTableWidgetItem(
                            item.get("condition", "")
                        ))
                        self.items_table.setItem(row, 3, QTableWidgetItem(
                            str(item.get("availability", {}).get("shipToLocationAvailability", {}).get("quantity", 0))
                        ))
                else:
                    self.items_table.hide()
                    self.placeholder_label.setText("No eBay listings found.\n\nStart by creating items in Inventory.")
                    self.placeholder_label.show()
        except Exception as e:
            logger.error(f"Failed to load eBay items: {e}")

    def refresh(self):
        """Refresh view."""
        self.check_connection()
