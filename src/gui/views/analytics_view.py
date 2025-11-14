"""
Analytics view for business metrics and reporting.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QScrollArea, QGroupBox, QComboBox, QPushButton
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import requests
import logging

logger = logging.getLogger(__name__)


class MetricCard(QFrame):
    """Card widget for displaying a single metric."""

    def __init__(self, title: str, value: str, subtitle: str = "", icon: str = ""):
        super().__init__()
        self.setObjectName("metric-card")
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            #metric-card {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                min-height: 120px;
            }
        """)

        layout = QVBoxLayout(self)

        # Icon and title
        if icon:
            icon_label = QLabel(icon)
            icon_font = QFont()
            icon_font.setPointSize(32)
            icon_label.setFont(icon_font)
            layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666; font-size: 13px; font-weight: normal;")
        layout.addWidget(title_label)

        # Value
        self.value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(32)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet("color: #2c3e50; margin: 5px 0;")
        layout.addWidget(self.value_label)

        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #999; font-size: 12px;")
            layout.addWidget(subtitle_label)

        layout.addStretch()

    def update_value(self, value: str, subtitle: str = None):
        """Update card value."""
        self.value_label.setText(value)


class AnalyticsView(QWidget):
    """Analytics and reporting view."""

    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000/api"
        self.setup_ui()

        # Refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

        # Initial load
        self.refresh_data()

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

        title = QLabel("Analytics & Reporting")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Time period selector
        period_label = QLabel("Period:")
        header_layout.addWidget(period_label)

        self.period_combo = QComboBox()
        self.period_combo.addItems(["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])
        self.period_combo.currentTextChanged.connect(self.refresh_data)
        header_layout.addWidget(self.period_combo)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Key metrics grid
        metrics_label = QLabel("Key Metrics")
        metrics_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(metrics_label)

        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(20)

        self.total_items_card = MetricCard("Total Items", "0", "", "📦")
        self.listed_items_card = MetricCard("Listed Items", "0", "", "🛒")
        self.sold_items_card = MetricCard("Sold Items", "0", "", "✅")
        self.revenue_card = MetricCard("Total Revenue", "$0.00", "", "💰")

        metrics_grid.addWidget(self.total_items_card, 0, 0)
        metrics_grid.addWidget(self.listed_items_card, 0, 1)
        metrics_grid.addWidget(self.sold_items_card, 0, 2)
        metrics_grid.addWidget(self.revenue_card, 0, 3)

        layout.addLayout(metrics_grid)

        # Financial metrics
        financial_label = QLabel("Financial Metrics")
        financial_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(financial_label)

        financial_grid = QGridLayout()
        financial_grid.setSpacing(20)

        self.inventory_value_card = MetricCard("Inventory Value", "$0.00", "Total cost", "💵")
        self.potential_revenue_card = MetricCard("Potential Revenue", "$0.00", "If all items sell", "📈")
        self.profit_card = MetricCard("Potential Profit", "$0.00", "Before fees", "💎")
        self.avg_margin_card = MetricCard("Avg. Margin", "0%", "Profit margin", "📊")

        financial_grid.addWidget(self.inventory_value_card, 0, 0)
        financial_grid.addWidget(self.potential_revenue_card, 0, 1)
        financial_grid.addWidget(self.profit_card, 0, 2)
        financial_grid.addWidget(self.avg_margin_card, 0, 3)

        layout.addLayout(financial_grid)

        # Category breakdown
        category_label = QLabel("Inventory by Category")
        category_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(category_label)

        self.category_group = QGroupBox()
        category_layout = QVBoxLayout(self.category_group)
        self.category_text = QLabel("Loading category data...")
        self.category_text.setStyleSheet("padding: 20px; font-size: 14px;")
        category_layout.addWidget(self.category_text)

        layout.addWidget(self.category_group)

        # Status breakdown
        status_label = QLabel("Inventory by Status")
        status_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(status_label)

        self.status_group = QGroupBox()
        status_layout = QVBoxLayout(self.status_group)
        self.status_text = QLabel("Loading status data...")
        self.status_text.setStyleSheet("padding: 20px; font-size: 14px;")
        status_layout.addWidget(self.status_text)

        layout.addWidget(self.status_group)

        layout.addStretch()

    def refresh_data(self):
        """Refresh analytics data."""
        try:
            self.load_inventory_stats()
        except Exception as e:
            logger.error(f"Failed to refresh analytics: {e}")

    def load_inventory_stats(self):
        """Load inventory statistics."""
        try:
            response = requests.get(f"{self.api_url}/inventory/statistics", timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})

                # Update key metrics
                total = data.get("total_items", 0)
                by_status = data.get("by_status", {})
                by_category = data.get("by_category", {})
                inventory_value = data.get("inventory_value", {})

                self.total_items_card.update_value(str(total))
                self.listed_items_card.update_value(str(by_status.get("Listed", 0)))
                self.sold_items_card.update_value(str(by_status.get("Sold", 0)))
                self.revenue_card.update_value("$0.00")  # Will be calculated from sales

                # Update financial metrics
                cost = inventory_value.get("total_cost", 0)
                potential_rev = inventory_value.get("total_potential_revenue", 0)
                potential_profit = inventory_value.get("total_potential_profit", 0)

                self.inventory_value_card.update_value(f"${cost:.2f}")
                self.potential_revenue_card.update_value(f"${potential_rev:.2f}")
                self.profit_card.update_value(f"${potential_profit:.2f}")

                # Calculate average margin
                if potential_rev > 0:
                    avg_margin = (potential_profit / potential_rev) * 100
                    self.avg_margin_card.update_value(f"{avg_margin:.1f}%")
                else:
                    self.avg_margin_card.update_value("0%")

                # Update category breakdown
                if by_category:
                    category_text = ""
                    for category, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
                        percentage = (count / total * 100) if total > 0 else 0
                        category_text += f"• {category}: {count} items ({percentage:.1f}%)\n"
                    self.category_text.setText(category_text.strip())
                else:
                    self.category_text.setText("No items categorized yet")

                # Update status breakdown
                if by_status:
                    status_text = ""
                    for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
                        percentage = (count / total * 100) if total > 0 else 0
                        status_text += f"• {status}: {count} items ({percentage:.1f}%)\n"
                    self.status_text.setText(status_text.strip())
                else:
                    self.status_text.setText("No items yet")

        except Exception as e:
            logger.error(f"Failed to load inventory statistics: {e}")

    def refresh(self):
        """Refresh view."""
        self.refresh_data()
