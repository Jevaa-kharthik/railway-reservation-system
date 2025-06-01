from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Time

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Train(db.Model):
    __tablename__ = 'trains' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    source = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    departure_time = db.Column(db.Time, nullable=False)
    seats_available = db.Column(db.Integer)

class Booking(db.Model):
    __tablename__ = 'bookings'  # <-- Fix table name
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey('trains.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    
class Passenger(db.Model):
    __tablename__ = 'passengers'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    booking = db.relationship('Booking', backref=db.backref('passengers', lazy=True))