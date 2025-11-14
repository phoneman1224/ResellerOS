"""
Settings view for application configuration.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QFormLayout, QLineEdit, QMessageBox, QTextEdit, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import requests
import logging
import os

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

        # eBay credentials input
        self.ebay_client_id_input = QLineEdit()
        self.ebay_client_id_input.setPlaceholderText("Enter your eBay Client ID...")
        ebay_layout.addRow("Client ID:", self.ebay_client_id_input)

        self.ebay_client_secret_input = QLineEdit()
        self.ebay_client_secret_input.setPlaceholderText("Enter your eBay Client Secret...")
        self.ebay_client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        ebay_layout.addRow("Client Secret:", self.ebay_client_secret_input)

        self.ebay_environment_combo = QComboBox()
        self.ebay_environment_combo.addItems(["sandbox", "production"])
        ebay_layout.addRow("Environment:", self.ebay_environment_combo)

        # Save credentials button
        save_creds_btn = QPushButton("💾 Save Credentials")
        save_creds_btn.clicked.connect(self.save_ebay_credentials)
        ebay_layout.addRow(save_creds_btn)

        # Get credentials link
        get_creds_label = QLabel('<a href="https://developer.ebay.com/">Get eBay API Credentials</a>')
        get_creds_label.setOpenExternalLinks(True)
        ebay_layout.addRow("Need credentials?", get_creds_label)

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
        ai_layout.addRow("Ollama URL:", self.ollama_url_input)

        self.ollama_model_input = QLineEdit()
        self.ollama_model_input.setPlaceholderText("phi3")
        ai_layout.addRow("Model Name:", self.ollama_model_input)

        save_ollama_btn = QPushButton("💾 Save AI Settings")
        save_ollama_btn.clicked.connect(self.save_ollama_settings)
        ai_layout.addRow(save_ollama_btn)

        # Ollama installation link
        ollama_link = QLabel('<a href="https://ollama.ai/">Install Ollama</a>')
        ollama_link.setOpenExternalLinks(True)
        ai_layout.addRow("Need Ollama?", ollama_link)

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
        self.load_ebay_credentials()
        self.check_ebay_status()
        self.check_ollama_status()
        self.load_system_info()

    def load_ebay_credentials(self):
        """Load eBay credentials from .env file."""
        try:
            env_path = ".env"
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    content = f.read()

                # Parse .env file
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        if key == 'EBAY_CLIENT_ID':
                            self.ebay_client_id_input.setText(value)
                        elif key == 'EBAY_CLIENT_SECRET':
                            self.ebay_client_secret_input.setText(value)
                        elif key == 'EBAY_ENVIRONMENT':
                            index = self.ebay_environment_combo.findText(value)
                            if index >= 0:
                                self.ebay_environment_combo.setCurrentIndex(index)
                        elif key == 'OLLAMA_BASE_URL':
                            self.ollama_url_input.setText(value)
                        elif key == 'OLLAMA_MODEL':
                            self.ollama_model_input.setText(value)
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")

    def save_ebay_credentials(self):
        """Save eBay credentials to .env file."""
        client_id = self.ebay_client_id_input.text().strip()
        client_secret = self.ebay_client_secret_input.text().strip()
        environment = self.ebay_environment_combo.currentText()

        if not client_id or not client_secret:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter both Client ID and Client Secret"
            )
            return

        try:
            env_path = ".env"

            # Read existing .env content
            env_content = {}
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_content[key.strip()] = value.strip()

            # Update eBay credentials
            env_content['EBAY_CLIENT_ID'] = client_id
            env_content['EBAY_CLIENT_SECRET'] = client_secret
            env_content['EBAY_ENVIRONMENT'] = environment

            # Write back to .env file
            with open(env_path, 'w') as f:
                for key, value in env_content.items():
                    f.write(f"{key}={value}\n")

            QMessageBox.information(
                self,
                "Success",
                "eBay credentials saved successfully!\n\n"
                "Please restart ResellerOS for changes to take effect."
            )

            logger.info("eBay credentials saved to .env file")

        except Exception as e:
            logger.error(f"Failed to save eBay credentials: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save credentials: {str(e)}"
            )

    def save_ollama_settings(self):
        """Save Ollama settings to .env file."""
        ollama_url = self.ollama_url_input.text().strip()
        ollama_model = self.ollama_model_input.text().strip()

        if not ollama_url:
            ollama_url = "http://localhost:11434"
        if not ollama_model:
            ollama_model = "phi3"

        try:
            env_path = ".env"

            # Read existing .env content
            env_content = {}
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_content[key.strip()] = value.strip()

            # Update Ollama settings
            env_content['OLLAMA_BASE_URL'] = ollama_url
            env_content['OLLAMA_MODEL'] = ollama_model

            # Write back to .env file
            with open(env_path, 'w') as f:
                for key, value in env_content.items():
                    f.write(f"{key}={value}\n")

            QMessageBox.information(
                self,
                "Success",
                "Ollama settings saved successfully!\n\n"
                "Please restart ResellerOS for changes to take effect."
            )

            logger.info("Ollama settings saved to .env file")

            # Refresh Ollama status
            self.check_ollama_status()

        except Exception as e:
            logger.error(f"Failed to save Ollama settings: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings: {str(e)}"
            )

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
