import os
from collections import defaultdict
from datetime import date as date_type, datetime, timedelta
from functools import wraps
import calendar
import csv
from io import StringIO

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database config from environment
if os.environ.get('USE_MYSQL', 'False') == 'True':
    db_user = os.environ.get('DB_USER', 'root')
    db_pass = os.environ.get('DB_PASSWORD', '')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '3306')
    db_name = os.environ.get('DB_NAME', 'hotel_booking')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
db = SQLAlchemy(app)


from werkzeug.security import generate_password_hash, check_password_hash


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def validate_length(value, max_len, field_name):
    """Return error string if value exceeds max_len, else None."""
    if value and len(value.strip()) > max_len:
        return f'{field_name} must be {max_len} characters or less.'
    return None


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    color = db.Column(db.String(7), default='#667eea')  # Hex color code
    role = db.Column(db.String(20), default='contributor')  # 'owner' or 'contributor'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_owner(self):
        return self.role == 'owner'


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), unique=True, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)
    ac_type = db.Column(db.String(10), nullable=False, default='AC')
    price_per_day = db.Column(db.Float, nullable=False)
    bookings = db.relationship('Booking', backref='room', lazy=True)
    monthly_prices = db.relationship('RoomPrice', backref='room', lazy=True, cascade='all, delete-orphan')


class RoomPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False, index=True)  # 1-12
    price_per_day = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('room_id', 'year', 'month', name='unique_room_month_price'),)


class BlockedRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)  # New: link to user
    blocked_by = db.Column(db.String(100), nullable=False)  # Keep for display/legacy
    reason = db.Column(db.String(200))
    start_date = db.Column(db.DateTime, nullable=False, index=True)
    end_date = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    room = db.relationship('Room', backref='blocks')
    user = db.relationship('User', backref='blocked_rooms')


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False, index=True)
    guest_name = db.Column(db.String(100), nullable=False)
    guest_phone = db.Column(db.String(20))
    id_number = db.Column(db.String(50))  # DL or Aadhaar
    payment_mode = db.Column(db.String(20))  # Cash or UPI
    payment_type = db.Column(db.String(20))  # Advance or Full
    total_amount = db.Column(db.Float, default=0)
    amount_received = db.Column(db.Float, default=0)
    booked_by = db.Column(db.String(100))
    receipt_no = db.Column(db.String(50))
    checkin = db.Column(db.DateTime, nullable=False, index=True)
    checkout = db.Column(db.DateTime, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    payment_mode = db.Column(db.String(20), nullable=False)  # Cash or UPI
    receipt_no = db.Column(db.String(50))
    notes = db.Column(db.String(200))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='payments')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if len(username) > 50 or len(password) > 128:
            error = 'Invalid username or password'
        else:
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['username'] = user.username
                session['user_role'] = user.role
                return redirect(url_for('dashboard'))
            error = 'Invalid username or password'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    year = request.args.get('year', datetime.now().year, type=int)
    current_month = datetime.now().month
    current_year = datetime.now().year
    rooms = Room.query.order_by(Room.number).all()
    bookings = Booking.query.filter(
        db.extract('year', Booking.checkin) <= year,
        db.extract('year', Booking.checkout) >= year
    ).all()
    blocks = BlockedRoom.query.filter(
        db.extract('year', BlockedRoom.start_date) <= year,
        db.extract('year', BlockedRoom.end_date) >= year
    ).all()

    # Pre-compute calendar data - build date-indexed lookup for O(1) per day
    year_start = date_type(year, 1, 1)
    year_end = date_type(year, 12, 31)
    
    # Build (room_id, date) -> booking mapping
    booking_by_room_date = {}
    for b in bookings:
        start = max(b.checkin.date(), year_start)
        end = min(b.checkout.date(), year_end + timedelta(days=1))
        d = start
        while d < end:
            booking_by_room_date[(b.room_id, d)] = b
            d += timedelta(days=1)
    
    # Build (room_id, date) -> [blocks] mapping
    blocks_by_room_date = defaultdict(list)
    for bl in blocks:
        start = max(bl.start_date.date(), year_start)
        end = min(bl.end_date.date(), year_end + timedelta(days=1))
        d = start
        while d < end:
            blocks_by_room_date[(bl.room_id, d)].append(bl)
            d += timedelta(days=1)

    cal_data = {}
    for month in range(1, 13):
        _, days_in_month = calendar.monthrange(year, month)
        cal_data[month] = {'days': days_in_month, 'rooms': {}}
        for room in rooms:
            room_days = {}
            for day in range(1, days_in_month + 1):
                current = date_type(year, month, day)
                booking = booking_by_room_date.get((room.id, current))
                if booking:
                    room_days[day] = {'status': 'booked', 'booking': booking}
                else:
                    matching_blocks = blocks_by_room_date.get((room.id, current))
                    if matching_blocks:
                        room_days[day] = {'status': 'blocked', 'blocks': matching_blocks, 'count': len(matching_blocks)}
                    else:
                        room_days[day] = {'status': 'available'}
            cal_data[month]['rooms'][room.id] = room_days

    return render_template('dashboard.html', year=year, rooms=rooms, bookings=bookings, blocks=blocks, cal_data=cal_data, current_month=current_month, current_year=current_year)


@app.route('/api/bookings/<int:year>/<int:month>')
@login_required
def api_month_bookings(year, month):
    """Return booking data for a specific month."""
    _, days_in_month = calendar.monthrange(year, month)
    month_start = datetime(year, month, 1)
    month_end = datetime(year, month, days_in_month, 23, 59, 59)

    rooms = Room.query.order_by(Room.number).all()
    bookings = Booking.query.filter(
        Booking.checkin <= month_end,
        Booking.checkout >= month_start
    ).all()

    data = {}
    for room in rooms:
        room_bookings = [b for b in bookings if b.room_id == room.id]
        days = {}
        for day in range(1, days_in_month + 1):
            current = datetime(year, month, day)
            booked = any(b.checkin <= current < b.checkout for b in room_bookings)
            days[day] = {
                'booked': booked,
                'guest': next((b.guest_name for b in room_bookings if b.checkin <= current < b.checkout), None)
            }
        data[room.number] = {'type': room.room_type, 'days': days}

    return jsonify(data)


@app.route('/month/<int:year>/<int:month>')
@login_required
def month_view(year, month):
    rooms = Room.query.order_by(Room.number).all()
    _, days_in_month = calendar.monthrange(year, month)
    month_start = datetime(year, month, 1)
    month_end = datetime(year, month, days_in_month, 23, 59, 59)
    bookings = Booking.query.filter(Booking.checkin <= month_end, Booking.checkout >= month_start).all()
    blocks = BlockedRoom.query.filter(BlockedRoom.start_date <= month_end, BlockedRoom.end_date >= month_start).all()
    month_name = calendar.month_name[month]
    return render_template('month.html', year=year, month=month, month_name=month_name,
                           days_in_month=days_in_month, rooms=rooms, bookings=bookings, blocks=blocks)


@app.route('/room/<int:room_id>')
@login_required
def room_detail(room_id):
    room = Room.query.get_or_404(room_id)
    bookings = Booking.query.filter_by(room_id=room_id).order_by(Booking.checkin.desc()).all()
    blocks = BlockedRoom.query.filter_by(room_id=room_id).order_by(BlockedRoom.start_date.desc()).all()
    
    # Get monthly prices for current year and next year
    current_year = datetime.now().year
    all_prices = RoomPrice.query.filter(
        RoomPrice.room_id == room_id,
        RoomPrice.year.in_([current_year, current_year + 1])
    ).all()
    prices_map = {(p.year, p.month): p.price_per_day for p in all_prices}
    monthly_prices = {}
    for year in [current_year, current_year + 1]:
        for month in range(1, 13):
            key = f"{year}-{month}"
            monthly_prices[key] = prices_map.get((year, month))
    
    return render_template('room_detail.html', room=room, bookings=bookings, blocks=blocks, 
                         monthly_prices=monthly_prices, current_year=current_year)


@app.route('/api/room/<int:room_id>/monthly-prices')
@login_required
def get_monthly_prices(room_id):
    room = Room.query.get_or_404(room_id)
    year = request.args.get('year', datetime.now().year, type=int)
    
    price_objs = {p.month: p.price_per_day for p in RoomPrice.query.filter_by(room_id=room_id, year=year).all()}
    prices = {month: price_objs.get(month, room.price_per_day) for month in range(1, 13)}
    
    return jsonify(prices)


@app.route('/api/room/<int:room_id>/set-monthly-price', methods=['POST'])
@login_required
def set_monthly_price(room_id):
    room = Room.query.get_or_404(room_id)
    data = request.get_json()
    year = data.get('year')
    month = data.get('month')
    price = data.get('price')
    
    if not all([year, month, price]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        price = float(price)
        if price <= 0:
            return jsonify({'success': False, 'error': 'Price must be positive'}), 400
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid price format'}), 400
    
    # Check if price already exists for this month
    price_obj = RoomPrice.query.filter_by(room_id=room_id, year=year, month=month).first()
    
    if price_obj:
        price_obj.price_per_day = price
        price_obj.updated_at = datetime.utcnow()
    else:
        price_obj = RoomPrice(room_id=room_id, year=year, month=month, price_per_day=price)
        db.session.add(price_obj)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Price updated successfully'})


@app.route('/api/room/<int:room_id>/clear-monthly-price', methods=['POST'])
@login_required
def clear_monthly_price(room_id):
    data = request.get_json()
    year = data.get('year')
    month = data.get('month')
    
    if not all([year, month]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    price_obj = RoomPrice.query.filter_by(room_id=room_id, year=year, month=month).first()
    if price_obj:
        db.session.delete(price_obj)
        db.session.commit()
    
    return jsonify({'success': True, 'message': 'Monthly price cleared'})


@app.route('/reports')
@login_required
def reports():
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    _, days_in_month = calendar.monthrange(year, month)
    month_start = datetime(year, month, 1)
    month_end = datetime(year, month, days_in_month, 23, 59, 59)

    rooms = Room.query.order_by(Room.number).all()
    bookings = Booking.query.filter(Booking.checkin <= month_end, Booking.checkout >= month_start).all()

    # Collection totals
    total_collected = sum(b.amount_received or 0 for b in bookings)
    cash_collected = sum(b.amount_received or 0 for b in bookings if b.payment_mode == 'Cash')
    upi_collected = sum(b.amount_received or 0 for b in bookings if b.payment_mode == 'UPI')

    # Occupancy by room for the month
    bookings_by_room = defaultdict(list)
    for b in bookings:
        bookings_by_room[b.room_id].append(b)

    room_occupancy = {}
    for room in rooms:
        room_bookings = bookings_by_room[room.id]
        occupied_days = sum(1 for day in range(1, days_in_month + 1)
                           if any(b.checkin.date() <= datetime(year, month, day).date() < b.checkout.date() for b in room_bookings))
        room_occupancy[room.id] = {'room': room, 'occupied': occupied_days, 'total': days_in_month,
                                    'percent': round(occupied_days / days_in_month * 100)}

    # Total occupancy by day
    daily_occupancy = {}
    total_rooms = len(rooms)
    for day in range(1, days_in_month + 1):
        current = datetime(year, month, day).date()
        occupied = sum(1 for room in rooms if any(b.checkin.date() <= current < b.checkout.date() for b in bookings_by_room[room.id]))
        daily_occupancy[day] = {'occupied': occupied, 'total': total_rooms,
                                'percent': round(occupied / total_rooms * 100) if total_rooms else 0}

    month_name = calendar.month_name[month]
    return render_template('reports.html', year=year, month=month, month_name=month_name,
                           days_in_month=days_in_month, total_collected=total_collected,
                           cash_collected=cash_collected, upi_collected=upi_collected,
                           room_occupancy=room_occupancy, daily_occupancy=daily_occupancy,
                           bookings=bookings, rooms=rooms)


@app.route('/reports/download/customer')
@login_required
def download_customer_report():
    """Download customer details report as CSV"""
    # Only owners can download reports
    current_user = User.query.get(session.get('user_id'))
    if not current_user or current_user.role != 'owner':
        return "Access denied. Only owners can download reports.", 403
    # Get date range from query params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return "Start date and end date are required", 400
    
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD", 400
    
    # Query bookings in date range
    bookings = Booking.query.filter(
        Booking.checkin >= start_dt,
        Booking.checkin <= end_dt
    ).order_by(Booking.checkin.desc()).all()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Room Number', 'Guest Name', 'Phone', 'ID Number', 'Check-in', 'Check-out', 'Booked By'])
    
    # Write data
    for booking in bookings:
        writer.writerow([
            booking.checkin.strftime('%d-%m-%Y'),
            booking.room.number,
            booking.guest_name,
            booking.guest_phone or '',
            booking.id_number or '',
            booking.checkin.strftime('%d-%m-%Y %H:%M'),
            booking.checkout.strftime('%d-%m-%Y %H:%M'),
            booking.booked_by or ''
        ])
    
    # Prepare response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=customer_report_{start_date}_to_{end_date}.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response


@app.route('/reports/download/financial')
@login_required
def download_financial_report():
    """Download financial report as CSV"""
    # Only owners can download reports
    current_user = User.query.get(session.get('user_id'))
    if not current_user or current_user.role != 'owner':
        return "Access denied. Only owners can download reports.", 403
    # Get date range from query params
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return "Start date and end date are required", 400
    
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD", 400
    
    # Query bookings in date range
    bookings = Booking.query.filter(
        Booking.checkin >= start_dt,
        Booking.checkin <= end_dt
    ).order_by(Booking.checkin.desc()).all()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Date', 'Receipt No.', 'Room Number', 'Guest Name', 'Payment Mode', 'Payment Type', 'Total Amount', 'Amount Received', 'Balance'])
    
    # Track totals
    total_amount_sum = 0
    total_received_sum = 0
    total_balance_sum = 0
    
    # Write data
    for booking in bookings:
        total_amt = booking.total_amount or 0
        received = booking.amount_received or 0
        balance = total_amt - received
        
        total_amount_sum += total_amt
        total_received_sum += received
        total_balance_sum += balance
        
        writer.writerow([
            booking.checkin.strftime('%d-%m-%Y'),
            booking.receipt_no or '',
            booking.room.number,
            booking.guest_name,
            booking.payment_mode or '',
            booking.payment_type or '',
            f'{total_amt:.2f}',
            f'{received:.2f}',
            f'{balance:.2f}'
        ])
    
    # Write totals row
    writer.writerow([])
    writer.writerow(['', '', '', '', '', 'TOTAL:', f'{total_amount_sum:.2f}', f'{total_received_sum:.2f}', f'{total_balance_sum:.2f}'])
    
    # Prepare response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=financial_report_{start_date}_to_{end_date}.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response


@app.route('/book', methods=['GET', 'POST'])
@login_required
def book_room():
    if request.method == 'POST':
        room_id = request.form['room_id']
        guest_name = request.form['guest_name'].strip()
        guest_phone = request.form.get('guest_phone', '').strip()
        
        # Input length validation
        length_error = (
            validate_length(guest_name, 100, 'Guest name') or
            validate_length(guest_phone, 20, 'Phone number') or
            validate_length(request.form.get('id_number', ''), 50, 'ID number') or
            validate_length(request.form.get('receipt_no', ''), 50, 'Receipt number') or
            validate_length(request.form.get('booked_by', ''), 100, 'Booked by')
        )
        if not guest_name:
            length_error = 'Guest name is required.'
        if length_error:
            rooms = Room.query.all()
            current_username = session.get('username', 'Unknown')
            return render_template('book.html', rooms=rooms, error=length_error, current_username=current_username)
        
        checkin = datetime.strptime(request.form['checkin'], '%Y-%m-%dT%H:%M')
        checkout = datetime.strptime(request.form['checkout'], '%Y-%m-%dT%H:%M')

        # Validate date logic
        if checkout <= checkin:
            rooms = Room.query.all()
            current_username = session.get('username', 'Unknown')
            return render_template('book.html', rooms=rooms, error='Check-out date must be after check-in date.', current_username=current_username)
        
        # Validate dates are not too far in the past (allow up to 24 hours for same-day corrections)
        if checkin < datetime.now() - timedelta(days=1):
            rooms = Room.query.all()
            current_username = session.get('username', 'Unknown')
            return render_template('book.html', rooms=rooms, error='Check-in date cannot be more than 1 day in the past.', current_username=current_username)
        
        # Validate minimum stay (at least 1 hour)
        stay_duration = (checkout - checkin).total_seconds() / 3600
        if stay_duration < 1:
            rooms = Room.query.all()
            current_username = session.get('username', 'Unknown')
            return render_template('book.html', rooms=rooms, error='Minimum booking duration is 1 hour.', current_username=current_username)

        # Check for conflicts
        conflict = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.checkin < checkout,
            Booking.checkout > checkin
        ).first()

        if conflict:
            rooms = Room.query.all()
            current_username = session.get('username', 'Unknown')
            return render_template('book.html', rooms=rooms, error='Room is already booked for this period.', current_username=current_username)

        # Check for blocks
        blocked = BlockedRoom.query.filter(
            BlockedRoom.room_id == room_id,
            BlockedRoom.start_date < checkout,
            BlockedRoom.end_date > checkin
        ).first()

        if blocked:
            rooms = Room.query.all()
            current_username = session.get('username', 'Unknown')
            error_msg = f'Room is blocked by {blocked.blocked_by} from {blocked.start_date.strftime("%d %b %H:%M")} to {blocked.end_date.strftime("%d %b %H:%M")}'
            if blocked.reason:
                error_msg += f': {blocked.reason}'
            return render_template('book.html', rooms=rooms, error=error_msg, current_username=current_username)

        booking = Booking(room_id=room_id, guest_name=guest_name,
                          guest_phone=guest_phone, checkin=checkin, checkout=checkout,
                          id_number=request.form.get('id_number', ''),
                          payment_mode=request.form.get('payment_mode', ''),
                          payment_type=request.form.get('payment_type', ''),
                          total_amount=float(request.form.get('total_amount', 0) or 0),
                          amount_received=float(request.form.get('amount_received', 0) or 0),
                          booked_by=request.form.get('booked_by', ''),
                          receipt_no=request.form.get('receipt_no', ''))
        db.session.add(booking)
        db.session.flush()  # Get booking.id before committing
        
        # Create initial payment transaction if amount received > 0
        amount_received = float(request.form.get('amount_received', 0) or 0)
        if amount_received > 0:
            payment = Payment(
                booking_id=booking.id,
                amount=amount_received,
                payment_mode=request.form.get('payment_mode', 'Cash'),
                receipt_no=request.form.get('receipt_no', ''),
                notes='Initial payment at booking'
            )
            db.session.add(payment)
        
        db.session.commit()
        return redirect(url_for('dashboard'))

    rooms = Room.query.all()
    current_username = session.get('username', 'Unknown')
    return render_template('book.html', rooms=rooms, error=None, current_username=current_username)


@app.route('/rooms', methods=['GET', 'POST'])
@login_required
def manage_rooms():
    # Get month/year filter from query params
    filter_month = request.args.get('month', type=int)
    filter_year = request.args.get('year', type=int)
    
    # Default to current month if not provided
    current_date = datetime.now()
    display_year = filter_year if filter_year else current_date.year
    display_month = filter_month if filter_month else current_date.month
    display_month_name = calendar.month_name[display_month]
    
    if request.method == 'POST':
        number = request.form['number'].strip()
        room_type = request.form['room_type'].strip()
        ac_type = request.form['ac_type'].strip()
        
        length_error = (
            validate_length(number, 10, 'Room number') or
            validate_length(room_type, 50, 'Room type') or
            validate_length(ac_type, 10, 'AC type')
        )
        if not number or not room_type:
            length_error = length_error or 'Room number and type are required.'
        if length_error:
            rooms = Room.query.order_by(Room.number).all()
            prices = {p.room_id: p for p in RoomPrice.query.filter_by(year=display_year, month=display_month).all()}
            room_prices = {}
            for room in rooms:
                price_obj = prices.get(room.id)
                room_prices[room.id] = {'price': price_obj.price_per_day if price_obj else room.price_per_day, 'is_custom': price_obj is not None, 'base_price': room.price_per_day}
            
            # Get available months for filter
            all_prices = RoomPrice.query.with_entities(RoomPrice.year, RoomPrice.month).distinct().all()
            available_months = sorted(set((p.year, p.month) for p in all_prices), reverse=True)
            if (current_date.year, current_date.month) not in available_months:
                available_months.insert(0, (current_date.year, current_date.month))
                available_months = sorted(available_months, reverse=True)
            
            return render_template('rooms.html', rooms=rooms, room_prices=room_prices, 
                                 current_month_name=display_month_name, current_year=display_year,
                                 available_months=available_months, selected_month=display_month,
                                 selected_year=display_year, error=length_error)
        
        price = float(request.form['price_per_day'])
        room = Room(number=number, room_type=room_type, ac_type=ac_type, price_per_day=price)
        db.session.add(room)
        db.session.commit()
        # Preserve filter when redirecting after adding room
        if filter_month and filter_year:
            return redirect(url_for('manage_rooms', month=filter_month, year=filter_year))
        return redirect(url_for('manage_rooms'))
    
    rooms = Room.query.order_by(Room.number).all()
    
    # Build a dictionary of selected month prices for each room
    prices = {p.room_id: p for p in RoomPrice.query.filter_by(year=display_year, month=display_month).all()}
    room_prices = {}
    for room in rooms:
        price_obj = prices.get(room.id)
        room_prices[room.id] = {
            'price': price_obj.price_per_day if price_obj else room.price_per_day,
            'is_custom': price_obj is not None,
            'base_price': room.price_per_day
        }
    
    # Get available months for filter dropdown (months with custom prices + current month)
    all_prices = RoomPrice.query.with_entities(RoomPrice.year, RoomPrice.month).distinct().all()
    available_months = sorted(set((p.year, p.month) for p in all_prices), reverse=True)
    # Always include current month
    if (current_date.year, current_date.month) not in available_months:
        available_months.insert(0, (current_date.year, current_date.month))
        available_months = sorted(available_months, reverse=True)
    
    return render_template('rooms.html', rooms=rooms, room_prices=room_prices, 
                         current_month_name=display_month_name, current_year=display_year,
                         available_months=available_months, selected_month=display_month,
                         selected_year=display_year)


@app.route('/rooms/delete/<int:room_id>', methods=['POST'])
@login_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    Booking.query.filter_by(room_id=room_id).delete()
    db.session.delete(room)
    db.session.commit()
    return redirect(url_for('manage_rooms'))


@app.route('/bookings')
@login_required
def list_bookings():
    page = request.args.get('page', 1, type=int)
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    per_page = 20
    
    # Base query
    query = Booking.query
    
    # Apply month/year filter if provided
    if month and year:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        query = query.filter(Booking.checkin >= start_date, Booking.checkin < end_date)
    
    # Get available months/years for filter dropdown
    all_bookings = Booking.query.with_entities(Booking.checkin).all()
    available_months = set()
    for b in all_bookings:
        if b.checkin:
            available_months.add((b.checkin.year, b.checkin.month))
    available_months = sorted(available_months, reverse=True)
    
    pagination = query.order_by(Booking.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('bookings.html', 
                         bookings=pagination.items, 
                         pagination=pagination,
                         available_months=available_months,
                         selected_month=month,
                         selected_year=year)


@app.route('/bookings/delete/<int:booking_id>', methods=['POST'])
@login_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    return redirect(url_for('list_bookings'))


@app.route('/bookings/update/<int:booking_id>', methods=['POST'])
@login_required
def update_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Input length validation
    length_error = (
        validate_length(request.form.get('receipt_no', ''), 50, 'Receipt number') or
        validate_length(request.form.get('notes', ''), 200, 'Notes')
    )
    if length_error:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': length_error}), 400
        return redirect(request.referrer or url_for('list_bookings'))
    
    # Add new payment transaction
    amount = float(request.form.get('amount', 0))
    if amount > 0:
        payment = Payment(
            booking_id=booking.id,
            amount=amount,
            payment_mode=request.form.get('payment_mode', 'Cash'),
            receipt_no=request.form.get('receipt_no', '').strip(),
            notes=request.form.get('notes', '').strip()
        )
        db.session.add(payment)
        
        # Update booking's total amount_received
        booking.amount_received = (booking.amount_received or 0) + amount
        # Update payment_mode to show last payment mode (for compatibility)
        booking.payment_mode = request.form.get('payment_mode', booking.payment_mode)
        if request.form.get('receipt_no'):
            booking.receipt_no = request.form.get('receipt_no')
        
        db.session.commit()
        
        # Calculate payment breakdown
        payments = Payment.query.filter_by(booking_id=booking.id).all()
        cash_total = sum(p.amount for p in payments if p.payment_mode == 'Cash')
        upi_total = sum(p.amount for p in payments if p.payment_mode == 'UPI')
        
        # Return JSON response for AJAX calls
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Payment added successfully',
                'booking': {
                    'id': booking.id,
                    'total_amount': booking.total_amount,
                    'amount_received': booking.amount_received,
                    'remaining': booking.total_amount - booking.amount_received,
                    'cash_total': cash_total,
                    'upi_total': upi_total
                },
                'payments': [{
                    'id': p.id,
                    'amount': p.amount,
                    'payment_mode': p.payment_mode,
                    'receipt_no': p.receipt_no or '',
                    'payment_date': p.payment_date.strftime('%d %b %Y, %H:%M'),
                    'notes': p.notes or ''
                } for p in payments]
            })
    
    return redirect(request.referrer or url_for('list_bookings'))


@app.route('/api/booking-payments/<int:booking_id>')
@login_required
def api_booking_payments(booking_id):
    """Get payment history for a booking."""
    payments = Payment.query.filter_by(booking_id=booking_id).order_by(Payment.payment_date.desc()).all()
    return jsonify([{
        'id': p.id,
        'amount': p.amount,
        'payment_mode': p.payment_mode,
        'receipt_no': p.receipt_no or '',
        'payment_date': p.payment_date.strftime('%d %b %Y, %H:%M'),
        'notes': p.notes or ''
    } for p in payments])


@app.route('/api/available-rooms')
@login_required
def api_available_rooms():
    """Return rooms with availability status for given date range."""
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')
    
    if not checkin or not checkout:
        rooms = Room.query.order_by(Room.number).all()
        return jsonify([{'id': r.id, 'number': r.number, 'type': r.room_type,
                         'ac': r.ac_type, 'price': r.price_per_day, 'available': True} for r in rooms])
    
    checkin_dt = datetime.strptime(checkin, '%Y-%m-%dT%H:%M')
    checkout_dt = datetime.strptime(checkout, '%Y-%m-%dT%H:%M')
    
    rooms = Room.query.order_by(Room.number).all()
    # Single query for all conflicts instead of per-room
    booked_room_ids = {b.room_id for b in Booking.query.filter(Booking.checkin < checkout_dt, Booking.checkout > checkin_dt).all()}
    blocked_room_ids = {bl.room_id for bl in BlockedRoom.query.filter(BlockedRoom.start_date < checkout_dt, BlockedRoom.end_date > checkin_dt).all()}
    
    # Batch fetch prices for checkin month
    checkin_year = checkin_dt.year
    checkin_month = checkin_dt.month
    prices = {p.room_id: p.price_per_day for p in RoomPrice.query.filter_by(year=checkin_year, month=checkin_month).all()}
    
    result = []
    for room in rooms:
        booked = room.id in booked_room_ids
        blocked = room.id in blocked_room_ids
        price = prices.get(room.id, room.price_per_day)
        
        # Get detailed block/booking info for debugging
        reason_detail = None
        if booked:
            conflict_booking = Booking.query.filter(
                Booking.room_id == room.id,
                Booking.checkin < checkout_dt,
                Booking.checkout > checkin_dt
            ).first()
            if conflict_booking:
                reason_detail = f"Booked until {conflict_booking.checkout.strftime('%d %b %H:%M')}"
        elif blocked:
            conflict_block = BlockedRoom.query.filter(
                BlockedRoom.room_id == room.id,
                BlockedRoom.start_date < checkout_dt,
                BlockedRoom.end_date > checkin_dt
            ).first()
            if conflict_block:
                reason_detail = f"Blocked from {conflict_block.start_date.strftime('%d %b %H:%M')}"
        
        result.append({'id': room.id, 'number': room.number, 'type': room.room_type,
                       'ac': room.ac_type, 'price': price, 'available': not booked and not blocked,
                       'reason': reason_detail or ('Booked' if booked else ('Blocked' if blocked else None))})
    return jsonify(result)


@app.route('/block', methods=['GET', 'POST'])
@login_required
def block_room():
    if request.method == 'POST':
        room_id = request.form['room_id']
        blocked_by = request.form['blocked_by'].strip()
        reason = request.form.get('reason', '').strip()
        
        length_error = (
            validate_length(blocked_by, 100, 'Blocked by') or
            validate_length(reason, 200, 'Reason')
        )
        if not blocked_by:
            length_error = length_error or 'Blocked by is required.'
        if length_error:
            rooms = Room.query.order_by(Room.number).all()
            blocks = BlockedRoom.query.order_by(BlockedRoom.start_date.desc()).all()
            current_username = session.get('username', 'Unknown')
            return render_template('block.html', rooms=rooms, blocks=blocks, current_username=current_username, error=length_error)
        
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%dT%H:%M')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%dT%H:%M')
        
        # Validate dates
        now = datetime.now()
        if start_date < now:
            rooms = Room.query.order_by(Room.number).all()
            blocks = BlockedRoom.query.order_by(BlockedRoom.start_date.desc()).all()
            current_username = session.get('username', 'Unknown')
            return render_template('block.html', rooms=rooms, blocks=blocks, current_username=current_username, 
                                 error='Start date cannot be in the past. Please select a current or future date.')
        
        if end_date <= start_date:
            rooms = Room.query.order_by(Room.number).all()
            blocks = BlockedRoom.query.order_by(BlockedRoom.start_date.desc()).all()
            current_username = session.get('username', 'Unknown')
            return render_template('block.html', rooms=rooms, blocks=blocks, current_username=current_username, 
                                 error='End date must be after start date.')
        
        user_id = session.get('user_id')
        block = BlockedRoom(room_id=room_id, user_id=user_id, blocked_by=blocked_by, reason=reason,
                            start_date=start_date, end_date=end_date)
        db.session.add(block)
        db.session.commit()
        return redirect(url_for('block_room'))
    rooms = Room.query.order_by(Room.number).all()
    blocks = BlockedRoom.query.order_by(BlockedRoom.start_date.desc()).all()
    current_username = session.get('username', 'Unknown')
    return render_template('block.html', rooms=rooms, blocks=blocks, current_username=current_username)


@app.route('/block/delete/<int:block_id>', methods=['POST'])
@login_required
def delete_block(block_id):
    block = BlockedRoom.query.get_or_404(block_id)
    db.session.delete(block)
    db.session.commit()
    return redirect(url_for('block_room'))


@app.route('/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    # Only owners can access this page
    current_user = User.query.get(session.get('user_id'))
    if not current_user or current_user.role != 'owner':
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        color = request.form.get('color', '#667eea').strip()
        role = request.form.get('role', 'contributor')
        
        length_error = validate_length(username, 50, 'Username')
        if not username:
            length_error = length_error or 'Username is required.'
        if not password or len(password) < 4:
            length_error = length_error or 'Password must be at least 4 characters.'
        if len(password) > 128:
            length_error = length_error or 'Password must be 128 characters or less.'
        # Validate color format
        if not color.startswith('#') or len(color) != 7:
            length_error = length_error or 'Invalid color format. Use hex color like #FF5733'
        # Validate role
        if role not in ['owner', 'contributor']:
            length_error = length_error or 'Invalid role selected'
        if length_error:
            users = User.query.all()
            return render_template('users.html', users=users, error=length_error)
        
        if User.query.filter_by(username=username).first():
            users = User.query.all()
            return render_template('users.html', users=users, error='Username already exists')
        user = User(username=username, color=color, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('manage_users'))
    users = User.query.all()
    return render_template('users.html', users=users, error=None)


@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    # Only owners can edit users
    current_user = User.query.get(session.get('user_id'))
    if not current_user or current_user.role != 'owner':
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form.get('password', '').strip()
        color = request.form.get('color', user.color).strip()
        role = request.form.get('role', user.role)
        
        length_error = validate_length(username, 50, 'Username')
        if not username:
            length_error = length_error or 'Username is required.'
        # Only validate password if provided (optional for edit)
        if password:
            if len(password) < 4:
                length_error = length_error or 'Password must be at least 4 characters.'
            if len(password) > 128:
                length_error = length_error or 'Password must be 128 characters or less.'
        # Validate color format
        if not color.startswith('#') or len(color) != 7:
            length_error = length_error or 'Invalid color format. Use hex color like #FF5733'
        # Validate role
        if role not in ['owner', 'contributor']:
            length_error = length_error or 'Invalid role selected'
        if length_error:
            users = User.query.all()
            return render_template('users.html', users=users, error=length_error, edit_user=user)
        
        # Check if username is taken by another user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            users = User.query.all()
            return render_template('users.html', users=users, error='Username already exists', edit_user=user)
        
        # Update user
        user.username = username
        user.color = color
        user.role = role
        if password:  # Only update password if provided
            user.set_password(password)
        
        db.session.commit()
        
        # Update session if editing current user
        if user_id == session.get('user_id'):
            session['username'] = user.username
            session['user_role'] = user.role
        
        return redirect(url_for('manage_users'))
    
    # GET request - show edit form
    users = User.query.all()
    return render_template('users.html', users=users, error=None, edit_user=user)


@app.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    # Only owners can delete users
    current_user = User.query.get(session.get('user_id'))
    if not current_user or current_user.role != 'owner':
        return redirect(url_for('dashboard'))
    
    if user_id == session.get('user_id'):
        return redirect(url_for('manage_users'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('manage_users'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin user (only on first run)
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', color='#667eea', role='owner')  # Purple, Owner
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Database initialized with admin user")
        else:
            print("✅ Database initialized")
    app.run(debug=True, port=5001)
