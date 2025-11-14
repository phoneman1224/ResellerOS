"""
Expenses view for tracking business expenses.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QHeaderView, QMessageBox, QDialog, QFormLayout, QTextEdit,
    QDoubleSpinBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AddExpenseDialog(QDialog):
    """Dialog for adding new expenses."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Expense")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI."""
        layout = QFormLayout(self)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., Shipping supplies")
        layout.addRow("Title *:", self.title_input)

        self.category_input = QComboBox()
        self.category_input.addItems([
            "Inventory", "Shipping", "Supplies", "Fees", "Marketing", "Other"
        ])
        layout.addRow("Category *:", self.category_input)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setPrefix("$ ")
        self.amount_input.setMaximum(999999.99)
        self.amount_input.setDecimals(2)
        layout.addRow("Amount *:", self.amount_input)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        layout.addRow("Date:", self.date_input)

        self.vendor_input = QLineEdit()
        self.vendor_input.setPlaceholderText("Vendor name...")
        layout.addRow("Vendor:", self.vendor_input)

        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        self.description_input.setPlaceholderText("Expense description...")
        layout.addRow("Description:", self.description_input)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Expense")
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
            "amount": self.amount_input.value(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "vendor": self.vendor_input.text(),
            "description": self.description_input.toPlainText(),
            "is_deductible": True,
        }


class ExpensesView(QWidget):
    """Expenses tracking view."""

    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000/api/expenses"
        self.expenses = []
        self.setup_ui()
        # We'll load expenses when the backend endpoint is ready

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header with add button
        header_layout = QHBoxLayout()

        title = QLabel("Expense Tracking")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        add_btn = QPushButton("➕ Add Expense")
        add_btn.clicked.connect(self.show_add_dialog)
        header_layout.addWidget(add_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_expenses)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Summary cards
        summary_layout = QHBoxLayout()

        self.total_label = QLabel("Total Expenses: $0.00")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #e8f4f8; border-radius: 5px;")
        summary_layout.addWidget(self.total_label)

        self.month_label = QLabel("This Month: $0.00")
        self.month_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #fff4e6; border-radius: 5px;")
        summary_layout.addWidget(self.month_label)

        layout.addLayout(summary_layout)

        # Filters
        filter_layout = QHBoxLayout()

        category_label = QLabel("Category:")
        filter_layout.addWidget(category_label)

        self.category_filter = QComboBox()
        self.category_filter.addItems([
            "All", "Inventory", "Shipping", "Supplies", "Fees", "Marketing", "Other"
        ])
        self.category_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.category_filter)

        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # Expenses table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Date", "Title", "Category", "Amount", "Vendor", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        # Placeholder message
        self.placeholder_label = QLabel("No expenses recorded yet.\nClick 'Add Expense' to get started!")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #999; font-size: 14px; padding: 40px;")
        layout.addWidget(self.placeholder_label)
        self.table.hide()

    def show_add_dialog(self):
        """Show add expense dialog."""
        dialog = AddExpenseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if not data["title"]:
                QMessageBox.warning(self, "Error", "Title is required")
                return

            # For now, add to local list (backend endpoint will be implemented)
            self.add_expense_local(data)

    def add_expense_local(self, data):
        """Add expense locally (temporary until backend ready)."""
        expense = {
            "id": len(self.expenses) + 1,
            "title": data["title"],
            "category": data["category"],
            "amount": data["amount"],
            "date": data["date"],
            "vendor": data.get("vendor", ""),
            "description": data.get("description", ""),
        }
        self.expenses.append(expense)
        self.display_expenses()
        QMessageBox.information(self, "Success", "Expense added successfully!")

    def load_expenses(self):
        """Load expenses from API (will be implemented when backend ready)."""
        # For now, just display what we have locally
        self.display_expenses()

    def display_expenses(self):
        """Display expenses in table."""
        if not self.expenses:
            self.placeholder_label.show()
            self.table.hide()
            return

        self.placeholder_label.hide()
        self.table.show()

        # Apply filters
        filtered = self.expenses
        category = self.category_filter.currentText()
        if category != "All":
            filtered = [e for e in self.expenses if e["category"] == category]

        self.table.setRowCount(len(filtered))

        total = sum(e["amount"] for e in self.expenses)
        self.total_label.setText(f"Total Expenses: ${total:.2f}")

        # Calculate this month
        current_month = datetime.now().strftime("%Y-%m")
        month_total = sum(e["amount"] for e in self.expenses if e["date"].startswith(current_month))
        self.month_label.setText(f"This Month: ${month_total:.2f}")

        for row, expense in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(expense["date"]))
            self.table.setItem(row, 1, QTableWidgetItem(expense["title"]))
            self.table.setItem(row, 2, QTableWidgetItem(expense["category"]))
            self.table.setItem(row, 3, QTableWidgetItem(f"${expense['amount']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(expense.get("vendor", "")))

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 4, 4, 4)

            delete_btn = QPushButton("Delete")
            delete_btn.setMaximumWidth(80)
            delete_btn.clicked.connect(lambda checked, exp_id=expense["id"]: self.delete_expense(exp_id))
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 5, action_widget)

    def delete_expense(self, expense_id):
        """Delete an expense."""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this expense?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.expenses = [e for e in self.expenses if e["id"] != expense_id]
            self.display_expenses()

    def apply_filters(self):
        """Apply filters to expense list."""
        self.display_expenses()

    def refresh(self):
        """Refresh view."""
        self.load_expenses()
