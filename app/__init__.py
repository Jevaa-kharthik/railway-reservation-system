from flask import Flask, request, redirect, flash, session, render_template, url_for, abort
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from models.models import db, User, Train, Booking, Passenger
from utils.auth import login_required
from datetime import date, time
from sqlalchemy import text
import os
from app import db
from flask_mail import Mail, Message
import re
# from .models import Train  # Removed duplicate and problematic import

bcrypt = None  # will be set after app is created
mail = Mail()

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'))

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail.init_app(app)
bcrypt = Bcrypt(app)

# Configuration
app.secret_key = 'nothingbut123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://jevaakharthik:jevaa%40iitm@localhost/train_booking_system?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB and Migrate
db.init_app(app)
migrate = Migrate(app, db)

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect('/register')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['username'] = user.username
        flash('Login successful!', 'success')

        trains = Train.query.order_by(Train.departure_time).all()
        upcoming_bookings = Booking.query.filter_by(user_id=user.id).all()

        return render_template('dashboard.html', username=user.username, trains=trains, upcoming_bookings=upcoming_bookings)

    flash('Invalid username or password.', 'danger')
    return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    username = user.username if user else 'Guest'
    trains = Train.query.order_by(Train.departure_time).all()
    upcoming_bookings = Booking.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', username=username, trains=trains, upcoming_bookings=upcoming_bookings)

@app.route('/train_list')
def train_list():
    # your logic here (fetching train data, rendering template, etc.)
    return render_template('train_list.html', trains=Train.query.all())

@app.route('/booking_success/<int:train_id>')
@login_required
def booking_success(train_id):
    train = Train.query.get_or_404(train_id)
    return render_template('booking_success.html', train=train, booking_date=date.today())

@app.route('/book/<int:train_id>', methods=['GET', 'POST'])
@login_required
def book(train_id):
    train = Train.query.get_or_404(train_id)

    if request.method == 'POST':
        seats = int(request.form['seats'])
        passenger_names = request.form.getlist('passenger_names')

        if not passenger_names or len(passenger_names) < 1:
            return "At least one passenger name is required.", 400

        if seats > train.seats_available:
            flash('Not enough seats available.', 'danger')
            return redirect(url_for('book', train_id=train_id))

        new_booking = Booking(
            user_id=session['user_id'],
            train_id=train_id,
            booking_date=date.today()
        )
        db.session.add(new_booking)
        db.session.flush()  # This assigns an id to new_booking without committing

        for pname in passenger_names:
            passenger = Passenger(
                booking_id=new_booking.id,
                name=pname
            )
            db.session.add(passenger)

        # Update seats available on the train
        train.seats_available -= seats

        db.session.commit()  # Commit all changes

        return redirect(url_for('booking_success', train_id=train_id))

    return render_template('book_ticket.html', train=train)

@app.route('/mybookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    return render_template('view_bookings.html', bookings=bookings)

@app.route('/add_train', methods=['GET', 'POST'])
def add_train():
    if request.method == 'POST':
        # Extract data from form
        name = request.form['name']
        source = request.form['source']
        destination = request.form['destination']
        seats = int(request.form['seats'])
        departure_time_str = request.form['departure_time']  # 'HH:MM' string

        # Convert string to time object
        hour, minute = map(int, departure_time_str.split(':'))
        departure_time = time(hour, minute)

        # Create new train object
        new_train = Train(
            name=name,
            source=source,
            destination=destination,
            seats_available=seats,
            departure_time=departure_time
        )

        # Add and commit to DB
        db.session.add(new_train)
        db.session.commit()

        # Redirect back to dashboard or train list page
        return redirect(url_for('dashboard'))

    # GET request - show form
    return render_template('add_train.html')

@app.route('/test-db')
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        return '✅ Database connection is successful!'
    except Exception as e:
        return f'❌ Database connection failed: {str(e)}'
    
@app.route('/booking_history')
@login_required
def booking_history():
    user_id = session['user_id']
    
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()

    booking_details = []
    for booking in bookings:
        passengers = Passenger.query.filter_by(booking_id=booking.id).all()
        train = Train.query.get(booking.train_id)
        
        # Join passenger names into a comma-separated string
        passenger_names = ", ".join([p.name for p in passengers])
        
        booking_details.append({
            'booking': booking,
            'train': train,
            'passenger_names': passenger_names
        })

    return render_template('booking_history.html', booking_details=booking_details)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Email format validation
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('contact'))

        msg = Message(
            subject=f"New Contact Form Submission from {name}",
            sender=app.config['MAIL_USERNAME'],
            recipients=['your_admin_email@example.com'],
            body=f"Name: {name}\nEmail: {email}\nMessage:\n{message}"
        )
        mail.send(msg)

        flash("Thank you for contacting us! We'll get back to you soon.", "success")
        return render_template('contact.html', success=True)

    return render_template('contact.html')

@app.route('/cancel')
@login_required
def cancel_ticket():
    user_id = session['user_id']
    bookings = Booking.query.filter_by(user_id=user_id).all()
    return render_template('cancel_ticket.html', bookings=bookings)

@app.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_specific_ticket(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != session['user_id']:
        abort(403)

    db.session.delete(booking)  # This will also delete passengers due to cascade
    db.session.commit()
    flash("Booking canceled successfully.", "success")
    return render_template('cancel_ticket.html', bookings=Booking.query.filter_by(user_id=session['user_id']).all())

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Check if username is already taken by other users
        if User.query.filter(User.username == username, User.id != user.id).first():
            flash('Username already taken. Please choose another.', 'danger')
            return redirect(url_for('update_profile'))

        user.username = username
        user.email = email if email else None

        if password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user.password = hashed_password

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        # Render the same page with updated user info and flash message
        return render_template('update_profile.html', user=user)

    return render_template('update_profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True, port=8080)