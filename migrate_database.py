#!/usr/bin/env python3
"""
Comprehensive database migration script for booking-engine
This script will update your database schema to include all recent changes.

Run this script once to apply all migrations:
    python migrate_database.py

This script is idempotent - safe to run multiple times.
"""

import sqlite3
import sys
from datetime import datetime

DATABASE_PATH = 'instance/hotel.db'

def get_column_names(cursor, table_name):
    """Get list of column names for a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [column[1] for column in cursor.fetchall()]

def migrate_booking_table(conn):
    """Add status, canceled_at, and comments columns to booking table."""
    cursor = conn.cursor()
    columns = get_column_names(cursor, 'booking')
    changes_made = []
    
    # 1. Add status column
    if 'status' not in columns:
        cursor.execute("""
            ALTER TABLE booking 
            ADD COLUMN status VARCHAR(20) DEFAULT 'active'
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_booking_status ON booking(status)")
        changes_made.append("✅ Added 'status' column with default 'active'")
    else:
        print("   ℹ️  'status' column already exists")
    
    # 2. Add canceled_at column
    if 'canceled_at' not in columns:
        cursor.execute("""
            ALTER TABLE booking 
            ADD COLUMN canceled_at DATETIME
        """)
        changes_made.append("✅ Added 'canceled_at' column")
    else:
        print("   ℹ️  'canceled_at' column already exists")
    
    # 3. Add comments column
    if 'comments' not in columns:
        cursor.execute("""
            ALTER TABLE booking 
            ADD COLUMN comments VARCHAR(200)
        """)
        changes_made.append("✅ Added 'comments' column (VARCHAR 200)")
    else:
        print("   ℹ️  'comments' column already exists")
    
    # 4. Ensure all existing bookings have status='active' if NULL
    cursor.execute("UPDATE booking SET status = 'active' WHERE status IS NULL")
    updated_count = cursor.rowcount
    if updated_count > 0:
        changes_made.append(f"✅ Updated {updated_count} existing bookings to status='active'")
    
    conn.commit()
    return changes_made

def cleanup_old_columns(conn):
    """Remove any old/deprecated columns if they exist."""
    cursor = conn.cursor()
    columns = get_column_names(cursor, 'booking')
    changes_made = []
    
    # Check if 'notes' column exists (old version that was renamed to comments)
    if 'notes' in columns:
        # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
        print("   ⚠️  Found old 'notes' column - this was renamed to 'comments'")
        print("   ℹ️  If you have data in 'notes', it should have been migrated to 'comments'")
        changes_made.append("⚠️  Old 'notes' column detected (already migrated to 'comments')")
    
    return changes_made

def migrate_user_table(conn):
    """Check User table - show_checkout_indicator was removed."""
    cursor = conn.cursor()
    columns = get_column_names(cursor, 'user')
    changes_made = []
    
    # The show_checkout_indicator column may exist but is no longer used
    if 'show_checkout_indicator' in columns:
        print("   ℹ️  'show_checkout_indicator' column exists but is no longer used (settings feature removed)")
        changes_made.append("ℹ️  Unused 'show_checkout_indicator' column found (can be ignored)")
    
    return changes_made

def verify_indexes(conn):
    """Ensure all necessary indexes exist."""
    cursor = conn.cursor()
    changes_made = []
    
    indexes_to_create = [
        ("ix_booking_status", "CREATE INDEX IF NOT EXISTS ix_booking_status ON booking(status)"),
        ("ix_booking_checkin", "CREATE INDEX IF NOT EXISTS ix_booking_checkin ON booking(checkin)"),
        ("ix_booking_checkout", "CREATE INDEX IF NOT EXISTS ix_booking_checkout ON booking(checkout)"),
        ("ix_booking_room_id", "CREATE INDEX IF NOT EXISTS ix_booking_room_id ON booking(room_id)"),
    ]
    
    for index_name, create_sql in indexes_to_create:
        cursor.execute(create_sql)
        changes_made.append(f"✅ Ensured index '{index_name}' exists")
    
    conn.commit()
    return changes_made

def main():
    print("=" * 70)
    print("🔄 Database Migration Script for Booking Engine")
    print("=" * 70)
    print()
    
    try:
        # Connect to database
        print(f"📂 Connecting to database: {DATABASE_PATH}")
        conn = sqlite3.connect(DATABASE_PATH)
        print("✅ Connected successfully")
        print()
        
        # Backup reminder
        print("⚠️  IMPORTANT: Ensure you have a backup of your database before proceeding!")
        print(f"   Database location: {DATABASE_PATH}")
        response = input("\nContinue with migration? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            print("❌ Migration cancelled by user")
            sys.exit(0)
        
        print()
        print("-" * 70)
        
        # Run migrations
        all_changes = []
        
        print("📊 Migrating booking table...")
        changes = migrate_booking_table(conn)
        all_changes.extend(changes)
        print()
        
        print("🧹 Checking for deprecated columns...")
        changes = cleanup_old_columns(conn)
        all_changes.extend(changes)
        print()
        
        print("👤 Checking user table...")
        changes = migrate_user_table(conn)
        all_changes.extend(changes)
        print()
        
        print("🔍 Verifying indexes...")
        changes = verify_indexes(conn)
        all_changes.extend(changes)
        print()
        
        print("-" * 70)
        print()
        
        # Summary
        if all_changes:
            print("✨ Migration Summary:")
            for change in all_changes:
                print(f"   {change}")
        else:
            print("✅ Database is already up to date - no changes needed!")
        
        print()
        print("=" * 70)
        print("🎉 Migration completed successfully!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Restart your Flask server if it's running")
        print("2. Test your application to ensure everything works correctly")
        print("3. The following features are now available:")
        print("   • Soft delete with status tracking (active/canceled)")
        print("   • Comments field for bookings (up to 200 characters)")
        print("   • Checkout day indicators in calendar views")
        print()
        
        conn.close()
        
    except sqlite3.Error as e:
        print()
        print("=" * 70)
        print(f"❌ Database Error: {e}")
        print("=" * 70)
        print()
        print("Troubleshooting:")
        print("1. Make sure the database file exists at:", DATABASE_PATH)
        print("2. Ensure no other process is using the database")
        print("3. Check file permissions")
        sys.exit(1)
        
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Unexpected Error: {e}")
        print("=" * 70)
        sys.exit(1)

if __name__ == '__main__':
    main()
