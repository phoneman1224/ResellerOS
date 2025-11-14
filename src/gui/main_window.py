"""
Main window for ResellerOS application.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
import logging

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ResellerOS - eBay Reseller Management")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 700)

        self.setup_ui()
        self.apply_styles()

        logger.info("Main window initialized")

    def setup_ui(self):
        """Setup user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # Content area
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)

        # Create and add views
        self.views = {}
        self.create_views()

        # Show dashboard by default
        self.switch_view("dashboard")

    def create_sidebar(self) -> QWidget:
        """Create navigation sidebar.

        Returns:
            Sidebar widget
        """
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setObjectName("sidebar")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # App title/logo
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(20, 30, 20, 30)

        title = QLabel("📦 ResellerOS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title_layout.addWidget(title)

        subtitle = QLabel("eBay Reseller Management")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(9)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #888;")
        title_layout.addWidget(subtitle)

        layout.addWidget(title_container)

        # Navigation buttons
        nav_items = [
            ("Dashboard", "dashboard", "📊"),
            ("Inventory", "inventory", "📦"),
            ("Expenses", "expenses", "💰"),
            ("Analytics", "analytics", "📈"),
            ("AI Assistant", "assistant", "🤖"),
            ("eBay", "ebay", "🛒"),
            ("Settings", "settings", "⚙️"),
        ]

        for label, view_name, icon in nav_items:
            btn = QPushButton(f"{icon}  {label}")
            btn.setObjectName("nav-button")
            btn.setMinimumHeight(50)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, v=view_name: self.switch_view(v))
            layout.addWidget(btn)

        layout.addStretch()

        # Version info
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #666; padding: 20px;")
        layout.addWidget(version_label)

        return sidebar

    def create_views(self):
        """Create and add all application views."""
        from src.gui.views.dashboard_view import DashboardView
        from src.gui.views.inventory_view import InventoryView
        from src.gui.views.expenses_view import ExpensesView
        from src.gui.views.analytics_view import AnalyticsView
        from src.gui.views.assistant_view import AssistantView
        from src.gui.views.ebay_view import EbayView
        from src.gui.views.settings_view import SettingsView

        # Create all views
        views_to_create = {
            "dashboard": DashboardView,
            "inventory": InventoryView,
            "expenses": ExpensesView,
            "analytics": AnalyticsView,
            "assistant": AssistantView,
            "ebay": EbayView,
            "settings": SettingsView,
        }

        for name, ViewClass in views_to_create.items():
            try:
                view = ViewClass()
                self.views[name] = view
                self.content_stack.addWidget(view)
                logger.debug(f"Created view: {name}")
            except Exception as e:
                logger.error(f"Failed to create view {name}: {e}")
                # Create placeholder
                placeholder = QWidget()
                placeholder_layout = QVBoxLayout(placeholder)
                label = QLabel(f"View '{name}' not available\n\nError: {str(e)}")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                placeholder_layout.addWidget(label)
                self.views[name] = placeholder
                self.content_stack.addWidget(placeholder)

    def create_placeholder_view(self, title: str) -> QWidget:
        """Create a placeholder view.

        Args:
            title: View title

        Returns:
            Placeholder widget
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(f"{title} View\n\nComing Soon")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_font = QFont()
        label_font.setPointSize(24)
        label.setFont(label_font)
        label.setStyleSheet("color: #999;")

        layout.addWidget(label)

        return widget

    def switch_view(self, view_name: str):
        """Switch to a different view.

        Args:
            view_name: Name of view to switch to
        """
        if view_name in self.views:
            self.content_stack.setCurrentWidget(self.views[view_name])
            logger.debug(f"Switched to view: {view_name}")

            # Refresh view if it has a refresh method
            view = self.views[view_name]
            if hasattr(view, 'refresh'):
                try:
                    view.refresh()
                except Exception as e:
                    logger.error(f"Failed to refresh view {view_name}: {e}")
        else:
            logger.warning(f"Unknown view: {view_name}")

    def apply_styles(self):
        """Apply application styles."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }

            #sidebar {
                background-color: #2c3e50;
            }

            #nav-button {
                background-color: transparent;
                color: #ecf0f1;
                border: none;
                padding: 15px 20px;
                text-align: left;
                font-size: 14px;
                border-left: 3px solid transparent;
            }

            #nav-button:hover {
                background-color: #34495e;
                border-left: 3px solid #3498db;
            }

            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #2980b9;
            }

            QPushButton:pressed {
                background-color: #21618c;
            }

            QPushButton:disabled {
                background-color: #95a5a6;
            }

            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }

            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #3498db;
            }

            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                gridline-color: #f0f0f0;
            }

            QTableWidget::item {
                padding: 8px;
            }

            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }

            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #bdc3c7;
                font-weight: bold;
            }

            QLabel {
                color: #2c3e50;
            }
        """)

    def closeEvent(self, event):
        """Handle window close event.

        Args:
            event: Close event
        """
        reply = QMessageBox.question(
            self,
            'Confirm Exit',
            'Are you sure you want to exit ResellerOS?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Application closing")
            event.accept()
        else:
            event.ignore()
