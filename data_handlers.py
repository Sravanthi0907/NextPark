import json
import re
import uuid
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash


VEHICLE_RATES_PER_HOUR = {
    "Bike": 20,
    "EV": 40,
    "Car": 50,
    "Truck": 80,
    "Bus": 100,
}


class DataHandler:
    def __init__(self):
        self.bookings_file = 'bookings.json'
        self.users_file = 'users.json'
        self.stands_file = 'stands.json'
        self.users_qr_dir = 'users'
        self.initialize_files()

    def initialize_files(self):
        for file_name in [self.bookings_file, self.users_file, self.stands_file]:
            if not os.path.exists(file_name):
                with open(file_name, 'w') as f:
                    if file_name == self.bookings_file:
                        json.dump({"bookings": []}, f)
                    elif file_name == self.users_file:
                        json.dump({"users": []}, f)
                    else:
                        json.dump({
                            "stands": [
                                {"id": i, "status": "available", "current_booking_id": None}
                                for i in range(1, 11)
                            ]
                        }, f)

        os.makedirs(self.users_qr_dir, exist_ok=True)

    def read_json_file(self, file_name):
        with open(file_name, 'r') as f:
            return json.load(f)

    def write_json_file(self, file_name, data):
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def normalize_vehicle_reg(reg):
        return re.sub(r'\s+', '', reg.strip().upper())

    @staticmethod
    def safe_filename(value):
        return re.sub(r'[^\w\-]', '_', value)

    def generate_unique_qr_token(self):
        return f"DL-{uuid.uuid4().hex[:12].upper()}"

    def generate_qr_image(self, qr_token):
        import qrcode
        safe = self.safe_filename(qr_token)
        path = os.path.join(self.users_qr_dir, f"{safe}.jpg")
        img = qrcode.make(qr_token)
        img.convert("RGB").save(path, "JPEG", quality=95)
        return path.replace('\\', '/')

    @staticmethod
    def combine_date_time(booking_date, time_value):
        return datetime.fromisoformat(f"{booking_date}T{time_value}")

    @staticmethod
    def normalize_vehicle_type(vehicle_type):
        key = vehicle_type.strip().lower()
        for name in VEHICLE_RATES_PER_HOUR:
            if name.lower() == key:
                return name
        return None

    @staticmethod
    def calculate_fee(vehicle_type, start_iso, end_iso):
        vehicle_type = DataHandler.normalize_vehicle_type(vehicle_type)
        if not vehicle_type:
            return None, f"Unknown vehicle type. Choose from: {', '.join(VEHICLE_RATES_PER_HOUR)}"

        start = datetime.fromisoformat(start_iso)
        end = datetime.fromisoformat(end_iso)
        if end <= start:
            return None, "End time must be after start time."

        hours = max(1, int((end - start).total_seconds() + 3599) // 3600)
        rate = VEHICLE_RATES_PER_HOUR[vehicle_type]
        amount = hours * rate
        return {
            "amount": amount,
            "hours": hours,
            "ratePerHour": rate,
            "vehicleType": vehicle_type
        }, None

    def get_user_bookings(self, user_id):
        data = self.read_json_file(self.bookings_file)
        return [booking for booking in data['bookings'] if booking['userId'] == user_id]

    def get_user_by_id(self, user_id):
        data = self.read_json_file(self.users_file)
        for user in data['users']:
            if user['id'] == user_id:
                return user
        return None

    def get_user_by_username(self, username):
        data = self.read_json_file(self.users_file)
        username_lower = username.lower()
        for user in data['users']:
            if user.get('username', '').lower() == username_lower:
                return user
        return None

    def get_user_by_email(self, email):
        data = self.read_json_file(self.users_file)
        email_lower = email.lower()
        for user in data['users']:
            if user.get('email', '').lower() == email_lower:
                return user
        return None

    def get_user_by_login(self, login_id):
        login_id = login_id.strip()
        user = self.get_user_by_username(login_id)
        if user:
            return user
        return self.get_user_by_email(login_id)

    def get_user_identifiers(self, user):
        if not user:
            return set()
        identifiers = {user['id']}
        if user.get('qrToken'):
            identifiers.add(user['qrToken'])
        return identifiers

    def create_user(self, username, email, vehicle_reg, password):
        username = username.strip()
        email = email.strip().lower()
        vehicle_reg = self.normalize_vehicle_reg(vehicle_reg)

        if self.get_user_by_username(username):
            return None, 'Username already taken.'
        if self.get_user_by_email(email):
            return None, 'Email already registered.'

        for user in self.read_json_file(self.users_file)['users']:
            if self.normalize_vehicle_reg(user.get('vehicleReg', '')) == vehicle_reg:
                return None, 'Vehicle registration already linked to an account.'

        user_id = f"user_{uuid.uuid4().hex[:10]}"
        qr_token = self.generate_unique_qr_token()
        qr_image_path = self.generate_qr_image(qr_token)
        new_user = {
            "id": user_id,
            "username": username,
            "email": email,
            "vehicleReg": vehicle_reg,
            "qrToken": qr_token,
            "passwordHash": generate_password_hash(password),
            "qrImagePath": qr_image_path.replace('\\', '/'),
            "active_bookings": []
        }

        data = self.read_json_file(self.users_file)
        data['users'].append(new_user)
        self.write_json_file(self.users_file, data)
        return new_user, None

    def authenticate_user(self, login_id, password):
        user = self.get_user_by_login(login_id)
        if not user:
            return None
        if check_password_hash(user['passwordHash'], password):
            return user
        return None

    def booking_is_active(self, booking):
        now = datetime.now()
        start = datetime.fromisoformat(booking['startTime'])
        end = datetime.fromisoformat(booking['endTime'])
        return start <= now <= end

    def booking_has_started(self, booking):
        return datetime.now() >= datetime.fromisoformat(booking['startTime'])

    def user_can_access_booking(self, user_id, booking_id):
        booking = self.get_booking_by_id(booking_id)
        if not booking or booking['userId'] != user_id:
            return False, None
        if booking.get('paymentStatus') != 'Successful':
            return False, booking
        if not self.booking_has_started(booking):
            return False, booking
        if not self.booking_is_active(booking):
            return False, booking
        return True, booking

    def check_stand_availability(self, stand_number, start_iso, end_iso):
        """Check if a stand is available during the requested time period.
        Returns (is_available, conflicting_booking) tuple."""
        stand_number = int(stand_number)
        data = self.read_json_file(self.bookings_file)
        
        start = datetime.fromisoformat(start_iso)
        end = datetime.fromisoformat(end_iso)
        
        for booking in data['bookings']:
            # Only check active or future bookings (exclude cancelled bookings)
            if booking.get('paymentStatus') == 'Cancelled':
                continue
            
            if booking['standNumber'] == stand_number:
                booking_start = datetime.fromisoformat(booking['startTime'])
                booking_end = datetime.fromisoformat(booking['endTime'])
                
                # Check for time overlap
                if not (end <= booking_start or start >= booking_end):
                    return False, booking
        
        return True, None

    def create_booking(self, booking_data):
        data = self.read_json_file(self.bookings_file)
        booking_id = int(datetime.now().timestamp() * 1000)

        new_booking = {
            "id": booking_id,
            "standNumber": int(booking_data['standNumber']),
            "bookingDate": booking_data.get('bookingDate'),
            "startTime": booking_data['startTime'],
            "endTime": booking_data['endTime'],
            "vehicleType": booking_data.get('vehicleType', 'Car'),
            "amountPaid": booking_data.get('amountPaid', 0),
            "paymentStatus": booking_data.get('paymentStatus', 'Pending'),
            "accessStatus": booking_data.get('accessStatus', 'pending'),
            "userId": booking_data['userId'],
            "qrScanCount": 0,
            "standStatus": "closed"
        }

        data['bookings'].append(new_booking)
        self.write_json_file(self.bookings_file, data)

        self.update_stand_status(new_booking['standNumber'], "reserved", booking_id)
        self.update_user_bookings(booking_data['userId'], booking_id)

        return new_booking

    def mark_booking_access_granted(self, booking_id):
        data = self.read_json_file(self.bookings_file)
        for booking in data['bookings']:
            if booking['id'] == booking_id:
                booking['accessStatus'] = 'granted'
                break
        self.write_json_file(self.bookings_file, data)

    def update_stand_status(self, stand_number, status, booking_id=None):
        stand_number = int(stand_number)
        data = self.read_json_file(self.stands_file)
        for stand in data['stands']:
            if stand['id'] == stand_number:
                stand['status'] = status
                stand['current_booking_id'] = booking_id
                break
        self.write_json_file(self.stands_file, data)

    def update_user_bookings(self, user_id, booking_id):
        data = self.read_json_file(self.users_file)
        for user in data['users']:
            if user['id'] == user_id:
                if 'active_bookings' not in user:
                    user['active_bookings'] = []
                user['active_bookings'].append(booking_id)
                break
        self.write_json_file(self.users_file, data)

    def update_payment_status(self, booking_id, status, amount_paid=None):
        data = self.read_json_file(self.bookings_file)
        for booking in data['bookings']:
            if booking['id'] == booking_id:
                booking['paymentStatus'] = status
                if amount_paid is not None:
                    booking['amountPaid'] = amount_paid
                break
        self.write_json_file(self.bookings_file, data)

    def cancel_booking(self, booking_id):
        data = self.read_json_file(self.bookings_file)
        booking = None
        for b in data['bookings']:
            if b['id'] == booking_id:
                booking = b
                data['bookings'].remove(b)
                break

        if booking:
            self.update_stand_status(booking['standNumber'], "available", None)

            user_data = self.read_json_file(self.users_file)
            for user in user_data['users']:
                if user['id'] == booking['userId']:
                    if booking_id in user.get('active_bookings', []):
                        user['active_bookings'].remove(booking_id)
                    break
            self.write_json_file(self.users_file, user_data)

        self.write_json_file(self.bookings_file, data)

    def get_booking_by_id(self, booking_id):
        data = self.read_json_file(self.bookings_file)
        for booking in data['bookings']:
            if booking['id'] == booking_id:
                return booking
        return None

    def booking_belongs_to_user(self, booking_id, user_id):
        booking = self.get_booking_by_id(booking_id)
        return booking is not None and booking['userId'] == user_id

    def increment_qr_scan_count(self, booking_id):
        """Increment QR scan count and return the new count and stand status"""
        data = self.read_json_file(self.bookings_file)
        for booking in data['bookings']:
            if booking['id'] == booking_id:
                booking['qrScanCount'] = booking.get('qrScanCount', 0) + 1
                new_count = booking['qrScanCount']
                
                # Odd scans = Open, Even scans = Closed
                stand_status = "Open" if new_count % 2 == 1 else "Closed"
                booking['standStatus'] = stand_status
                
                self.write_json_file(self.bookings_file, data)
                return new_count, stand_status
        
        return 0, "Closed"

    def get_booking_scan_count(self, booking_id):
        """Get current scan count for a booking"""
        booking = self.get_booking_by_id(booking_id)
        if booking:
            return booking.get('qrScanCount', 0)
        return 0

    def cleanup_expired_bookings(self):
        """Mark stands as available when bookings expire."""
        now = datetime.now()
        data = self.read_json_file(self.bookings_file)
        stands_data = self.read_json_file(self.stands_file)
        updated_stands = False
        
        for booking in data['bookings']:
            # Skip cancelled or already-expired bookings
            if booking.get('paymentStatus') == 'Cancelled':
                continue
            
            end_time = datetime.fromisoformat(booking['endTime'])
            
            # Mark as expired if end time has passed
            if now > end_time and booking.get('paymentStatus') != 'Expired':
                booking['paymentStatus'] = 'Expired'
                updated_stands = True
        
        if updated_stands:
            self.write_json_file(self.bookings_file, data)
        
        # Update stands that have no active bookings
        for stand in stands_data.get('stands', []):
            stand_id = stand['id']
            has_active_booking = False
            
            for booking in data['bookings']:
                if booking.get('paymentStatus') == 'Cancelled' or booking.get('paymentStatus') == 'Expired':
                    continue
                
                if booking['standNumber'] == stand_id:
                    start = datetime.fromisoformat(booking['startTime'])
                    end = datetime.fromisoformat(booking['endTime'])
                    
                    if start <= now <= end:
                        has_active_booking = True
                        break
                    elif now < start:
                        has_active_booking = True
                        stand['status'] = 'booked'
                        stand['current_booking_id'] = booking['id']
                        break
            
            if not has_active_booking and stand['status'] != 'available':
                stand['status'] = 'available'
                stand['current_booking_id'] = None
                updated_stands = True
        
        if updated_stands:
            self.write_json_file(self.stands_file, stands_data)

    def get_stand_current_status(self, stand_number):
        """Determine the actual status of a stand at current time.
        Returns 'booked', 'available', 'open', or 'closed' based on active bookings."""
        stand_number = int(stand_number)
        now = datetime.now()
        data = self.read_json_file(self.bookings_file)
        
        # Check for active bookings on this stand
        for booking in data['bookings']:
            if booking['standNumber'] == stand_number:
                # Skip cancelled bookings
                if booking.get('paymentStatus') == 'Cancelled':
                    continue
                
                start = datetime.fromisoformat(booking['startTime'])
                end = datetime.fromisoformat(booking['endTime'])
                
                if start <= now <= end:
                    # Booking is active - check scan status (open/closed)
                    return booking.get('standStatus', 'closed')
                elif now < start:
                    # Future booking
                    return 'booked'
        
        # No active bookings
        return 'available'

    def get_booking_stand_status(self, booking_id):
        """Get current stand status for a booking"""
        booking = self.get_booking_by_id(booking_id)
        if booking:
            return booking.get('standStatus', 'Closed')
        return 'Closed'
