# Railway Reservation System

## Overview
The Railway Reservation System is a web application built using Flask that allows users to register, log in, and book train tickets. The application provides a user-friendly interface for managing train bookings and viewing booking history.

## Project Structure
```
railway-reservation-system
├── app.py
├── config.py
├── requirements.txt
├── models
│   └── models.py
├── utils
│   └── auth.py
├── templates
│   ├── base.html
│   ├── home.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── book_ticket.html
│   ├── booking_success.html
│   └── view_bookings.html
└── README.md
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd railway-reservation-system
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the database:
   - Ensure you have a MySQL server running.
   - Create a database named `railway_reservation_system`.

## Configuration
- Update the database connection string in `app.py` with your MySQL credentials.

## Usage
1. Run the application:
   ```
   python app.py
   ```

2. Open your web browser and go to `http://127.0.0.1:5000`.

## Features
- User registration and login
- View available trains
- Book tickets for trains
- View booking history

## License
This project is licensed under the MIT License.