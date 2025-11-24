#!/usr/bin/env python3
"""
FastF1 Flask Viewer - Standalone Application
A lightweight Flask app for viewing F1 data from the FastF1 SQLite database
"""

from flask import Flask, render_template, abort
import sqlite3
import os

app = Flask(__name__)

# Database path (one level up from this folder)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'f1_data.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """Session list view"""
    conn = get_db()
    sessions = conn.execute('SELECT * FROM sessions ORDER BY year DESC, round_number DESC').fetchall()
    conn.close()
    return render_template('index.html', sessions=sessions)

@app.route('/session/<session_id>')
def session(session_id):
    """Session detail view with charts"""
    conn = get_db()
    
    # Get session info
    session = conn.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,)).fetchone()
    if not session:
        abort(404)
    
    # Get race results
    results = conn.execute('''
        SELECT sr.*, d.broadcast_name, d.team_name, d.team_color
        FROM session_results sr
        JOIN drivers d ON sr.driver_id = d.driver_id
        WHERE sr.session_id = ?
        ORDER BY sr.position
    ''', (session_id,)).fetchall()
    
    # Get lap statistics
    lap_stats = conn.execute('''
        SELECT
            driver_id,
            COUNT(*) as total_laps,
            MIN(lap_time_seconds) as fastest_lap,
            AVG(lap_time_seconds) as avg_lap
        FROM laps
        WHERE session_id = ? AND lap_time_seconds IS NOT NULL
        GROUP BY driver_id
        ORDER BY fastest_lap
    ''', (session_id,)).fetchall()
    
    # Get position data for race progression chart
    position_data_raw = conn.execute('''
        SELECT
            l.driver_id,
            l.lap_number,
            l.position,
            d.team_color,
            d.broadcast_name
        FROM laps l
        JOIN drivers d ON l.driver_id = d.driver_id
        WHERE l.session_id = ? AND l.position IS NOT NULL
        ORDER BY l.driver_id, l.lap_number
    ''', (session_id,)).fetchall()
    
    # Convert to dicts for JSON serialization
    position_data = [dict(row) for row in position_data_raw]
    
    # Get stint data
    stint_data_raw = conn.execute('''
        SELECT
            l.driver_id,
            l.lap_number,
            l.stint,
            l.compound,
            l.tyre_life,
            l.lap_time_seconds,
            d.team_color,
            d.broadcast_name,
            sr.position as finish_position
        FROM laps l
        JOIN drivers d ON l.driver_id = d.driver_id
        LEFT JOIN session_results sr ON l.driver_id = sr.driver_id AND l.session_id = sr.session_id
        WHERE l.session_id = ?
        ORDER BY sr.position, l.driver_id, l.lap_number
    ''', (session_id,)).fetchall()
    
    # Convert to dicts for JSON serialization
    stint_data = [dict(row) for row in stint_data_raw]
    
    # Get lap times per lap number
    lap_times_per_lap_raw = conn.execute('''
        SELECT
            lap_number,
            lap_time_seconds
        FROM laps
        WHERE session_id = ? AND lap_time_seconds IS NOT NULL
        ORDER BY lap_number, lap_time_seconds
    ''', (session_id,)).fetchall()
    
    # Convert to dicts for JSON serialization
    lap_times_per_lap = [dict(row) for row in lap_times_per_lap_raw]
    
    conn.close()
    
    return render_template('session.html',
                         session=session,
                         results=results,
                         lap_stats=lap_stats,
                         position_data=position_data,
                         stint_data=stint_data,
                         lap_times_per_lap=lap_times_per_lap)

@app.route('/driver/<session_id>/<driver_id>')
def driver(session_id, driver_id):
    """Driver lap detail view"""
    conn = get_db()
    
    # Get session info
    session = conn.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,)).fetchone()
    if not session:
        abort(404)
    
    # Get driver info
    driver = conn.execute('SELECT * FROM drivers WHERE driver_id = ?', (driver_id,)).fetchone()
    if not driver:
        abort(404)
    
    # Get all laps for this driver
    laps = conn.execute('''
        SELECT *
        FROM laps
        WHERE session_id = ? AND driver_id = ?
        ORDER BY lap_number
    ''', (session_id, driver_id)).fetchall()
    
    conn.close()
    
    return render_template('driver.html',
                         session=session,
                         driver=driver,
                         laps=laps)

@app.route('/lap/<session_id>/<driver_id>/<int:lap_number>')
def lap(session_id, driver_id, lap_number):
    """Lap telemetry detail view"""
    conn = get_db()
    
    # Get session info
    session = conn.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,)).fetchone()
    if not session:
        abort(404)
    
    # Get driver info
    driver = conn.execute('SELECT * FROM drivers WHERE driver_id = ?', (driver_id,)).fetchone()
    if not driver:
        abort(404)
    
    # Get lap info
    lap = conn.execute('''
        SELECT *
        FROM laps
        WHERE session_id = ? AND driver_id = ? AND lap_number = ?
    ''', (session_id, driver_id, lap_number)).fetchone()
    
    if not lap:
        abort(404)
    
    # Get telemetry for this lap
    telemetry_raw = conn.execute('''
        SELECT *
        FROM telemetry
        WHERE session_id = ? AND driver_id = ? AND lap_number = ?
        ORDER BY distance
    ''', (session_id, driver_id, lap_number)).fetchall()
    
    # Convert to dicts for JSON serialization
    telemetry = [dict(row) for row in telemetry_raw]
    
    conn.close()
    
    return render_template('lap.html',
                         session=session,
                         driver=driver,
                         lap=lap,
                         telemetry=telemetry)

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}")
        print("Please ensure f1_data.db is in the parent directory")
        exit(1)
    
    print("=" * 80)
    print("FastF1 Flask Viewer")
    print("=" * 80)
    print(f"Database: {DB_PATH}")
    print("Server: http://localhost:5001")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
