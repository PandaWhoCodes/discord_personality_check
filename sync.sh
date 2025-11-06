#!/bin/bash

# Discord MBTI Personality Bot - Database Sync Script
# Manually sync local database with Turso

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run sync
python -m src.sync_db
