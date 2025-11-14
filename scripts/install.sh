#!/bin/bash

# ResellerOS Installation Script

set -e  # Exit on error

echo "======================================"
echo "ResellerOS Installation"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}Error: Python 3.11+ required, found $python_version${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $python_version detected${NC}"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists, skipping...${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --quiet --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --quiet -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your eBay API credentials${NC}"
else
    echo -e "${YELLOW}.env file already exists, skipping...${NC}"
fi

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "from src.core.database import init_database; init_database()"
echo -e "${GREEN}✓ Database initialized${NC}"

# Create required directories
echo ""
echo "Creating required directories..."
mkdir -p uploads backups logs resources/icons
echo -e "${GREEN}✓ Directories created${NC}"

# Installation complete
echo ""
echo "======================================"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo "======================================"
echo ""
echo "To run ResellerOS:"
echo ""
echo "  1. Activate virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     python src/main.py"
echo ""
echo "Optional: Install Ollama for AI features"
echo "  Visit: https://ollama.ai"
echo "  Run: ollama pull phi3"
echo ""
echo "Configure eBay API credentials in .env file"
echo "  Get credentials from: https://developer.ebay.com/"
echo ""
