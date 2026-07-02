#!/bin/bash
# Quick Migration Script
# Run this to update your database schema in one command

set -e  # Exit on error

echo "=========================================="
echo "🔄 Quick Database Migration"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found"
    echo "Please run this script from the booking-engine directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "Please create it first: python3 -m venv venv"
    exit 1
fi

# Backup database
echo "📦 Creating backup..."
if [ -f "instance/hotel.db" ]; then
    cp instance/hotel.db instance/hotel.db.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup created: instance/hotel.db.backup.$(date +%Y%m%d_%H%M%S)"
else
    echo "⚠️  No existing database found - will create new one on first run"
fi

echo ""
echo "🚀 Running migration..."
echo ""

# Activate venv and run migration
source venv/bin/activate
python migrate_database.py

echo ""
echo "=========================================="
echo "✅ Migration complete!"
echo "=========================================="
echo ""
echo "Next: Restart your Flask server"
echo "  python app.py"
echo ""
