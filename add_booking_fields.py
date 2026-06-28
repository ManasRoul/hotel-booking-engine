#!/usr/bin/env python3
"""
Migration script to add adults, children, and mattress fields to Booking table.
Run this script to update your existing database.
"""

import os
import sys
from app import app, db
from sqlalchemy import text

def migrate():
    """Add new columns to the booking table."""
    with app.app_context():
        # Get database type
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        
        if 'sqlite' in db_uri:
            # SQLite migration
            print("Detected SQLite database")
            with db.engine.connect() as conn:
                try:
                    conn.execute(text("ALTER TABLE booking ADD COLUMN adults INTEGER DEFAULT 1"))
                    conn.commit()
                    print("✓ Added 'adults' column")
                except Exception as e:
                    if 'duplicate column name' in str(e).lower():
                        print("⊘ Column 'adults' already exists")
                    else:
                        print(f"✗ Error adding 'adults': {e}")
                
                try:
                    conn.execute(text("ALTER TABLE booking ADD COLUMN children INTEGER DEFAULT 0"))
                    conn.commit()
                    print("✓ Added 'children' column")
                except Exception as e:
                    if 'duplicate column name' in str(e).lower():
                        print("⊘ Column 'children' already exists")
                    else:
                        print(f"✗ Error adding 'children': {e}")
                
                try:
                    conn.execute(text("ALTER TABLE booking ADD COLUMN mattress INTEGER DEFAULT 0"))
                    conn.commit()
                    print("✓ Added 'mattress' column")
                except Exception as e:
                    if 'duplicate column name' in str(e).lower():
                        print("⊘ Column 'mattress' already exists")
                    else:
                        print(f"✗ Error adding 'mattress': {e}")
                    
        elif 'mysql' in db_uri:
            # MySQL migration
            print("Detected MySQL database")
            with db.engine.connect() as conn:
                try:
                    conn.execute(text("ALTER TABLE booking ADD COLUMN adults INT DEFAULT 1"))
                    conn.commit()
                    print("✓ Added 'adults' column")
                except Exception as e:
                    if 'duplicate column' in str(e).lower():
                        print("⊘ Column 'adults' already exists")
                    else:
                        print(f"✗ Error adding 'adults': {e}")
                
                try:
                    conn.execute(text("ALTER TABLE booking ADD COLUMN children INT DEFAULT 0"))
                    conn.commit()
                    print("✓ Added 'children' column")
                except Exception as e:
                    if 'duplicate column' in str(e).lower():
                        print("⊘ Column 'children' already exists")
                    else:
                        print(f"✗ Error adding 'children': {e}")
                
                try:
                    conn.execute(text("ALTER TABLE booking ADD COLUMN mattress INT DEFAULT 0"))
                    conn.commit()
                    print("✓ Added 'mattress' column")
                except Exception as e:
                    if 'duplicate column' in str(e).lower():
                        print("⊘ Column 'mattress' already exists")
                    else:
                        print(f"✗ Error adding 'mattress': {e}")
        else:
            print(f"Unknown database type: {db_uri}")
            return False
        
        print("\n✓ Migration completed successfully!")
        print("Note: Existing bookings will have default values (adults=1, children=0, mattress=0)")
        return True

if __name__ == '__main__':
    print("=" * 60)
    print("BOOKING FIELDS MIGRATION")
    print("=" * 60)
    print("This will add the following columns to the booking table:")
    print("  - adults (default: 1)")
    print("  - children (default: 0)")
    print("  - mattress (default: 0)")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response in ['yes', 'y']:
        migrate()
    else:
        print("Migration cancelled.")
