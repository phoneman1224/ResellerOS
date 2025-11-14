"""
Settings view for application configuration.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QFormLayout, QLineEdit, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import requests
import logging

logger = logging.getLogger(__name__)


class SettingsView(QWidget):
    """Settings view for configuring the application."""

    def __init__(self):
        super().__init__()
        self.api_url = "http://localhost:8000/api"
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        title = QLabel("Settings")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # eBay settings
        ebay_group = QGroupBox("eBay Integration")
        ebay_layout = QFormLayout(ebay_group)

        self.ebay_status_label = QLabel("Not Connected")
        ebay_layout.addRow("Status:", self.ebay_status_label)

        ebay_btn_layout = QHBoxLayout()

        self.connect_ebay_btn = QPushButton("Connect eBay Account")
        self.connect_ebay_btn.clicked.connect(self.connect_ebay)
        ebay_btn_layout.addWidget(self.connect_ebay_btn)

        self.disconnect_ebay_btn = QPushButton("Disconnect")
        self.disconnect_ebay_btn.clicked.connect(self.disconnect_ebay)
        self.disconnect_ebay_btn.setEnabled(False)
        ebay_btn_layout.addWidget(self.disconnect_ebay_btn)

        ebay_layout.addRow(ebay_btn_layout)

        layout.addWidget(ebay_group)

        # AI settings
        ai_group = QGroupBox("AI Configuration")
        ai_layout = QFormLayout(ai_group)

        self.ollama_status_label = QLabel("Checking...")
        ai_layout.addRow("Ollama Status:", self.ollama_status_label)

        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setPlaceholderText("http://localhost:11434")
        self.ollama_url_input.setEnabled(False)
        ai_layout.addRow("Ollama URL:", self.ollama_url_input)

        layout.addWidget(ai_group)

        # System info
        info_group = QGroupBox("System Information")
        info_layout = QFormLayout(info_group)

        self.app_version_label = QLabel("1.0.0")
        info_layout.addRow("Version:", self.app_version_label)

        self.db_size_label = QLabel("Calculating...")
        info_layout.addRow("Database Size:", self.db_size_label)

        self.uploads_size_label = QLabel("Calculating...")
        info_layout.addRow("Uploads Size:", self.uploads_size_label)

        refresh_info_btn = QPushButton("Refresh Info")
        refresh_info_btn.clicked.connect(self.load_system_info)
        info_layout.addRow(refresh_info_btn)

        layout.addWidget(info_group)

        # Logs
        logs_group = QGroupBox("Application Logs")
        logs_layout = QVBoxLayout(logs_group)

        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        self.logs_display.setMaximumHeight(200)
        self.logs_display.setPlaceholderText("Logs will appear here...")
        logs_layout.addWidget(self.logs_display)

        logs_btn_layout = QHBoxLayout()
        view_logs_btn = QPushButton("View Recent Logs")
        view_logs_btn.clicked.connect(self.load_logs)
        logs_btn_layout.addWidget(view_logs_btn)
        logs_btn_layout.addStretch()
        logs_layout.addLayout(logs_btn_layout)

        layout.addWidget(logs_group)

        layout.addStretch()

    def load_settings(self):
        """Load current settings."""
        self.check_ebay_status()
        self.check_ollama_status()
        self.load_system_info()

    def check_ebay_status(self):
        """Check eBay connection status."""
        try:
            response = requests.get(f"{self.api_url}/ebay/auth-status", timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                if data.get("authenticated"):
                    self.ebay_status_label.setText("✓ Connected")
                    self.ebay_status_label.setStyleSheet("color: green; font-weight: bold;")
                    self.connect_ebay_btn.setEnabled(False)
                    self.disconnect_ebay_btn.setEnabled(True)
                else:
                    self.ebay_status_label.setText("✗ Not Connected")
                    self.ebay_status_label.setStyleSheet("color: red;")
                    self.connect_ebay_btn.setEnabled(True)
                    self.disconnect_ebay_btn.setEnabled(False)
            else:
                self.ebay_status_label.setText("Error checking status")
        except Exception as e:
            logger.error(f"Failed to check eBay status: {e}")
            self.ebay_status_label.setText("Error checking status")

    def connect_ebay(self):
        """Connect eBay account."""
        reply = QMessageBox.question(
            self,
            "Connect eBay",
            "This will open your browser to authenticate with eBay. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                response = requests.post(f"{self.api_url}/ebay/auth/login", timeout=120)
                if response.status_code == 200:
                    QMessageBox.information(
                        self, "Success",
                        "Successfully connected to eBay!"
                    )
                    self.check_ebay_status()
                else:
                    error = response.json().get("detail", "Unknown error")
                    QMessageBox.critical(self, "Error", f"Failed to connect: {error}")
            except Exception as e:
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
                response = requests.post(f"{self.api_url}/ebay/auth/logout", timeout=10)
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", "Disconnected from eBay")
                    self.check_ebay_status()
                else:
                    error = response.json().get("detail", "Unknown error")
                    QMessageBox.critical(self, "Error", f"Failed to disconnect: {error}")
            except Exception as e:
                logger.error(f"eBay disconnection failed: {e}")
                QMessageBox.critical(self, "Error", f"Failed to disconnect: {str(e)}")

    def check_ollama_status(self):
        """Check Ollama status."""
        try:
            response = requests.get(f"{self.api_url}/assistant/ollama-status", timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                if data.get("available"):
                    models = ", ".join(data.get("models", []))
                    self.ollama_status_label.setText(f"✓ Online ({models})")
                    self.ollama_status_label.setStyleSheet("color: green; font-weight: bold;")
                else:
                    self.ollama_status_label.setText("✗ Offline")
                    self.ollama_status_label.setStyleSheet("color: orange;")
            else:
                self.ollama_status_label.setText("Unknown")
        except Exception as e:
            logger.error(f"Failed to check Ollama status: {e}")
            self.ollama_status_label.setText("✗ Offline")
            self.ollama_status_label.setStyleSheet("color: orange;")

    def load_system_info(self):
        """Load system information."""
        try:
            response = requests.get(f"{self.api_url}/system/info", timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                self.db_size_label.setText(f"{data.get('database_size_mb', 0)} MB")
                self.uploads_size_label.setText(f"{data.get('uploads_size_mb', 0)} MB")
            else:
                self.db_size_label.setText("Error")
                self.uploads_size_label.setText("Error")
        except Exception as e:
            logger.error(f"Failed to load system info: {e}")
            self.db_size_label.setText("Error")
            self.uploads_size_label.setText("Error")

    def load_logs(self):
        """Load recent logs."""
        try:
            response = requests.get(f"{self.api_url}/system/logs?lines=50", timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                logs = data.get("logs", [])
                self.logs_display.setText("\n".join(logs[-30:]))  # Show last 30 lines
            else:
                self.logs_display.setText("Failed to load logs")
        except Exception as e:
            logger.error(f"Failed to load logs: {e}")
            self.logs_display.setText(f"Error loading logs: {str(e)}")

    def refresh(self):
        """Refresh view."""
        self.load_settings()
