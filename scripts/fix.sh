#!/bin/bash

# Quick fix script for existing installations

echo "Fixing ResellerOS installation..."
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found. Run ./scripts/install.sh first"
    exit 1
fi

echo "1. Fixing Python dependencies..."
# Uninstall problematic packages
pip uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip 2>/dev/null || true

echo "2. Reinstalling dependencies..."
pip install --upgrade -r requirements.txt

echo ""
echo "✓ Fix complete!"
echo ""
echo "Now run the application:"
echo "  ./scripts/run.sh"
echo ""
