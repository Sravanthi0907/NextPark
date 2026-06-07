# NextPark — Parking Stand Access Management System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python" alt="Python 3.8+"/>
  <img src="https://img.shields.io/badge/Flask-3.x-black?logo=flask" alt="Flask"/>
  <img src="https://img.shields.io/badge/jsQR-Local-green" alt="jsQR"/>
  <img src="https://img.shields.io/badge/Render-Ready-46E3B7?logo=render" alt="Render Ready"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License"/>
</p>

**NextPark** is an intelligent, high-performance, and secure parking stand access management system. It bridges **dynamic client-side image processing** with a **robust Flask backend** to handle real-time reservation updates, secure payments, and dynamic QR code stand toggling.

---

## Key Features

| Feature | Description |
|---|---|
| **Local Client-Side QR Decoding** | Instantly decodes user access tokens inside the browser using a locally-served `jsQR` library, eliminating server-side OpenCV/NumPy CPU bottlenecks |
| **Dynamic Access Toggling** | Scan count tracking toggles stand status (odd scans = Open, even scans = Closed) |
| **Dynamic In-Memory QR Codes** | Dynamic on-the-fly QR image streaming ensures profile codes and download files never break, even on ephemeral filesystems |
| **Persistent Disk Support** | Seamlessly integrates with cloud storage mounts via the `DATA_DIR` environment variable to prevent data loss on restarts |
| **Automatic HTTPS Redirect** | Enforces secure TLS connection contexts in production, guaranteeing browser camera permission authorization |

---

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+), FontAwesome 6, Plus Jakarta Sans
- **Backend**: Flask (Python 3.8+), Gunicorn (WSGI)
- **Database**: Lightweight JSON-based file storage
- **Client-Side Scanner**: `jsQR` (served locally for 100% offline & remote reliability)
- **Dynamic Assets**: `qrcode` + `Pillow` (in-memory dynamic QR image streaming)

---

## Project Structure

```
NextPark/
│
├── app.py                  ← Main Flask application server & API routes
├── data_handlers.py        ← Business logic, rate calculation & database handlers
│
├── requirements.txt        ← Python production dependencies
├── Procfile                ← Gunicorn deployment command (Render)
├── render.yaml             ← Render service blueprint
├── runtime.txt             ← Python version specification
├── .gitignore
└── README.md
│
├── static/
│   ├── css/
│   │   └── main.css        ← Enhanced UI responsive styling
│   └── js/
│       └── jsQR.min.js     ← Local client-side QR decoding library
│
├── templates/
│   ├── layout.html         ← Base page shell template
│   ├── _head.html          ← Included head metadata and styles
│   ├── _nav.html           ← Included navigation bar
│   ├── _flash.html         ← Included flash messages
│   ├── home.html           ← Home dashboard page
│   ├── booking.html        ← Slot reservation page
│   ├── history.html        ← Activity log with scanner modal
│   ├── profile.html        ← User profile page (shows personal QR)
│   ├── login.html          ← User login screen
│   └── register.html       ← User registration screen
│
└── data/                   ← Mount directory for persistent disk storage (or project root)
    ├── bookings.json       ← Saved booking records
    ├── users.json          ← Registered user accounts database
    ├── stands.json         ← Parking stands metadata
    ├── data.json           ← General application data
    ├── history.json        ← Reserved history logs
    └── qr_history.json     ← QR scan audit logs
```

---

## Installation

### Prerequisites
- **Python 3.8+**
- **Webcam** — required for the scanner interface
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/NextPark.git
cd NextPark
```

### 2. Create a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Complete Workflow & Deployment

Follow these steps to configure, run, and deploy the application.

---

### Local Development Setup

Run the Flask development server on your local machine.

```bash
python app.py
```

- Open your browser and navigate to: **http://localhost:5000**
- *Note: Camera access is permitted locally over insecure HTTP contexts only on `localhost`.*
- 
---
