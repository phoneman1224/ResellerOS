#!/bin/bash

# ResellerOS Quick Start Script

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run ./scripts/install.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the application
echo "Starting ResellerOS..."
python src/main.py
