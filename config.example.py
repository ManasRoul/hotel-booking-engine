# MySQL Database Configuration for Shared Hosting
# Copy this file to config.py and fill in your actual database credentials

# MySQL Server Details (get these from your hosting provider)
MYSQL_HOST = 'localhost'  # or your MySQL server address
MYSQL_USER = 'your_username'
MYSQL_PASSWORD = 'your_password'
MYSQL_DATABASE = 'your_database_name'

# Example for typical shared hosting:
# MYSQL_HOST = 'localhost' or 'mysql.yourhosting.com'
# MYSQL_USER = 'username_booking'
# MYSQL_PASSWORD = 'strong_password_here'
# MYSQL_DATABASE = 'username_bookingdb'

# Notes:
# 1. Never commit config.py to version control (it contains passwords!)
# 2. config.py is already in .gitignore
# 3. For local development, you can still use SQLite (instance/hotel.db)
# 4. The migration script will auto-detect which database to use
