#!/bin/bash
# Quick migration runner that auto-confirms

cd "$(dirname "$0")"

# Backup database
if [ -f "instance/hotel.db" ]; then
    cp instance/hotel.db "instance/hotel.db.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup created"
fi

# Run migration with yes piped in
yes | python migrate_database.py

echo ""
echo "Migration complete! Restart your Flask server if it's running."
