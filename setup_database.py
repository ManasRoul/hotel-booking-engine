#!/usr/bin/env python3
"""
Database Setup Script for Hotel Booking Engine
This script creates all database tables and an initial admin user.
"""

import os
import sys

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
else:
    print(f"⚠️  Warning: {env_file} file not found!")
    print("   Make sure database configuration is set in environment variables.\n")

# Import Flask app and database
try:
    from app import app, db, User
    print("✅ Successfully imported Flask app and models\n")
except ImportError as e:
    print(f"❌ ERROR: Failed to import app components: {e}")
    print("   Make sure you're in the correct directory and Flask is installed.")
    sys.exit(1)

def create_tables():
    """Create all database tables"""
    print("=" * 60)
    print("STEP 1: Creating Database Tables")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            print("✅ Database tables created successfully!")
            print("\nTables created:")
            print("  📋 user           - User accounts and authentication")
            print("  🏠 room           - Hotel rooms")
            print("  💰 room_price     - Monthly pricing for rooms")
            print("  📅 booking        - Customer bookings")
            print("  🚫 blocked_room   - Room blocking/unavailability")
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"\n📊 Total tables in database: {len(tables)}")
            print(f"   Tables: {', '.join(tables)}")
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR creating tables: {e}")
            import traceback
            traceback.print_exc()
            return False

def create_admin_user():
    """Create initial admin user"""
    print("\n" + "=" * 60)
    print("STEP 2: Creating Admin User")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Check if admin already exists
            existing_admin = User.query.filter_by(username='admin').first()
            
            if existing_admin:
                print("⚠️  Admin user already exists!")
                print(f"   Username: admin")
                print(f"   Role: {existing_admin.role}")
                return True
            
            # Create admin user
            admin = User(
                username='admin',
                role='owner',  # Owner has full access
                color='#667eea'  # Purple color
            )
            admin.set_password('admin123')  # Default password
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            print("\n" + "=" * 60)
            print("LOGIN CREDENTIALS")
            print("=" * 60)
            print("🔐 Username: admin")
            print("🔑 Password: admin123")
            print("👤 Role:     owner (full access)")
            print("\n⚠️  IMPORTANT: Change this password after first login!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR creating admin user: {e}")
            import traceback
            traceback.print_exc()
            return False

def verify_setup():
    """Verify the setup was successful"""
    print("\n" + "=" * 60)
    print("STEP 3: Verification")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Check tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['user', 'room', 'room_price', 'booking', 'blocked_room']
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                print(f"⚠️  Missing tables: {', '.join(missing_tables)}")
                return False
            
            print("✅ All required tables exist")
            
            # Check users exist
            user_count = User.query.count()
            print(f"✅ Users in database: {user_count}")
            
            if user_count > 0:
                users = User.query.all()
                print("\n👥 User List:")
                for user in users:
                    print(f"   - {user.username} ({user.role})")
            
            # Display database info
            print("\n📊 Database Information:")
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'mysql' in db_uri.lower():
                # Extract database name from URI (hide password)
                if '@' in db_uri:
                    parts = db_uri.split('@')
                    host_db = parts[1] if len(parts) > 1 else 'unknown'
                    if '/' in host_db:
                        db_name = host_db.split('/')[-1]
                        print(f"   Database: {db_name}")
                    print(f"   Type: MySQL")
                else:
                    print(f"   Type: MySQL")
            else:
                print(f"   Type: SQLite")
                print(f"   File: hotel.db")
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR during verification: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main setup function"""
    print("\n" + "=" * 60)
    print("🏨 HOTEL BOOKING ENGINE - DATABASE SETUP")
    print("=" * 60)
    print()
    
    # Step 1: Create tables
    if not create_tables():
        print("\n❌ Setup failed at table creation step.")
        sys.exit(1)
    
    # Step 2: Create admin user
    if not create_admin_user():
        print("\n❌ Setup failed at user creation step.")
        sys.exit(1)
    
    # Step 3: Verify everything
    if not verify_setup():
        print("\n⚠️  Setup completed with warnings.")
        sys.exit(1)
    
    # Success!
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Visit your website at: https://book.sagarbela.com/login")
    print("2. Login with username 'admin' and password 'admin123'")
    print("3. Change the admin password immediately")
    print("4. Start adding rooms and bookings!")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
