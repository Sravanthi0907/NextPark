# NextPark - Parking Stand Access Management System

A Flask-based web application for managing parking stand reservations with dynamic QR code access control and real-time synchronization across all users.

## Overview

NextPark is an intelligent parking management system that allows users to book parking stands and control access through personal QR codes. The system features:

- **Personal QR Code Access**: Each user has a unique QR code for stand access
- **Dynamic Open/Close Toggle**: QR scans toggle stand status (odd scans = open, even scans = closed)
- **Real-Time Synchronization**: All users see reservation updates instantly
- **Booking Management**: Easy booking, payment tracking, and cancellation
- **QR Scan History**: Complete audit trail of all access attempts
- **Time-Based Access**: Automatic access expiration after booking ends

## Features

### 1. User Management
- User registration with email and vehicle registration
- Secure login/logout functionality
- Personal QR code generation
- Profile management and QR code download

### 2. Parking Stand Booking
- Real-time availability view for all 10 parking stands
- Dynamic pricing based on vehicle type and duration
- Multiple vehicle types: Bike, EV, Car, Truck, Bus
- Hourly rate calculation
- Payment status tracking

### 3. Dynamic QR Access Control
- **Scan Count Tracking**: System tracks total QR scans per booking
- **Odd/Even Pattern**:
  - 1st scan (odd) → Stand opens
  - 2nd scan (even) → Stand closes
  - 3rd scan (odd) → Stand opens
  - Pattern continues for unlimited scans

### 4. Global Synchronization
- Stand status synchronized globally across all user accounts
- Real-time reservation updates visible to all users
- Automatic availability after booking ends
- Consistent parking experience for all users

### 5. Access History & Audit Trail
- QR scan history with timestamps
- Booking history with payment details
- Access status tracking (pending, granted, expired)
- Complete audit log for compliance

## Tech Stack

- **Backend**: Flask (Python 3.x)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: JSON-based file storage
- **QR Code**: cv2, qrcode libraries
- **Authentication**: Flask Sessions with password hashing

## Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Setup Instructions

1. **Clone or download the project**
```bash
cd project
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Access the application**
Open your browser and navigate to: `http://localhost:5000`

## Project Structure

```
project/
├── app.py                    # Main Flask application
├── data_handlers.py          # Data handling and business logic
├── requirements.txt          # Python dependencies
├── runtime.txt              # Runtime configuration
├── static/
│   └── css/
│       └── main.css         # Enhanced responsive styling
├── templates/               # HTML templates
│   ├── layout.html         # Base layout template
│   ├── home.html           # Home page
│   ├── booking.html        # Booking page
│   ├── history.html        # Booking history
│   ├── profile.html        # User profile
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   └── _*.html             # Partial templates
├── users/                  # User QR code storage
├── bookings.json           # Booking records
├── users.json              # User accounts
├── stands.json             # Parking stand status
├── data.json               # General application data
├── history.json            # Access history
└── qr_history.json         # QR scan history
```

## Configuration

### Environment Variables
```bash
SECRET_KEY=your-secret-key  # Flask session secret
```

### File Storage
- All data is stored as JSON files in the project directory
- No external database required
- QR codes stored in `/users` directory

## License

This project is proprietary software. All rights reserved.
