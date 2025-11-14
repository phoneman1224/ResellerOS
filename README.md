# ResellerOS

**Production-ready desktop application for eBay resellers**

ResellerOS is a comprehensive inventory management system designed specifically for eBay resellers. It combines powerful local AI assistance with seamless eBay integration to help you manage your inventory, track expenses, optimize pricing, and grow your business.

## Features

### 📦 Inventory Management
- Add, edit, and organize items with photos
- Track item status (Draft → Ready → Listed → Sold)
- Bulk operations and advanced filtering
- Photo management with upload and preview

### 💰 Financial Tracking
- Expense tracking and categorization
- Profit/loss calculations
- Sales analytics and reporting
- Revenue projections

### 🤖 AI Assistant (Powered by Ollama)
- Intelligent pricing suggestions based on market data
- SEO-optimized title generation
- Description writing assistance
- Automated category suggestions
- Graceful fallback when AI is unavailable

### 📊 Analytics Dashboard
- Real-time business metrics
- Profit margin analysis
- Inventory turnover rates
- Sales trends and forecasting

### 🔗 eBay Integration
- Secure OAuth authentication
- Direct listing creation
- Automatic sales sync
- Inventory synchronization
- Market research and competitive pricing

### 🔒 Security & Reliability
- Encrypted credential storage
- Automatic daily backups
- Offline-first architecture
- SQLite with WAL mode for data integrity
- Comprehensive error handling

## Requirements

- **Python 3.11 or higher**
- **Operating System:** Linux, macOS, or Windows
- **Optional:** Ollama for AI features (app works without it)
- **Internet:** Only required for eBay synchronization

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/ResellerOS.git
cd ResellerOS

# Run installation script
chmod +x scripts/install.sh
./scripts/install.sh
```

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.core.database import init_database; init_database()"

# Copy environment file
cp .env.example .env
# Edit .env with your eBay API credentials
```

## Usage

Start the application:

```bash
source venv/bin/activate
python src/main.py
```

## Architecture

ResellerOS uses a modern, layered architecture for maintainability and scalability.

## License

MIT License - see LICENSE file for details
