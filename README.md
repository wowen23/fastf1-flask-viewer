# FastF1 Flask Viewer

A lightweight standalone Flask application for viewing F1 race data from the FastF1 SQLite database.

## Features

- 📊 Session list with all available races
- 🏁 Race results and standings
- 📈 Interactive race progression charts (Chart.js)
- ⏱️ Detailed lap-by-lap data for each driver
- 📡 Telemetry visualization (speed, throttle, brake)

## Prerequisites

- Python 3.7+
- `f1_data.db` database in parent directory

## Installation

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

1. Start the Flask server:
```bash
python3 app.py
```

2. Open your browser to:
```
http://localhost:5000
```

## Structure

```
fastf1_flask_app/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── templates/             # Jinja2 templates
│   ├── base.html          # Base template with Bootstrap 5.3
│   ├── index.html         # Session list
│   ├── session.html       # Session detail with charts
│   ├── driver.html        # Driver lap list
│   └── lap.html           # Lap telemetry
└── static/                # Static files (currently empty)
```

## Routes

- `/` - Session list
- `/session/<session_id>` - Session detail
- `/driver/<session_id>/<driver_id>` - Driver laps
- `/lap/<session_id>/<driver_id>/<lap_number>` - Lap telemetry

## Design

The application uses Bootstrap 5.3.0 with the same visual design as the PHP admin panel implementation.
