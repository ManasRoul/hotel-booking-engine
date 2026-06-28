# Hotel Booking Engine - Deployment Guide

This guide will help you deploy your Hotel Booking Engine to a shared hosting environment with MySQL database.

---

## 📋 Prerequisites

Before deploying, make sure you have:

- **Shared Hosting Account** with:
  - Python 3.7+ support
  - MySQL database access
  - cPanel or FTP access
  - SSH access (recommended but not required)
  - Passenger WSGI support (most shared hosts have this)
  
- **MySQL Database** with:
  - Database name
  - Database username
  - Database password
  - Database host (usually `localhost`)

---

## 🚀 Step-by-Step Deployment

### Step 1: Configure MySQL Database

1. **Login to cPanel** on your hosting account

2. **Create MySQL Database:**
   - Go to "MySQL Databases"
   - Create a new database (e.g., `your_username_hotel`)
   - Note down the full database name (usually prefixed with your username)

3. **Create MySQL User:**
   - Create a new user with a strong password
   - Note down username and password

4. **Add User to Database:**
   - Grant **ALL PRIVILEGES** to the user for your database
   - This allows the app to create tables and manage bookings

5. **Note Your MySQL Details:**
   ```
   Host: localhost (or specific host from hosting provider)
   Database Name: your_username_hotel
   Username: your_username_hoteluser
   Password: your_secure_password
   Port: 3306 (default)
   ```

---

### Step 2: Prepare Configuration File

1. **Create `.env` file** in your project root (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. **Update the `.env` file** with your actual credentials:
   ```env
   # Database Configuration
   USE_MYSQL=True
   DB_HOST=localhost
   DB_USER=your_username_hoteluser
   DB_PASSWORD=your_secure_password
   DB_NAME=your_username_hotel
   DB_PORT=3306
   
   # Security
   SECRET_KEY=generate-a-long-random-string-here
   ```

3. **Generate a secure SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Copy the output and paste it as your SECRET_KEY value.

⚠️ **Security Note:** Never commit `.env` file with real credentials to version control!

---

### Step 3: Prepare Files for Upload

**Files/Folders to Upload:**
```
booking-engine/
├── app.py                    ✅ Upload
├── passenger_wsgi.py         ✅ Upload
├── setup_database.py         ✅ Upload (database setup script)
├── requirements.txt          ✅ Upload
├── .env                      ✅ Upload (with your credentials)
├── .htaccess                 ✅ Upload
├── static/                   ✅ Upload entire folder
│   └── css/
├── templates/                ✅ Upload entire folder
│   └── *.html
└── instance/                 ✅ Create empty folder
```

**Do NOT Upload:**
```
❌ venv/               (will create on server)
❌ __pycache__/        (auto-generated)
❌ .git/               (not needed)
❌ .env.example        (template only)
❌ *.pyc files         (compiled Python)
❌ .DS_Store           (Mac files)
❌ hotel.db            (local SQLite - not needed for MySQL)
```

---

### Step 4: Upload Files to Server

#### Option A: Using FTP/SFTP (FileZilla, Cyberduck)
1. Connect to your hosting via FTP
2. Navigate to your public_html or app directory
3. Upload all files maintaining folder structure
4. Ensure file permissions are correct (644 for files, 755 for directories)

#### Option B: Using cPanel File Manager
1. Compress your project folder locally (zip)
2. Upload the zip file via cPanel File Manager
3. Extract the zip in your desired directory
4. Delete the zip file after extraction

#### Option C: Using SSH (if available)
```bash
# On your local machine
scp -r booking-engine/* username@yourhost.com:~/public_html/

# Or use rsync
rsync -avz --exclude 'venv' --exclude '.git' booking-engine/ username@yourhost.com:~/public_html/
```

---

### Step 5: Install Python Dependencies

1. **SSH into your server** (or use cPanel Terminal)

2. **Navigate to your app directory:**
   ```bash
   cd ~/public_html  # or wherever you uploaded files
   ```

3. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   ```

4. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Verify installation:**
   ```bash
   pip list
   ```
   You should see Flask, Flask-SQLAlchemy, mysql-connector-python, etc.

---

### Step 6: Initialize Database

**Option A: Automated Setup (Recommended)**

Use the provided setup script to create all tables and admin user in one go:

```bash
# Navigate to app directory
cd ~/public_html  # or your app directory

# Activate virtual environment
source venv/bin/activate

# Run setup script
python3 setup_database.py
```

This will:
- Create all database tables (user, room, booking, etc.)
- Create an admin user (username: `admin`, password: `admin123`)
- Verify the setup

**Option B: Manual Setup**

Create tables manually:

```bash
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database tables created successfully!')"
```

Note: The database tables will also be created automatically when the app first runs (handled by `passenger_wsgi.py`).

---

### Step 7: Configure Web Server

#### For Passenger WSGI (most common):

Your `passenger_wsgi.py` file is already configured. Just ensure:

1. The file is in your app root directory
2. The file has correct permissions (644)

#### If using cPanel:

1. Go to "Setup Python App" in cPanel
2. Create new application:
   - Python version: 3.7+ (choose latest available)
   - Application root: `/home/username/public_html`
   - Application URL: your domain or subdomain
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`
3. Click "Create"
4. In the configuration page:
   - Add environment variables from your `.env` file
   - Save changes

---

### Step 8: Create Initial Admin User

**If you used `setup_database.py` in Step 6, this is already done!**

Default credentials:
- Username: `admin`
- Password: `admin123`
- Role: `owner`

⚠️ **Change this password immediately after first login!**

**Manual User Creation (if needed):**

See **SHARED_HOSTING_USERS.md** for detailed instructions, or use:

```python
from app import app, db, User

with app.app_context():
    admin = User(username='admin', role='owner')
    admin.set_password('your_secure_password')
    db.session.add(admin)
    db.session.commit()
    print('Admin user created!')
```

---

### Step 9: Test Your Deployment

1. **Visit your website:** `https://yourdomain.com`
2. You should be redirected to the login page
3. Login with your admin credentials
4. Test creating:
   - Rooms
   - Bookings
   - User management

---

## 🔧 Troubleshooting

### Issue: 500 Internal Server Error

**Check error logs:**
```bash
tail -f ~/logs/error_log  # Location varies by host
```

**Common causes:**
- Missing dependencies: Reinstall `requirements.txt`
- Wrong database credentials: Check `.env` file
- File permissions: Set to 644 for files, 755 for folders
- Virtual environment not activated in `passenger_wsgi.py`

### Issue: Database Connection Failed

**Verify credentials:**
```bash
mysql -h localhost -u your_user -p your_database
```

**Check if MySQL is accessible:**
- Some hosts use socket connections instead of TCP
- Contact your hosting provider for correct connection details

### Issue: CSS/Static Files Not Loading

**Check file paths in templates:**
- Ensure `{{ url_for('static', filename='css/...') }}` is used
- Verify static folder was uploaded
- Check .htaccess rules

### Issue: Application Not Starting

**Check passenger_wsgi.py logs:**
- Look for import errors
- Verify Python version compatibility
- Ensure all dependencies are installed in venv

---

## 🔒 Security Checklist

- [ ] Changed SECRET_KEY from default
- [ ] Set strong database password
- [ ] Set strong admin user password
- [ ] `.env` file not committed to git
- [ ] Database user has only necessary privileges
- [ ] File permissions set correctly
- [ ] HTTPS enabled (SSL certificate installed)
- [ ] Regular backups configured

---

## 📦 File Permissions Guide

```bash
# Set correct permissions
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
chmod 600 .env  # More restrictive for sensitive file
```

---

## 🔄 Updating Your Application

To update your deployed app:

1. Make changes locally and test
2. Upload changed files via FTP/SCP
3. If dependencies changed:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt --upgrade
   ```
4. Restart application (varies by host, often via cPanel or `touch tmp/restart.txt`)

---

## 📞 Getting Help

If you encounter issues:

1. Check your hosting provider's documentation for Python/WSGI apps
2. Review error logs in cPanel or via SSH
3. Verify all steps in this guide were followed
4. Contact your hosting support for server-specific help

---

## 🎉 Success!

Once deployed, your Hotel Booking Engine will be live at your domain. Users can:
- Login with their credentials
- Book rooms with real-time availability
- Manage bookings and view reports
- Administrators can manage rooms, users, and system settings

**Happy Hosting! 🏨**
