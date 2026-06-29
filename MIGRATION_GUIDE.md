# Database Migration Guide

## Overview
This migration script updates your booking-engine database schema with all recent enhancements.

## Changes Applied

### Booking Table Updates
1. **`status` column (VARCHAR 20)** - Tracks booking status
   - Default: `'active'`
   - Values: `'active'` or `'canceled'`
   - Indexed for performance
   - Enables soft delete functionality

2. **`canceled_at` column (DATETIME)** - Timestamp when booking was canceled
   - NULL for active bookings
   - Set to cancellation time for canceled bookings

3. **`comments` column (VARCHAR 200)** - Additional notes for bookings
   - Optional field for special requests or notes
   - Max 200 characters

### Indexes Created
- `ix_booking_status` - For filtering active/canceled bookings
- `ix_booking_checkin` - For date range queries
- `ix_booking_checkout` - For date range queries
- `ix_booking_room_id` - For room-specific queries

## How to Use

### Step 1: Backup Your Database
```bash
cd ~/Downloads/hello/booking-engine
cp instance/hotel.db instance/hotel.db.backup
```

### Step 2: Run Migration
```bash
# Make sure you're in the booking-engine directory
cd ~/Downloads/hello/booking-engine

# Activate virtual environment
source venv/bin/activate

# Run the migration script
python migrate_database.py
```

### Step 3: Verify
The script will:
- Check existing columns
- Add missing columns
- Create indexes
- Update existing data to set default values
- Show a summary of changes

### Step 4: Restart Server
```bash
# Stop the current server (Ctrl+C if running)
# Then start it again
python app.py
```

## What This Migration Enables

### 1. Soft Delete System
- Bookings are now "canceled" instead of deleted
- Maintains data integrity and history
- Prevents orphaned payment records
- View canceled bookings in Reports page

### 2. Comments Field
- Add special requests or notes to bookings
- Visible in:
  - Booking form (book.html)
  - Edit booking form (edit_booking.html)
  - Booking list (bookings.html)
  - Calendar popups (dashboard.html, month.html)

### 3. Checkout Day Indicators
- Calendar shows ◐ symbol on checkout days
- Diagonal red/white background indicates guest leaving
- Helps identify when rooms become available
- Always displayed for all users

## Troubleshooting

### Error: "database is locked"
- Stop the Flask server
- Close any database browser tools
- Try migration again

### Error: "no such table: booking"
- Ensure you're running from the correct directory
- Check that instance/hotel.db exists
- Database path should be: `instance/hotel.db`

### Migration shows "already exists" messages
- This is normal! The script is idempotent
- It safely skips columns that already exist
- You can run it multiple times without issues

### Changes not visible after migration
1. Restart the Flask server
2. Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
3. Clear browser cache if needed

## Rolling Back (if needed)

If you need to revert changes:

```bash
cd ~/Downloads/hello/booking-engine

# Stop the server
# Restore from backup
cp instance/hotel.db.backup instance/hotel.db

# Restart server
python app.py
```

## Manual Verification

To manually check the migration was successful:

```bash
# Open SQLite database
sqlite3 instance/hotel.db

# Check booking table structure
.schema booking

# Verify new columns exist
PRAGMA table_info(booking);

# Check indexes
.indices booking

# Exit
.quit
```

You should see:
- `status` column with type `VARCHAR(20)`
- `canceled_at` column with type `DATETIME`
- `comments` column with type `VARCHAR(200)`
- Indexes: `ix_booking_status`, `ix_booking_checkin`, `ix_booking_checkout`, `ix_booking_room_id`

## Support

If you encounter issues:
1. Check that all files are in the correct location
2. Ensure virtual environment is activated
3. Verify Python version is 3.7 or higher
4. Make sure SQLite3 is available
5. Check file permissions on instance/hotel.db

## Summary of Files Modified

The migration affects:
- `instance/hotel.db` - Database schema updated
- No code files are modified by the migration
- All application features should work immediately after migration

## What to Test After Migration

1. **Create a new booking** - Check comments field saves
2. **Edit a booking** - Verify comments display and update
3. **Cancel a booking** - Confirm soft delete works (status becomes 'canceled')
4. **View Reports** - Check canceled bookings section appears
5. **Calendar views** - Verify checkout day indicators show (◐ symbol)
6. **Mobile view** - Test popup doesn't scroll background

All features should work seamlessly after running this migration!
