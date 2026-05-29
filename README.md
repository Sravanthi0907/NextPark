# DriveLock Pro - Parking Stand Access Management System

A Flask-based web application for managing parking stand reservations with dynamic QR code access control and real-time synchronization across all users.

## Overview

DriveLock Pro is an intelligent parking management system that allows users to book parking stands and control access through personal QR codes. The system features:

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

## API Endpoints

### Authentication
- `POST /register` - Create new account
- `POST /login` - User login
- `POST /logout` - User logout

### Booking Management
- `POST /save_booking` - Create new booking
- `GET /booking` - Booking page
- `POST /cancel_booking` - Cancel booking
- `POST /update_payment_status` - Update payment

### QR Access Control
- `POST /verify_qr_access` - Process QR scan and toggle stand status
- `GET /get_status` - Get current stand statuses
- `GET /api/qr/download` - Download user QR code

### History & Information
- `GET /get_history` - Get user booking history
- `GET /get_qr_history` - Get QR scan history
- `POST /api/calculate_fee` - Calculate booking fees

## QR Code Access System

### How It Works

1. **User scans their QR code** during active booking
2. **System increments scan count** for that booking
3. **Stand status toggles** based on scan count:
   - Odd scans (1, 3, 5...) → "Open"
   - Even scans (2, 4, 6...) → "Closed"
4. **Status updates globally** for all users
5. **Access expires** automatically when booking ends

### Example Flow
```
Booking Period: 10:00 AM - 2:00 PM

10:15 AM - User scans QR (Scan #1 - Odd) → Stand "Open"
10:30 AM - User scans QR (Scan #2 - Even) → Stand "Closed"
10:45 AM - User scans QR (Scan #3 - Odd) → Stand "Open"
2:00 PM - Booking expires → Stand auto-resets to "available"
```

## Pricing

Vehicle rates (per hour):
- **Bike**: ₹20/hour
- **EV**: ₹40/hour
- **Car**: ₹50/hour
- **Truck**: ₹80/hour
- **Bus**: ₹100/hour

Pricing is calculated based on booking duration (rounded up to nearest hour).

## User Guide

### 1. Registration
- Navigate to Register page
- Enter username, email, vehicle registration number
- Create a strong password
- Your unique QR code will be generated automatically

### 2. Booking a Stand
- Go to "Book a Stand" page
- Select parking date
- Choose vehicle type and duration
- Select available parking stand
- Review calculated fee
- Complete payment (simulated)
- Stand is now reserved

### 3. Accessing Your Stand
- Go to booking history
- Click "Scan QR" for active booking
- Allow camera access when prompted
- QR scanner will read your personal code
- Stand status will toggle based on scan count

### 4. Viewing History
- **Booking History**: All reservations and their status
- **QR History**: All access attempts with timestamps

### 5. Profile Management
- View account details
- Download QR code for offline use
- Manage vehicle information

## CSS Improvements

The styling has been enhanced with:

- **Better Alignment**: Flexbox/Grid-based layouts for proper centering
- **Improved Responsiveness**: Mobile-first design approach
- **Enhanced Visual Hierarchy**: Clear spacing and typography
- **Accessibility**: Proper contrast ratios and readable fonts
- **Interactive Elements**: Smooth transitions and hover effects
- **Responsive Grids**: Stand grid adapts to different screen sizes
- **Modal Improvements**: Better centered modals with overflow handling

## Configuration

### Environment Variables
```bash
SECRET_KEY=your-secret-key  # Flask session secret
```

### File Storage
- All data is stored as JSON files in the project directory
- No external database required
- QR codes stored in `/users` directory

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- QR token verification
- Booking ownership verification
- Time-based access expiration
- CSRF protection via session tokens

## Troubleshooting

### QR Code Not Working
- Ensure camera permissions are granted
- Check lighting conditions
- Make sure QR code is clearly visible
- Try clearing browser cache

### Booking Issues
- Verify sufficient payment balance
- Check booking start time hasn't passed
- Ensure selected stand is available
- Confirm booking duration is valid

### Access Denied
- Verify using your personal QR code
- Check if booking is still active
- Ensure payment status is "Successful"
- Confirm current time is within booking window

## Performance Notes

- JSON-based storage suitable for up to ~1000 bookings
- Real-time synchronization across all users
- Minimal database queries due to file-based storage
- Efficient scan count tracking

## Future Enhancements

- Database migration (PostgreSQL/MySQL)
- Advanced analytics dashboard
- Recurring bookings
- Multi-vehicle support per user
- SMS/Email notifications
- Mobile app integration
- Payment gateway integration (Razorpay, Stripe)
- Reserved spots for regular users
- Dynamic pricing based on demand

## Support & Contribution

For issues or feature requests, please contact the development team or create an issue in the project repository.

## License

This project is proprietary software. All rights reserved.

## Deployment on Render

DriveLock Pro is configured for easy deployment on [Render](https://render.com), a modern cloud platform.

### Quick Deploy to Render

1. **Push your code to GitHub**
   - Create a GitHub repository
   - Commit and push all project files
   - Ensure `.gitignore` is in place

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository and branch

3. **Configure Service**
   - **Name**: `drivelock-pro` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --workers 4 --bind 0.0.0.0:$PORT app:app`
   - **Plan**: Free (or paid for production)

4. **Set Environment Variables**
   In the "Environment" section, add:
   ```
   FLASK_ENV=production
   SECRET_KEY=<generate-a-strong-random-key>
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy your application
   - Your app will be live at `https://<your-service-name>.onrender.com`

### Key Deployment Files

- **Procfile**: Specifies how to run the application on Render
- **runtime.txt**: Specifies Python version (3.11.9)
- **requirements.txt**: All Python dependencies
- **render.yaml**: Optional Render infrastructure configuration
- **.gitignore**: Excludes unnecessary files from deployment

### Important Notes for Production

1. **Data Persistence**: 
   - JSON files are stored on the container's ephemeral storage
   - Files persist during the service lifecycle but are lost on redeploy
   - For persistent data, consider migrating to a database:
     - Render PostgreSQL: Free tier available
     - Recommended: Migrate to PostgreSQL for production use

2. **Security**:
   - Always set a strong `SECRET_KEY` in environment variables
   - Enable HTTPS (automatic with Render)
   - Use environment variables for sensitive data

3. **Performance**:
   - Free tier has 0.5 GB RAM and 2 CPU (spins down after 15 mins inactivity)
   - Paid tier recommended for always-on service
   - Current configuration uses 4 Gunicorn workers (adjustable)

4. **Monitoring**:
   - Check Render dashboard for logs
   - Monitor for errors and performance issues
   - Set up email notifications for deployments

### Upgrading from Free Tier

When ready to go production:
1. Upgrade to a paid instance
2. Migrate JSON data to PostgreSQL
3. Set up proper database backups
4. Configure CDN for static files
5. Enable advanced monitoring

### Troubleshooting Render Deployment

- **Deployment fails**: Check build logs in Render dashboard
- **App crashes after deploy**: Review runtime logs
- **Data lost after redeploy**: Migrate to persistent database
- **Performance issues**: Upgrade to paid tier or optimize code

## Version History

### v1.2 - Production Ready
- Added booking conflict validation
- Enhanced activity logs with real-time stand status
- Automatic booking expiration cleanup
- Render deployment configuration
- Production-ready environment handling

### v1.1 - Enhanced Features
- Dynamic QR access control with odd/even toggling
- Global synchronization improvements
- Activity log enhancements

### v1.0 - Initial Release
- Dynamic QR access control with odd/even toggling
- Global synchronization of reservation slots
- Enhanced CSS with improved alignment
- Complete user and booking management
- Real-time history tracking
- Comprehensive documentation
