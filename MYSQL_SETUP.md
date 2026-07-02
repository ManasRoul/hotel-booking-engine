# MySQL Setup for Shared Hosting

## Quick Setup

### Step 1: Install MySQL Connector

```bash
pip install mysql-connector-python
```

### Step 2: Create .env file

Create a `.env` file in your project root (same directory as app.py):

```bash
# MySQL Configuration for Shared Hosting
USE_MYSQL=True
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database_name

# Flask Configuration
SECRET_KEY=your-secret-key-change-this

# Timezone Configuration (optional, defaults to UTC)
# Common timezones: Asia/Kolkata, America/New_York, Europe/London, etc.
# See: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE=UTC
```

**Example .env for shared hosting (India):**
```bash
USE_MYSQL=True
DB_USER=sagarbel_booking
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=sagarbel_hotel
SECRET_KEY=random-secret-key-change-in-production-xyz123
TIMEZONE=Asia/Kolkata
```

### Step 3: Get Your Database Credentials

Your hosting provider (cPanel, Plesk, etc.) will provide:
- **Host**: Usually `localhost` or a specific server address
- **Username**: Your MySQL username
- **Password**: Your MySQL password  
- **Database Name**: The database you created

**Example locations:**
- **cPanel**: MySQL® Databases → Create Database
- **Plesk**: Databases → Add Database
- **Direct Admin**: MySQL Management

### Step 4: Run Migration

```bash
python migrate_database.py
```

The script will:
- Auto-detect MySQL from config.py
- Connect to your MySQL database
- Add all necessary columns and indexes

## How It Works

### Auto-Detection

The application and migration scripts check:
1. Is `USE_MYSQL=True` in `.env` file? → Use MySQL
2. Does `instance/hotel.db` exist? → Use SQLite
3. Neither? → Show setup instructions

### Database Support

| Environment | Database | Configuration |
|-------------|----------|---------------|
| Local Dev | SQLite | `instance/hotel.db` (default) |
| Shared Hosting | MySQL | `.env` file required |

### For Local Development (SQLite)

No configuration needed! Just run:
```bash
python app.py
```

The app will create `instance/hotel.db` automatically.

### For Shared Hosting (MySQL)

1. Create `.env` file with MySQL credentials
2. Run setup: `python setup_database.py`
3. Run migration: `python migrate_database.py`
4. Deploy your app!

## How app.py Connects to Database

The app automatically detects which database to use based on environment variables:

```python
# From app.py
if os.environ.get('USE_MYSQL', 'False') == 'True':
    db_user = os.environ.get('DB_USER', 'root')
    db_pass = os.environ.get('DB_PASSWORD', '')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '3306')
    db_name = os.environ.get('DB_NAME', 'hotel_booking')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
else:
    # Default to SQLite for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel.db'
```

**This means:**
- ✅ No code changes needed
- ✅ Just set environment variables in `.env` file
- ✅ Same code works for both local (SQLite) and production (MySQL)

## Troubleshooting

### Error: "No module named 'mysql'"

```bash
pip install mysql-connector-python
```

### Error: "Access denied for user"

Check your credentials in `.env` file:
- Username correct?
- Password correct?
- Database exists?

### Error: "Can't connect to MySQL server"

- Is MySQL host address correct in `.env`?
- Is your IP whitelisted (some hosts require this)?
- Is MySQL service running?

### Testing Connection

Create a test file `test_mysql.py`:

```python
import os
import mysql.connector

# Load .env file
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

try:
    conn = mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', '3306')),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Then run: `python test_mysql.py`

## Security Notes

1. **Never commit .env file** - It contains passwords!
2. Add `.env` to your `.gitignore` file
3. Use strong passwords for MySQL users
4. Restrict MySQL user privileges to only what's needed
5. For shared hosting, `.env` should only be readable by your user (chmod 600)

Example `.gitignore`:
```
.env
*.pyc
__pycache__/
instance/
venv/
.DS_Store
```

## Migration Commands

### Backup Before Migration

**MySQL:**
```bash
mysqldump -u your_user -p your_database > backup.sql
```

**SQLite:**
```bash
cp instance/hotel.db instance/hotel.db.backup
```

### Run Migration

```bash
python migrate_database.py
```

### Restore from Backup (if needed)

**MySQL:**
```bash
mysql -u your_user -p your_database < backup.sql
```

**SQLite:**
```bash
cp instance/hotel.db.backup instance/hotel.db
```

## Next Steps After Migration

1. ✅ Migration completed successfully
2. ✅ `.env` file configured with MySQL settings
3. ✅ `mysql-connector-python` installed in requirements.txt
4. Test your application locally: `python app.py`
5. Deploy to shared hosting
6. Run setup on production: `python setup_database.py`
7. Run migration on production: `python migrate_database.py`

## .env File Example

Create a `.env` file in your project root:

```bash
# Database Configuration
USE_MYSQL=True
DB_USER=your_mysql_username
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database_name

# Flask Configuration
SECRET_KEY=your-random-secret-key-change-this-in-production
```

That's it! Your application is now ready for production use on shared hosting.
