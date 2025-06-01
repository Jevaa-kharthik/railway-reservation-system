from flask import Flask, request, redirect, flash, session, render_template
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from models.models import db, User, Train, Booking
from utils.auth import login_required
from datetime import date, datetime
from sqlalchemy import text
import os
from flask import Flask


app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates'))
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
            flash('Logged in successfully!', 'success')
            return redirect('/dashboard')

        flash('Invalid username or password.', 'danger')
        return redirect('/login')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect('/')

@app.route('/trainlist')
@login_required
def train_list():
    try:
        trains = Train.query.all()
    except Exception as e:
        # Log or print error
        print(f"Error fetching trains: {e}")
        flash("Could not load trains, please try again later.", "danger")
        trains = []
    return render_template('trainlist.html', trains=trains)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/book/<int:train_id>', methods=['GET', 'POST'])
@login_required
def book(train_id):
    train = Train.query.get_or_404(train_id)
    if request.method == 'POST':
        if train.seats_available > 0:
            train.seats_available -= 1
            booking = Booking(user_id=session['user_id'], train_id=train_id, booking_date=date.today())
            db.session.add(booking)
            db.session.commit()
            return render_template('booking_success.html', train=train)
        flash('No seats available for this train.', 'warning')
        return redirect(f'/book/{train_id}')
    return render_template('book_ticket.html', train=train)

@app.route('/mybookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    return render_template('view_bookings.html', bookings=bookings)

@app.route('/test-db')
def test_db():
    try:
        db.session.execute(text('SELECT 1'))
        return '✅ Database connection is successful!'
    except Exception as e:
        return f'❌ Database connection failed: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True, port=5002)