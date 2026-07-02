# Quick Migration Commands

## Option 1: Automated Script (Recommended)
```bash
cd ~/Downloads/hello/booking-engine
./quick_migrate.sh
```

## Option 2: Manual Steps
```bash
# 1. Navigate to project directory
cd ~/Downloads/hello/booking-engine

# 2. Backup database (optional but recommended)
cp instance/hotel.db instance/hotel.db.backup

# 3. Activate virtual environment
source venv/bin/activate

# 4. Run migration
python migrate_database.py

# 5. Restart server
python app.py
```

## What Gets Updated

✅ **Booking Table:**
- `status` VARCHAR(20) - 'active' or 'canceled'
- `canceled_at` DATETIME - When booking was canceled
- `comments` VARCHAR(200) - Additional notes

✅ **Indexes:** Created for better query performance

✅ **Existing Data:** Updated to set default values

## Verify Migration Success

After running migration, you should see:
```
✅ Added 'status' column with default 'active'
✅ Added 'canceled_at' column
✅ Added 'comments' column (VARCHAR 200)
✅ Updated N existing bookings to status='active'
✅ Ensured index 'ix_booking_status' exists
```

## Test After Migration

1. Open http://127.0.0.1:5001
2. Create a new booking - add comments
3. View booking details - check comments appear
4. Cancel a booking - verify it doesn't get deleted
5. Check Reports page - see canceled bookings section

## Troubleshooting

**Database locked?**
```bash
# Stop the Flask server first
pkill -f "python.*app.py"
# Then run migration
```

**Permission denied?**
```bash
chmod +x quick_migrate.sh
```

**Module not found?**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

That's it! Migration should take less than 1 second to complete.
