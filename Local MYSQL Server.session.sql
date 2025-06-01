
create DATABASE train_booking_system;
USE train_booking_system;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(512) NOT NULL
);


-- Create trains table
CREATE TABLE IF NOT EXISTS trains (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    seats_available INT NOT NULL,
    depature_time TIME NOT NULL
);

-- Create bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    train_id INT NOT NULL,
    booking_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (train_id) REFERENCES trains(id)
);

CREATE TABLE IF NOT EXISTS passengers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);

INSERT INTO trains (name, source, destination, seats_available, departure_time)
VALUES
('Chennai Express', 'Chennai', 'Mumbai', 120, '06:00:00'),
('Bangalore Superfast', 'Bangalore', 'Delhi', 80, '07:30:00'),
('Kolkata Duronto', 'Kolkata', 'Pune', 150, '08:00:00'),
('Hyderabad Mail', 'Hyderabad', 'Chennai', 200, '14:00:00'),
('Goa Special', 'Goa', 'Mangalore', 90, '09:00:00'),
('Mumbai Rajdhani', 'Mumbai', 'Delhi', 110, '17:00:00'),
('Pune Intercity', 'Pune', 'Nagpur', 130, '05:45:00'),
('Delhi Shatabdi', 'Delhi', 'Amritsar', 75, '06:30:00'),
('Chandigarh Express', 'Chandigarh', 'Jaipur', 100, '10:15:00'),
('Kerala Express', 'Trivandrum', 'Hyderabad', 95, '19:30:00');

select * from trains;

