#!/bin/bash

# Discord MBTI Personality Bot - Run Script
# Quick script to run the bot

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Sync database first
echo "🔄 Syncing database with Turso..."
python -m src.sync_db

# Run the bot
echo ""
echo "🤖 Starting Discord MBTI Personality Bot..."
python -m src.main
