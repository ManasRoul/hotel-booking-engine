# 🚀 Quick Deployment Checklist

## Before You Start

- ✅ You have a shared hosting account with Python 3.7+ and MySQL support
- ✅ You have created a MySQL database
- ✅ You have MySQL credentials (host, username, password, database name)
- ✅ You have cPanel or FTP access

---

## ⚡ Quick Setup (5 Steps)

### 1️⃣ Configure Environment

Create `.env` file (copy from `.env.example`):

```env
USE_MYSQL=True
DB_HOST=localhost
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=your_database_name
DB_PORT=3306
SECRET_KEY=generate-random-string-here
```

💡 Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### 2️⃣ Upload Files

**Upload these via FTP/cPanel:**
```
✅ app.py
✅ passenger_wsgi.py
✅ setup_database.py
✅ requirements.txt
✅ .env (with your credentials)
✅ .htaccess
✅ static/ (entire folder)
✅ templates/ (entire folder)
✅ instance/ (create empty folder)
```

**DON'T upload:**
```
❌ venv/
❌ __pycache__/
❌ .git/
❌ hotel.db
❌ .DS_Store
```

---

### 3️⃣ Install Dependencies

**Via SSH:**
```bash
cd ~/public_html  # or your app directory

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Via cPanel Python App Setup:**
1. Go to "Setup Python App"
2. Create application with Python 3.7+
3. Set application root and startup file
4. Environment will be created automatically

---

### 4️⃣ Initialize Database & Create Admin User

**One-command setup (Recommended):**
```bash
source venv/bin/activate
python3 setup_database.py
```

This creates all tables AND admin user with:
- **Username:** `admin`
- **Password:** `admin123` (⚠️ change after first login!)

**Alternative - Manual setup:**
```bash
source venv/bin/activate
python3 -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database ready!')"
```

Note: Tables are also created automatically on first run by `passenger_wsgi.py`.

---

### 5️⃣ Restart Application

```bash
mkdir -p tmp
touch tmp/restart.txt
```

**Or via cPanel:**
- Go to "Setup Python App"
- Click "Restart"

**Note:** If you ran `setup_database.py` in step 4, admin user is already created!

---

## ✅ Test Your Deployment

1. Visit your website: `https://yourdomain.com`
2. You should see the login page
3. Login with admin credentials
4. Test creating a room and booking

---

## 🔧 If Something Goes Wrong

### Check Error Logs
```bash
tail -f ~/logs/error_log
# or
tail -f ~/public_html/app.log
```

### Common Issues

**500 Error:**
- Check `.env` file exists with correct credentials
- Verify virtual environment is activated
- Check file permissions (644 for files, 755 for directories)

**Database Connection Error:**
- Verify MySQL credentials in `.env`
- Test MySQL connection: `mysql -u user -p database`
- Check if database exists

**Static Files Not Loading:**
- Verify `static/` folder was uploaded
- Check .htaccess file is present
- Clear browser cache

**Can't Login:**
- Verify admin user was created
- Check password hash is correct
- Use phpMyAdmin to verify user exists in `user` table

---

## 📚 Need More Details?

- **Full deployment guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **User management:** [SHARED_HOSTING_USERS.md](SHARED_HOSTING_USERS.md)
- **Project overview:** [README.md](README.md)

---

## 🎉 You're All Set!

Your Hotel Booking Engine is now live! 🏨

**Login:** `https://yourdomain.com/login`

**Default credentials:**
- Username: `admin`
- Password: Whatever you set in step 5

**Remember to:**
- ✅ Change the default admin password
- ✅ Create additional users as needed
- ✅ Set up regular database backups
- ✅ Enable HTTPS/SSL certificate

**Happy Hosting!**
