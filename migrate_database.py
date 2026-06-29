#!/usr/bin/env python3
"""
Comprehensive database migration script for booking-engine
This script will update your database schema to include all recent changes.

Run this script once to apply all migrations:
    python migrate_database.py

This script is idempotent - safe to run multiple times.
Supports both SQLite (local) and MySQL (shared hosting).
"""

import sys
from datetime import datetime
import os

# Load environment variables from .env if it exists
env_file = '.env'
if os.path.exists(env_file):
    print(f"📄 Loading environment variables from {env_file}...")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    print("✅ Environment variables loaded\n")

# Check which database to use based on environment variables
USE_MYSQL = os.environ.get('USE_MYSQL', 'False') == 'True'

if USE_MYSQL:
    MYSQL_USER = os.environ.get('DB_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('DB_PASSWORD', '')
    MYSQL_HOST = os.environ.get('DB_HOST', 'localhost')
    MYSQL_PORT = os.environ.get('DB_PORT', '3306')
    MYSQL_DATABASE = os.environ.get('DB_NAME', 'hotel_booking')

# Try importing database libraries
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

DATABASE_PATH = 'instance/hotel.db'

def get_column_names_mysql(cursor, table_name):
    """Get list of column names for a table (MySQL)."""
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    return [column[0] for column in cursor.fetchall()]

def get_column_names_sqlite(cursor, table_name):
    """Get list of column names for a table (SQLite)."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [column[1] for column in cursor.fetchall()]

def migrate_booking_table_mysql(conn, cursor):
    """Add status, canceled_at, and comments columns to booking table (MySQL)."""
    columns = get_column_names_mysql(cursor, 'booking')
    changes_made = []
    
    # 1. Add status column
    if 'status' not in columns:
        cursor.execute("""
            ALTER TABLE booking 
            ADD COLUMN status VARCHAR(20) DEFAULT 'active'
        """)
        cursor.execute("CREATE INDEX ix_booking_status ON booking(status)")
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

def migrate_booking_table_sqlite(conn):
    """Add status, canceled_at, and comments columns to booking table (SQLite)."""
    cursor = conn.cursor()
    columns = get_column_names_sqlite(cursor, 'booking')
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

def cleanup_old_columns(cursor, is_mysql):
    """Remove any old/deprecated columns if they exist."""
    get_columns = get_column_names_mysql if is_mysql else get_column_names_sqlite
    columns = get_columns(cursor, 'booking')
    changes_made = []
    
    # Check if 'notes' column exists (old version that was renamed to comments)
    if 'notes' in columns:
        print("   ⚠️  Found old 'notes' column - this was renamed to 'comments'")
        print("   ℹ️  If you have data in 'notes', it should have been migrated to 'comments'")
        changes_made.append("⚠️  Old 'notes' column detected (already migrated to 'comments')")
    
    return changes_made

def migrate_user_table(cursor, is_mysql):
    """Check User table - show_checkout_indicator was removed."""
    get_columns = get_column_names_mysql if is_mysql else get_column_names_sqlite
    columns = get_columns(cursor, 'user')
    changes_made = []
    
    # The show_checkout_indicator column may exist but is no longer used
    if 'show_checkout_indicator' in columns:
        print("   ℹ️  'show_checkout_indicator' column exists but is no longer used (settings feature removed)")
        changes_made.append("ℹ️  Unused 'show_checkout_indicator' column found (can be ignored)")
    
    return changes_made

def verify_indexes_mysql(conn, cursor):
    """Ensure all necessary indexes exist (MySQL)."""
    changes_made = []
    
    # Get existing indexes
    cursor.execute("SHOW INDEX FROM booking")
    existing_indexes = {row[2] for row in cursor.fetchall()}
    
    indexes_to_create = [
        ("ix_booking_status", "CREATE INDEX ix_booking_status ON booking(status)"),
        ("ix_booking_checkin", "CREATE INDEX ix_booking_checkin ON booking(checkin)"),
        ("ix_booking_checkout", "CREATE INDEX ix_booking_checkout ON booking(checkout)"),
        ("ix_booking_room_id", "CREATE INDEX ix_booking_room_id ON booking(room_id)"),
    ]
    
    for index_name, create_sql in indexes_to_create:
        if index_name not in existing_indexes:
            cursor.execute(create_sql)
            changes_made.append(f"✅ Created index '{index_name}'")
        else:
            print(f"   ℹ️  Index '{index_name}' already exists")
    
    conn.commit()
    return changes_made

def verify_indexes_sqlite(conn):
    """Ensure all necessary indexes exist (SQLite)."""
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
    
    # Detect which database to use
    use_mysql = False
    db_type = "SQLite"
    
    if USE_MYSQL and MYSQL_AVAILABLE:
        use_mysql = True
        db_type = "MySQL"
        print(f"🔍 Detected USE_MYSQL=True in environment")
        print(f"📊 MySQL Database: {MYSQL_DATABASE}")
        print(f"📡 MySQL Host: {MYSQL_HOST}:{MYSQL_PORT}")
    elif os.path.exists(DATABASE_PATH) and SQLITE_AVAILABLE:
        use_mysql = False
        db_type = "SQLite"
        print(f"📂 Using SQLite database: {DATABASE_PATH}")
    else:
        print("❌ Error: No database configuration found!")
        print()
        print("For MySQL (shared hosting):")
        print("1. Create .env file with:")
        print("   USE_MYSQL=True")
        print("   DB_USER=your_username")
        print("   DB_PASSWORD=your_password")
        print("   DB_HOST=localhost")
        print("   DB_PORT=3306")
        print("   DB_NAME=your_database")
        print()
        print("2. Install MySQL connector: pip install mysql-connector-python")
        print()
        print("For SQLite (local development):")
        print("1. Make sure instance/hotel.db exists")
        print("2. Run the app first to create the database")
        sys.exit(1)
    
    print(f"🗄️  Database Type: {db_type}")
    print()
    
    try:
        # Connect to database
        if use_mysql:
            print(f"📡 Connecting to MySQL server at {MYSQL_HOST}:{MYSQL_PORT}...")
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE
            )
            cursor = conn.cursor()
        else:
            print(f"📂 Connecting to SQLite database...")
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
        
        print("✅ Connected successfully")
        print()
        
        # Backup reminder
        print("⚠️  IMPORTANT: Ensure you have a backup of your database before proceeding!")
        if use_mysql:
            print(f"   Database: {MYSQL_DATABASE} on {MYSQL_HOST}")
            print(f"   Backup command: mysqldump -u {MYSQL_USER} -p {MYSQL_DATABASE} > backup.sql")
        else:
            print(f"   Database location: {DATABASE_PATH}")
            print(f"   Backup command: cp {DATABASE_PATH} {DATABASE_PATH}.backup")
        
        response = input("\nContinue with migration? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            print("❌ Migration cancelled by user")
            sys.exit(0)
        
        print()
        print("-" * 70)
        
        # Run migrations
        all_changes = []
        
        print("📊 Migrating booking table...")
        if use_mysql:
            changes = migrate_booking_table_mysql(conn, cursor)
        else:
            changes = migrate_booking_table_sqlite(conn)
        all_changes.extend(changes)
        print()
        
        print("🧹 Checking for deprecated columns...")
        changes = cleanup_old_columns(cursor, use_mysql)
        all_changes.extend(changes)
        print()
        
        print("👤 Checking user table...")
        changes = migrate_user_table(cursor, use_mysql)
        all_changes.extend(changes)
        print()
        
        print("🔍 Verifying indexes...")
        if use_mysql:
            changes = verify_indexes_mysql(conn, cursor)
        else:
            changes = verify_indexes_sqlite(conn)
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
        
    except mysql.connector.Error as e:
        print()
        print("=" * 70)
        print(f"❌ MySQL Error: {e}")
        print("=" * 70)
        print()
        print("Troubleshooting:")
        print("1. Check your .env file settings")
        print("2. Verify database credentials")
        print("3. Ensure MySQL server is accessible")
        print("4. Check if database exists")
        sys.exit(1)
        
    except sqlite3.Error as e:
        print()
        print("=" * 70)
        print(f"❌ SQLite Error: {e}")
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
