#!/bin/bash

# Discord MBTI Personality Bot - Setup Script
# This script sets up the development environment

set -e

echo "🤖 Discord MBTI Personality Bot - Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" 2>/dev/null; then
    echo "❌ Python 3.10+ is required. You have Python $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Please create .env file with your Discord bot token"
    echo "   See README.md for instructions"
else
    echo "✅ .env file found"
fi
echo ""

# Create data directory if it doesn't exist
mkdir -p data
echo "✅ Data directory ready"
echo ""

echo "========================================"
echo "✅ Setup complete!"
echo ""
echo "To start the bot:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the bot: python -m src.main"
echo ""
echo "Or use the run script: ./run.sh"
