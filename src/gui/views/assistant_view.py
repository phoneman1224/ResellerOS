"""
AI Assistant view for pricing and SEO suggestions.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QTextEdit, QComboBox, QDoubleSpinBox,
    QGroupBox, QFormLayout, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import requests
import logging

logger = logging.getLogger(__name__)


class AssistantView(QWidget):
    """AI Assistant view for item optimization."""

    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000/api/assistant"
        self.setup_ui()
        self.check_ollama_status()

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        title = QLabel("AI Assistant")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Ollama status
        self.status_label = QLabel("Checking AI status...")
        layout.addWidget(self.status_label)

        # Pricing section
        pricing_group = QGroupBox("Pricing Suggestion")
        pricing_layout = QFormLayout(pricing_group)

        self.pricing_title = QLineEdit()
        self.pricing_title.setPlaceholderText("Item title...")
        pricing_layout.addRow("Title:", self.pricing_title)

        self.pricing_category = QComboBox()
        self.pricing_category.addItems([
            "Clothing", "Electronics", "Collectibles", "Books",
            "Toys", "Home & Garden", "Sports", "Vintage", "Other"
        ])
        pricing_layout.addRow("Category:", self.pricing_category)

        self.pricing_cost = QDoubleSpinBox()
        self.pricing_cost.setPrefix("$ ")
        self.pricing_cost.setMaximum(999999.99)
        pricing_layout.addRow("Cost:", self.pricing_cost)

        self.pricing_condition = QComboBox()
        self.pricing_condition.addItems(["New", "Like New", "Good", "Fair", "Poor"])
        self.pricing_condition.setCurrentText("Good")
        pricing_layout.addRow("Condition:", self.pricing_condition)

        get_price_btn = QPushButton("🤖 Get Pricing Suggestion")
        get_price_btn.clicked.connect(self.get_pricing_suggestion)
        pricing_layout.addRow(get_price_btn)

        self.pricing_result = QTextEdit()
        self.pricing_result.setReadOnly(True)
        self.pricing_result.setMaximumHeight(150)
        self.pricing_result.setPlaceholderText("Pricing suggestion will appear here...")
        pricing_layout.addRow("Result:", self.pricing_result)

        layout.addWidget(pricing_group)

        # Title optimization section
        title_group = QGroupBox("Title Optimization")
        title_layout = QFormLayout(title_group)

        self.seo_title = QLineEdit()
        self.seo_title.setPlaceholderText("Enter your item title...")
        title_layout.addRow("Current Title:", self.seo_title)

        self.seo_category = QComboBox()
        self.seo_category.addItems([
            "Clothing", "Electronics", "Collectibles", "Books",
            "Toys", "Home & Garden", "Sports", "Vintage", "Other"
        ])
        title_layout.addRow("Category:", self.seo_category)

        optimize_btn = QPushButton("🤖 Optimize Title")
        optimize_btn.clicked.connect(self.optimize_title)
        title_layout.addRow(optimize_btn)

        self.title_result = QTextEdit()
        self.title_result.setReadOnly(True)
        self.title_result.setMaximumHeight(150)
        self.title_result.setPlaceholderText("Optimized title will appear here...")
        title_layout.addRow("Optimized Title:", self.title_result)

        layout.addWidget(title_group)

        layout.addStretch()

    def check_ollama_status(self):
        """Check Ollama availability."""
        try:
            response = requests.get(f"{self.api_url}/ollama-status", timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                if data.get("available"):
                    models = ", ".join(data.get("models", []))
                    self.status_label.setText(f"✓ AI Online - Models: {models or 'Unknown'}")
                    self.status_label.setStyleSheet("color: green; font-weight: bold;")
                else:
                    self.status_label.setText("⚠ AI Offline - Using fallback logic")
                    self.status_label.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.status_label.setText("⚠ AI Status Unknown")
                self.status_label.setStyleSheet("color: orange;")
        except Exception as e:
            logger.error(f"Failed to check Ollama status: {e}")
            self.status_label.setText("⚠ AI Offline - Using fallback logic")
            self.status_label.setStyleSheet("color: orange;")

    def get_pricing_suggestion(self):
        """Get AI pricing suggestion."""
        title = self.pricing_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Error", "Please enter a title")
            return

        cost = self.pricing_cost.value()
        if cost <= 0:
            QMessageBox.warning(self, "Error", "Please enter a valid cost")
            return

        self.pricing_result.setText("Generating pricing suggestion...")

        try:
            data = {
                "title": title,
                "category": self.pricing_category.currentText(),
                "cost": cost,
                "condition": self.pricing_condition.currentText(),
            }

            response = requests.post(f"{self.api_url}/suggest-price", json=data, timeout=30)

            if response.status_code == 200:
                result = response.json().get("data", {})
                price = result.get("price", 0)
                reasoning = result.get("reasoning", "")
                confidence = result.get("confidence", "")

                output = f"""Suggested Price: ${price:.2f}
Confidence: {confidence.upper()}

Reasoning:
{reasoning}
"""
                self.pricing_result.setText(output)
            else:
                error = response.json().get("detail", "Unknown error")
                self.pricing_result.setText(f"Error: {error}")
                QMessageBox.critical(self, "Error", f"Failed to get pricing: {error}")

        except Exception as e:
            logger.error(f"Pricing suggestion failed: {e}")
            self.pricing_result.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to get pricing: {str(e)}")

    def optimize_title(self):
        """Optimize title with AI."""
        title = self.seo_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Error", "Please enter a title")
            return

        self.title_result.setText("Optimizing title...")

        try:
            data = {
                "title": title,
                "category": self.seo_category.currentText(),
            }

            response = requests.post(f"{self.api_url}/optimize-title", json=data, timeout=30)

            if response.status_code == 200:
                result = response.json().get("data", {})
                suggested = result.get("suggested_title", "")
                seo_score = result.get("seo_score", 0)
                improvements = result.get("improvements", [])

                output = f"""Optimized Title:
{suggested}

SEO Score: {seo_score}/100

Improvements:
"""
                for imp in improvements:
                    output += f"• {imp}\n"

                self.title_result.setText(output)
            else:
                error = response.json().get("detail", "Unknown error")
                self.title_result.setText(f"Error: {error}")
                QMessageBox.critical(self, "Error", f"Failed to optimize title: {error}")

        except Exception as e:
            logger.error(f"Title optimization failed: {e}")
            self.title_result.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to optimize title: {str(e)}")

    def refresh(self):
        """Refresh view."""
        self.check_ollama_status()
