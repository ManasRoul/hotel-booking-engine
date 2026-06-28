# 🏨 Hotel Booking Engine

A full-featured hotel room booking system built with Flask, featuring real-time availability, user management, and comprehensive reporting.

---

## ✨ Features

### 📅 Booking Management
- Real-time room availability calendar
- Multi-day booking support
- Check-in/Check-out tracking
- Booking conflict prevention
- Guest information management
- Advance payment tracking

### 🏠 Room Management
- Room creation and configuration
- Room types (Single, Double, Suite, etc.)
- AC/Non-AC options
- Dynamic pricing per room
- Monthly pricing variations
- Room blocking/unavailability management

### 👥 User Management
- Multi-user support with role-based access
- Owner (Admin) and Contributor roles
- User color coding for easy identification
- Secure password hashing
- Session management

### 📊 Reports & Analytics
- Monthly booking reports
- Revenue tracking
- Room occupancy statistics
- Guest history
- Payment summaries
- Export to CSV

### 🎨 User Interface
- Clean, modern design
- Responsive layout (mobile-friendly)
- Color-coded bookings by user
- Intuitive navigation
- Month/Block view for availability
- Quick booking from calendar

---

## 🛠️ Technology Stack

- **Backend:** Flask (Python 3.7+)
- **Database:** SQLite (development) / MySQL (production)
- **ORM:** Flask-SQLAlchemy
- **Frontend:** HTML5, CSS3, JavaScript
- **Security:** Werkzeug password hashing
- **Deployment:** Passenger WSGI

---

## 📁 Project Structure

```
booking-engine/
├── app.py                      # Main application file
├── passenger_wsgi.py           # WSGI entry point for deployment
├── setup_database.py          # Database setup script (creates tables & admin user)
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration (create from .env.example)
├── .env.example               # Environment template
├── .htaccess                  # Apache configuration
│
├── static/                    # Static assets
│   └── css/
│       ├── base.css          # Base styles
│       ├── login.css         # Login page styles
│       ├── dashboard.css     # Dashboard styles
│       ├── rooms.css         # Room management styles
│       ├── book.css          # Booking form styles
│       ├── month.css         # Monthly calendar styles
│       ├── block.css         # Block view styles
│       ├── bookings.css      # Booking list styles
│       ├── users.css         # User management styles
│       └── reports.css       # Reports page styles
│
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── login.html           # Login page
│   ├── dashboard.html       # Main dashboard
│   ├── rooms.html           # Room management
│   ├── room_detail.html     # Room details/pricing
│   ├── book.html            # Booking form
│   ├── month.html           # Monthly availability view
│   ├── block.html           # Block/grid view
│   ├── bookings.html        # Booking list
│   ├── users.html           # User management
│   └── reports.html         # Reports & analytics
│
├── instance/                # Instance-specific files (auto-created)
│   └── hotel.db            # SQLite database (development)
│
└── Documentation/           # Guides and documentation
    ├── README.md            # This file
    ├── DEPLOYMENT_GUIDE.md  # Full deployment guide
    ├── QUICK_START.md       # Quick setup checklist
    └── SHARED_HOSTING_USERS.md  # User creation guide
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup

1. **Clone or download the project**

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```
   
   For local development, default settings work fine (SQLite database).

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Initialize database and create admin user:**
   ```bash
   python setup_database.py
   ```
   
   This creates all tables and an admin user:
   - Username: `admin`
   - Password: `admin123`

7. **Open browser:**
   Navigate to `http://localhost:5000/login`

---

## 🌐 Production Deployment

For deploying to shared hosting (cPanel, Bluehost, Hostinger, etc.):

### Quick Steps

1. **Set up MySQL database** in cPanel
2. **Configure `.env`** with MySQL credentials
3. **Upload files** via FTP/SFTP (including `setup_database.py`)
4. **Install dependencies** in virtual environment
5. **Run `setup_database.py`** to create tables and admin user
6. **Restart application**

### Detailed Guides

- **Quick deployment:** See [QUICK_START.md](QUICK_START.md)
- **Full deployment guide:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **User creation:** See [SHARED_HOSTING_USERS.md](SHARED_HOSTING_USERS.md)

---

## 📖 Usage Guide

### Login
- Navigate to `/login`
- Enter username and password
- System redirects to dashboard

### Dashboard
- View quick stats (total bookings, available rooms, etc.)
- Navigate to different sections

### Room Management
1. Go to "Rooms" section
2. Click "Add Room" to create new rooms
3. Configure room number, type, AC/Non-AC, and base price
4. Click on room to edit monthly pricing

### Creating Bookings
1. Go to "Month View" or "Block View"
2. Click on available date/room
3. Fill in guest details, dates, and payment info
4. Submit booking

### Managing Bookings
1. Go to "Bookings" section
2. View all bookings
3. Filter by status (Upcoming, In-House, Checked-Out, Cancelled)
4. Edit or cancel bookings as needed

### User Management (Owner only)
1. Go to "Users" section
2. Add new users with username, password, role, and color
3. Delete users when needed

### Reports
1. Go to "Reports" section
2. Select date range
3. View revenue, occupancy, and booking statistics
4. Export to CSV for further analysis

---

## 👤 User Roles

### Owner (Admin)
- Full system access
- Create/edit/delete rooms
- Create/edit/delete bookings
- Manage users
- View all reports
- Configure pricing

### Contributor
- Create/edit bookings
- View room availability
- View own bookings
- Limited reporting access
- Cannot manage rooms or users

---

## 🔒 Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Role-based access control
- SQL injection prevention (SQLAlchemy ORM)
- CSRF protection
- Secure session cookies
- Environment variable configuration

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database
USE_MYSQL=False              # True for production, False for development
DB_HOST=localhost
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=hotel_booking
DB_PORT=3306

# Security
SECRET_KEY=your-secret-key   # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
```

### Database Configuration

**Development (SQLite):**
- Set `USE_MYSQL=False` in `.env`
- Database file: `instance/hotel.db`
- No additional setup needed

**Production (MySQL):**
- Set `USE_MYSQL=True` in `.env`
- Configure MySQL credentials in `.env`
- Database tables created automatically on first run

---

## 📊 Database Schema

### Tables

**User**
- id, username, password_hash, color, role

**Room**
- id, number, room_type, ac_type, price_per_day

**RoomPrice**
- id, room_id, year, month, price_per_day

**Booking**
- id, room_id, user_id, guest_name, guest_phone, check_in, check_out, status, advance_paid

**BlockedRoom**
- id, room_id, user_id, blocked_by, reason, start_date, end_date

---

## 🐛 Troubleshooting

### Common Issues

**Database errors:**
- Check MySQL credentials in `.env`
- Verify database exists
- Ensure user has proper privileges

**Static files not loading:**
- Check `static/` folder exists
- Verify file paths in templates
- Clear browser cache

**Login issues:**
- Verify user exists in database
- Check password was hashed correctly
- Clear cookies and try again

**500 Internal Server Error:**
- Check error logs
- Verify all dependencies installed
- Check file permissions (644 for files, 755 for directories)

### Debug Mode

For local development, the app runs in debug mode by default. Check `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

**⚠️ Never enable debug mode in production!**

---

## 🔄 Updating the Application

### Local Development
```bash
git pull  # If using version control
source venv/bin/activate
pip install -r requirements.txt --upgrade
python app.py
```

### Production (Shared Hosting)
1. Upload modified files via FTP
2. Update dependencies if needed:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt --upgrade
   ```
3. Restart application (method varies by host)
   - cPanel: Restart Python App
   - Or: `touch tmp/restart.txt` in app directory

---

## 📝 License

This project is proprietary. All rights reserved.

---

## 🤝 Support

For issues or questions:

1. Check the documentation in this folder
2. Review error logs
3. Verify configuration settings
4. Contact your hosting provider for server-specific issues

---

## 🎯 Roadmap / Future Enhancements

- [ ] Email notifications for bookings
- [ ] SMS notifications
- [ ] Online payment integration
- [ ] Guest portal for self-booking
- [ ] Mobile app
- [ ] Advanced reporting with charts
- [ ] Multi-property support
- [ ] Housekeeping management
- [ ] Inventory management

---

## 🌟 Credits

Built with Flask and modern web technologies for efficient hotel management.

**Version:** 1.0.0  
**Last Updated:** June 2026

---

## 📞 Quick Links

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [Quick Start](QUICK_START.md) - Fast deployment checklist
- [User Management](SHARED_HOSTING_USERS.md) - Creating and managing users

---

**Happy Hotel Management! 🏨✨**
