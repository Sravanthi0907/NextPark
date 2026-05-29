from flask import (
    Flask, render_template, request, jsonify, flash,
    session, redirect, url_for, send_file, send_from_directory
)
import cv2
import json
import os
import base64
import numpy as np
from datetime import datetime
from functools import wraps
from data_handlers import DataHandler, VEHICLE_RATES_PER_HOUR

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "NextPark-dev-secret-change-me")

data_handler = DataHandler()

DATA_FILE = "data.json"
QR_HISTORY_FILE = "qr_history.json"

stands = {str(i): "available" for i in range(1, 11)}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            if request.method != "GET":
                return jsonify({"success": False, "message": "Login required."}), 401
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def api_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"success": False, "message": "Login required."}), 401
        return view(*args, **kwargs)
    return wrapped


def current_user():
    if not session.get("user_id"):
        return None
    return data_handler.get_user_by_id(session["user_id"])


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"stand1": "closed", "stand2": "closed", "access": {}}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_qr_history():
    if os.path.exists(QR_HISTORY_FILE):
        with open(QR_HISTORY_FILE, "r") as f:
            return json.load(f)
    return []


def save_qr_history(history):
    with open(QR_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


def add_qr_history_entry(stand, action, user, status, booking_id=None):
    history = load_qr_history()
    
    # Get current stand status from data_handler
    current_stand_status = data_handler.get_stand_current_status(stand)
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "stand": str(stand),
        "action": action,
        "user": user,
        "status": status,
        "standStatus": current_stand_status,  # Add current parking activity status
    }
    if booking_id is not None:
        entry["bookingId"] = booking_id
    history.append(entry)
    save_qr_history(history)


def decode_qr(image_data):
    try:
        image_data = image_data.split(",")[1]
        image_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(image)
        return data.strip() if data else None
    except Exception:
        return None


def close_expired_stand_access():
    data = load_data()
    now = datetime.now()
    changed = False
    access_map = data.get("access", {})

    for stand_key, info in list(access_map.items()):
        until = info.get("until")
        if until and datetime.fromisoformat(until) < now:
            data[stand_key] = "closed"
            access_map.pop(stand_key, None)
            changed = True

    if changed:
        data["access"] = access_map
        save_data(data)


def grant_stand_access(stand, user, booking):
    """Grant stand access and toggle status based on QR scan count"""
    stand_key = f"stand{stand}"
    data = load_data()
    if "access" not in data:
        data["access"] = {}

    # Increment scan count and get new status
    scan_count, new_status = data_handler.increment_qr_scan_count(booking["id"])
    
    # Update stand status based on odd/even scan count
    data[stand_key] = new_status.lower()
    data["access"][stand_key] = {
        "userId": user["id"],
        "qrToken": user["qrToken"],
        "bookingId": booking["id"],
        "until": booking["endTime"],
        "scanCount": scan_count,
        "standStatus": new_status
    }
    save_data(data)
    
    # Update stand status globally
    data_handler.update_stand_status(stand, new_status.lower(), booking["id"])
    
    # Mark booking access as granted on first scan
    if scan_count == 1:
        data_handler.mark_booking_access_granted(booking["id"])
    
    # Record QR scan in history
    add_qr_history_entry(
        stand, "qr_scan", user["id"], new_status, booking_id=booking["id"]
    )
    
    end_display = datetime.fromisoformat(booking["endTime"]).strftime("%I:%M %p on %d %b")
    scan_info = f"Scan #{scan_count}: Stand {stand} is now {new_status}."
    return True, f"{scan_info} Access remains active until {end_display}."


@app.route("/")
@login_required
def home():
    data_handler.cleanup_expired_bookings()
    return render_template("home.html")


@app.route("/booking")
@login_required
def booking():
    return render_template(
        "booking.html",
        vehicle_types=list(VEHICLE_RATES_PER_HOUR.keys()),
    )


@app.route("/history")
@login_required
def history():
    return render_template("history.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        vehicle_reg = request.form.get("vehicle_reg", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not all([username, email, vehicle_reg, password]):
            flash("All fields are required.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
        else:
            user, error = data_handler.create_user(username, email, vehicle_reg, password)
            if error:
                flash(error, "error")
            else:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                flash("Account created! Your unique QR code is ready under My QR.", "success")
                return redirect(url_for("profile"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("home"))

    if request.method == "POST":
        login_id = request.form.get("login_id", "").strip()
        password = request.form.get("password", "")
        user = data_handler.authenticate_user(login_id, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['username']}!", "success")
            next_url = request.args.get("next") or url_for("home")
            return redirect(next_url)
        flash("Invalid username/email or password.", "error")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))


@app.route("/profile")
@login_required
def profile():
    user = current_user()
    return render_template("profile.html", user=user)


@app.route("/media/qr/<filename>")
@login_required
def serve_user_qr(filename):
    user = current_user()
    expected = os.path.basename(user.get("qrImagePath", ""))
    if filename != expected or not os.path.exists(os.path.join("users", filename)):
        return "", 403
    return send_from_directory("users", filename, mimetype="image/jpeg")


@app.route("/api/qr/download")
@login_required
def api_qr_download():
    user = current_user()
    path = user.get("qrImagePath")
    if not path or not os.path.exists(path):
        flash("QR code file not found.", "error")
        return redirect(url_for("profile"))
    return send_file(
        path,
        as_attachment=True,
        download_name=f"nextpark_{user['username']}.jpg",
        mimetype="image/jpeg",
    )


@app.route("/api/calculate_fee", methods=["POST"])
@api_login_required
def calculate_fee():
    payload = request.json or {}
    booking_date = payload.get("bookingDate")
    start_time = payload.get("startTime")
    end_time = payload.get("endTime")
    vehicle_type = payload.get("vehicleType")

    if not all([booking_date, start_time, end_time, vehicle_type]):
        return jsonify({"success": False, "message": "All booking fields are required."}), 400

    try:
        start_iso = data_handler.combine_date_time(booking_date, start_time).isoformat()
        end_iso = data_handler.combine_date_time(booking_date, end_time).isoformat()
    except ValueError:
        return jsonify({"success": False, "message": "Invalid date or time."}), 400

    fee, error = data_handler.calculate_fee(vehicle_type, start_iso, end_iso)
    if error:
        return jsonify({"success": False, "message": error}), 400

    return jsonify({"success": True, **fee, "startTime": start_iso, "endTime": end_iso})


@app.route("/get_history", methods=["GET"])
@api_login_required
def get_history():
    data_handler.cleanup_expired_bookings()
    bookings = data_handler.get_user_bookings(session["user_id"])
    bookings.sort(key=lambda b: b.get("startTime", ""), reverse=True)
    return jsonify(bookings)


@app.route("/get_qr_history", methods=["GET"])
@api_login_required
def get_qr_history():
    user = current_user()
    identifiers = data_handler.get_user_identifiers(user)
    history = [entry for entry in load_qr_history() if entry.get("user") in identifiers]
    history.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    return jsonify(history)


@app.route("/get_status", methods=["GET"])
@api_login_required
def get_status():
    close_expired_stand_access()
    data_handler.cleanup_expired_bookings()  # Update stand statuses based on booking times
    data = load_data()
    
    # Get current stand statuses from stands.json
    stands_data = data_handler.read_json_file(data_handler.stands_file)
    stands_status = {}
    for stand in stands_data.get('stands', []):
        stands_status[str(stand['id'])] = stand['status']
    
    return jsonify({
        "stand1": data.get("stand1", "closed"),
        "stand2": data.get("stand2", "closed"),
        "access": data.get("access", {}),
        "standsStatus": stands_status,
        **stands
    })


@app.route("/verify_qr_access", methods=["POST"])
@api_login_required
def verify_qr_access():
    payload = request.json or {}
    booking_id = payload.get("bookingId")
    image_data = payload.get("image")

    if not booking_id or not image_data:
        return jsonify({"success": False, "message": "Booking and QR scan are required."})

    if not data_handler.booking_belongs_to_user(booking_id, session["user_id"]):
        return jsonify({"success": False, "message": "Booking not found."}), 404

    can_access, booking = data_handler.user_can_access_booking(session["user_id"], booking_id)
    if not can_access:
        if booking and not data_handler.booking_has_started(booking):
            return jsonify({
                "success": False,
                "message": "Access is available only after your booking start time."
            })
        return jsonify({
            "success": False,
            "message": "Booking is not active. Check payment and booking window."
        })

    user = current_user()

    scanned = decode_qr(image_data)
    
    print("========== QR DEBUG ==========")
    print("Scanned QR:", scanned)
    print("Current User:", user["username"])
    print("Expected Token:", user["qrToken"])
    print("=============================")

    if not scanned:
        return jsonify({"success": False, "message": "No QR code detected. Try again."})

    if scanned != user["qrToken"]:
        return jsonify({
            "success": False,
            "message": "QR code does not match your account. Use your personal QR from My QR."
        })

    stand = booking["standNumber"]
    
    # Process QR scan - toggle stand status based on scan count
    success, message = grant_stand_access(stand, user, booking)
    return jsonify({"success": success, "message": message})


@app.route("/save_booking", methods=["POST"])
@api_login_required
def save_booking():
    payload = request.json or {}
    booking_date = payload.get("bookingDate")
    start_time = payload.get("startTime")
    end_time = payload.get("endTime")
    vehicle_type = payload.get("vehicleType")
    stand_number = payload.get("standNumber")

    if not all([booking_date, start_time, end_time, vehicle_type, stand_number]):
        return jsonify({"success": False, "message": "Complete all booking fields."}), 400

    try:
        start_iso = data_handler.combine_date_time(booking_date, start_time).isoformat()
        end_iso = data_handler.combine_date_time(booking_date, end_time).isoformat()
    except ValueError:
        return jsonify({"success": False, "message": "Invalid date or time."}), 400

    fee, error = data_handler.calculate_fee(vehicle_type, start_iso, end_iso)
    if error:
        return jsonify({"success": False, "message": error}), 400

    # Check for booking conflicts
    is_available, conflicting_booking = data_handler.check_stand_availability(
        stand_number, start_iso, end_iso
    )
    if not is_available:
        conflict_start = datetime.fromisoformat(conflicting_booking['startTime']).strftime("%H:%M")
        conflict_end = datetime.fromisoformat(conflicting_booking['endTime']).strftime("%H:%M")
        return jsonify({
            "success": False,
            "message": f"Stand {stand_number} is already booked from {conflict_start} to {conflict_end}. Please choose another stand or time."
        }), 409

    booking_data = {
        "standNumber": stand_number,
        "bookingDate": booking_date,
        "startTime": start_iso,
        "endTime": end_iso,
        "vehicleType": fee["vehicleType"],
        "amountPaid": fee["amount"],
        "paymentStatus": payload.get("paymentStatus", "Successful"),
        "userId": session["user_id"],
    }

    new_booking = data_handler.create_booking(booking_data)
    
    # Update global stand status to "reserved" and update stands dictionary
    stands[str(stand_number)] = "booked"
    
    add_qr_history_entry(
        stand_number, "book", session["user_id"], "confirmed", booking_id=new_booking["id"]
    )
    add_qr_history_entry(
        stand_number, "payment", session["user_id"], "Successful", booking_id=new_booking["id"]
    )

    return jsonify({"success": True, "booking": new_booking, "fee": fee})


@app.route("/update_payment_status", methods=["POST"])
@api_login_required
def update_payment_status():
    payload = request.json or {}
    booking_id = payload.get("bookingId")

    if not data_handler.booking_belongs_to_user(booking_id, session["user_id"]):
        return jsonify({"success": False, "message": "Booking not found."}), 404

    booking = data_handler.get_booking_by_id(booking_id)
    amount = payload.get("amountPaid", booking.get("amountPaid", 0))
    data_handler.update_payment_status(booking_id, payload.get("status"), amount)

    if booking:
        add_qr_history_entry(
            booking["standNumber"],
            "payment",
            session["user_id"],
            payload.get("status"),
            booking_id=booking_id,
        )

    return jsonify({"success": True})


@app.route("/cancel_booking", methods=["POST"])
@api_login_required
def cancel_booking():
    payload = request.json or {}
    booking_id = payload.get("bookingId")

    if not data_handler.booking_belongs_to_user(booking_id, session["user_id"]):
        return jsonify({"success": False, "message": "Booking not found."}), 404

    booking = data_handler.get_booking_by_id(booking_id)

    if booking and booking.get("accessStatus") == "granted":
        return jsonify({
            "success": False,
            "message": "Cannot cancel a booking after stand access has been granted.",
        }), 403

    if booking:
        stands[str(booking["standNumber"])] = "available"
        add_qr_history_entry(
            booking["standNumber"],
            "cancel",
            session["user_id"],
            "cancelled",
            booking_id=booking_id,
        )
        data_handler.cancel_booking(booking_id)

    return jsonify({"success": True})


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_ENV") != "production"
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
    
