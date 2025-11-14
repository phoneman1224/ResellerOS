"""
Inventory view for managing items.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QHeaderView, QMessageBox, QDialog, QFormLayout, QTextEdit,
    QDoubleSpinBox, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import requests
import logging

logger = logging.getLogger(__name__)


class AddItemDialog(QDialog):
    """Dialog for adding new items."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Item")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI."""
        layout = QFormLayout(self)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter item title...")
        layout.addRow("Title *:", self.title_input)

        self.category_input = QComboBox()
        self.category_input.addItems([
            "Clothing", "Electronics", "Collectibles", "Books",
            "Toys", "Home & Garden", "Sports", "Vintage", "Other"
        ])
        layout.addRow("Category:", self.category_input)

        self.cost_input = QDoubleSpinBox()
        self.cost_input.setPrefix("$ ")
        self.cost_input.setMaximum(999999.99)
        layout.addRow("Cost *:", self.cost_input)

        self.condition_input = QComboBox()
        self.condition_input.addItems(["New", "Like New", "Good", "Fair", "Poor"])
        self.condition_input.setCurrentText("Good")
        layout.addRow("Condition:", self.condition_input)

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setPlaceholderText("Internal notes...")
        layout.addRow("Notes:", self.notes_input)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Item")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)

    def get_data(self):
        """Get form data."""
        return {
            "title": self.title_input.text(),
            "category": self.category_input.currentText(),
            "cost": self.cost_input.value(),
            "condition": self.condition_input.currentText(),
            "notes": self.notes_input.toPlainText(),
            "status": "Draft",
        }


class InventoryView(QWidget):
    """Inventory management view."""

    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000/api/inventory"
        self.items = []
        self.setup_ui()
        self.load_items()

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header with add button
        header_layout = QHBoxLayout()

        title = QLabel("Inventory Management")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        add_btn = QPushButton("➕ Add Item")
        add_btn.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(add_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_items)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Search and filters
        filter_layout = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search items...")
        self.search_box.setMinimumWidth(300)
        self.search_box.textChanged.connect(self.on_search_changed)
        filter_layout.addWidget(self.search_box)

        status_label = QLabel("Status:")
        filter_layout.addWidget(status_label)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Draft", "Ready", "Listed", "Sold", "Archived"])
        self.status_filter.currentTextChanged.connect(self.load_items)
        filter_layout.addWidget(self.status_filter)

        category_label = QLabel("Category:")
        filter_layout.addWidget(category_label)

        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "All", "Clothing", "Electronics", "Collectibles", "Books",
            "Toys", "Home & Garden", "Sports", "Vintage", "Other"
        ])
        self.category_filter.currentTextChanged.connect(self.load_items)
        filter_layout.addWidget(self.category_filter)

        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # Items table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Title", "Category", "Cost", "Price", "Status", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Search timer (debounce)
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.load_items)

    def on_search_changed(self):
        """Handle search text change."""
        self.search_timer.stop()
        self.search_timer.start(500)  # Wait 500ms before searching

    def show_add_dialog(self):
        """Show add item dialog."""
        dialog = AddItemDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["title"]:
                QMessageBox.warning(self, "Error", "Title is required")
                return

            self.create_item(data)

    def create_item(self, data):
        """Create a new item.

        Args:
            data: Item data dictionary
        """
        try:
            response = requests.post(self.api_url + "/items", json=data, timeout=10)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Item created successfully!")
                self.load_items()
            else:
                error = response.json().get("detail", "Unknown error")
                QMessageBox.critical(self, "Error", f"Failed to create item: {error}")
        except Exception as e:
            logger.error(f"Failed to create item: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create item: {str(e)}")

    def load_items(self):
        """Load items from API."""
        try:
            # Build query parameters
            params = {}
            status = self.status_filter.currentText()
            if status != "All":
                params["status"] = status

            category = self.category_filter.currentText()
            if category != "All":
                params["category"] = category

            search = self.search_box.text().strip()
            if search:
                params["search"] = search

            params["limit"] = 1000  # Get all items

            response = requests.get(self.api_url + "/items", params=params, timeout=10)
            if response.status_code == 200:
                self.items = response.json()
                self.display_items()
            else:
                logger.error(f"Failed to load items: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to load items: {e}")

    def display_items(self):
        """Display items in table."""
        self.table.setRowCount(len(self.items))

        for row, item in enumerate(self.items):
            self.table.setItem(row, 0, QTableWidgetItem(str(item.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(item.get("title", "")))
            self.table.setItem(row, 2, QTableWidgetItem(item.get("category", "")))
            self.table.setItem(row, 3, QTableWidgetItem(f"${item.get('cost', 0):.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(f"${item.get('price', 0):.2f}"))

            # Status with color
            status_item = QTableWidgetItem(item.get("status", ""))
            status = item.get("status", "")
            if status == "Sold":
                status_item.setBackground(Qt.GlobalColor.green)
            elif status == "Listed":
                status_item.setBackground(Qt.GlobalColor.cyan)
            elif status == "Draft":
                status_item.setBackground(Qt.GlobalColor.yellow)
            self.table.setItem(row, 5, status_item)

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 4, 4, 4)

            delete_btn = QPushButton("Delete")
            delete_btn.setMaximumWidth(80)
            delete_btn.clicked.connect(lambda checked, item_id=item["id"]: self.delete_item(item_id))
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 6, action_widget)

    def delete_item(self, item_id):
        """Delete an item.

        Args:
            item_id: Item ID to delete
        """
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this item?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                response = requests.delete(f"{self.api_url}/items/{item_id}", timeout=10)
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", "Item deleted successfully!")
                    self.load_items()
                else:
                    error = response.json().get("detail", "Unknown error")
                    QMessageBox.critical(self, "Error", f"Failed to delete item: {error}")
            except Exception as e:
                logger.error(f"Failed to delete item: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete item: {str(e)}")

    def refresh(self):
        """Refresh view."""
        self.load_items()
