#!/usr/bin/env python3
"""
FastF1 to SQLite Importer
Fetches F1 data from FastF1 and stores it in a local SQLite database
"""

import fastf1
import sqlite3
import pandas as pd
from datetime import datetime
import json

# Configuration
CACHE_DIR = '/tmp/fastf1_cache'
DB_PATH = '/Users/williamowen/driverdb/f1_data.db'
YEAR = 2025
EVENT = 'Las Vegas'  # Las Vegas Grand Prix
SESSION_TYPE = 'Race'

# Enable caching
fastf1.Cache.enable_cache(CACHE_DIR)

print("=" * 80)
print(f"FastF1 to SQLite Importer - {EVENT} {YEAR} {SESSION_TYPE}")
print("=" * 80)

# Initialize database connection
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create tables
print("\n📦 Creating database schema...")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    year INTEGER,
    round_number INTEGER,
    event_name TEXT,
    country TEXT,
    location TEXT,
    session_name TEXT,
    session_date DATETIME,
    session_type TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS drivers (
    driver_id TEXT PRIMARY KEY,
    driver_number INTEGER,
    broadcast_name TEXT,
    full_name TEXT,
    first_name TEXT,
    last_name TEXT,
    country_code TEXT,
    team_name TEXT,
    team_color TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS session_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    driver_id TEXT,
    driver_number INTEGER,
    position REAL,
    grid_position REAL,
    points REAL,
    status TEXT,
    time TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS laps (
    lap_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    driver_id TEXT,
    lap_number INTEGER,
    lap_time_seconds REAL,
    sector1_time_seconds REAL,
    sector2_time_seconds REAL,
    sector3_time_seconds REAL,
    speed_i1 REAL,
    speed_i2 REAL,
    speed_fl REAL,
    speed_st REAL,
    compound TEXT,
    tyre_life INTEGER,
    stint INTEGER,
    is_personal_best BOOLEAN,
    track_status TEXT,
    position INTEGER,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS telemetry (
    telemetry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    driver_id TEXT,
    lap_number INTEGER,
    distance REAL,
    speed REAL,
    rpm REAL,
    gear INTEGER,
    throttle REAL,
    brake BOOLEAN,
    drs INTEGER,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
)
""")

conn.commit()
print("✅ Database schema created")

# Load session
print(f"\n🏎️  Loading {EVENT} {YEAR} {SESSION_TYPE}...")
session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
session.load()

print(f"✅ Session loaded: {session.event['EventName']} - {session.name}")
print(f"   Date: {session.date}")
print(f"   Drivers: {len(session.drivers)}")

# Insert session data
session_id = f"{YEAR}_{session.event['RoundNumber']:02d}_{SESSION_TYPE}"
cursor.execute("""
    INSERT OR REPLACE INTO sessions
    (session_id, year, round_number, event_name, country, location, session_name, session_date, session_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    session_id,
    YEAR,
    int(session.event['RoundNumber']),
    session.event['EventName'],
    session.event['Country'],
    session.event['Location'],
    session.name,
    session.date.isoformat(),
    SESSION_TYPE
))

print(f"\n👥 Importing driver data...")
# Insert drivers
drivers_data = []
for driver_num in session.drivers:
    driver_info = session.get_driver(driver_num)
    driver_id = driver_info['Abbreviation']

    drivers_data.append((
        driver_id,
        int(driver_info['DriverNumber']) if pd.notna(driver_info['DriverNumber']) else None,
        driver_info['BroadcastName'],
        driver_info['FullName'],
        driver_info['FirstName'],
        driver_info['LastName'],
        driver_info['CountryCode'],
        driver_info['TeamName'],
        driver_info['TeamColor']
    ))

cursor.executemany("""
    INSERT OR REPLACE INTO drivers
    (driver_id, driver_number, broadcast_name, full_name, first_name, last_name, country_code, team_name, team_color)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", drivers_data)

print(f"✅ Imported {len(drivers_data)} drivers")

# Insert session results
print(f"\n🏁 Importing session results...")
results = session.results
results_data = []

for idx, result in results.iterrows():
    results_data.append((
        session_id,
        result['Abbreviation'],
        int(result['DriverNumber']) if pd.notna(result['DriverNumber']) else None,
        float(result['Position']) if pd.notna(result['Position']) else None,
        float(result['GridPosition']) if pd.notna(result['GridPosition']) else None,
        float(result['Points']) if pd.notna(result['Points']) else None,
        result['Status'],
        str(result['Time']) if pd.notna(result['Time']) else None
    ))

cursor.executemany("""
    INSERT INTO session_results
    (session_id, driver_id, driver_number, position, grid_position, points, status, time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", results_data)

print(f"✅ Imported {len(results_data)} results")

# Insert laps
print(f"\n⏱️  Importing lap data...")
laps = session.laps
laps_data = []

for idx, lap in laps.iterrows():
    # Convert timedelta to seconds
    lap_time = lap['LapTime'].total_seconds() if pd.notna(lap['LapTime']) else None
    s1_time = lap['Sector1Time'].total_seconds() if pd.notna(lap['Sector1Time']) else None
    s2_time = lap['Sector2Time'].total_seconds() if pd.notna(lap['Sector2Time']) else None
    s3_time = lap['Sector3Time'].total_seconds() if pd.notna(lap['Sector3Time']) else None

    laps_data.append((
        session_id,
        lap['Driver'],
        int(lap['LapNumber']) if pd.notna(lap['LapNumber']) else None,
        lap_time,
        s1_time,
        s2_time,
        s3_time,
        float(lap['SpeedI1']) if pd.notna(lap['SpeedI1']) else None,
        float(lap['SpeedI2']) if pd.notna(lap['SpeedI2']) else None,
        float(lap['SpeedFL']) if pd.notna(lap['SpeedFL']) else None,
        float(lap['SpeedST']) if pd.notna(lap['SpeedST']) else None,
        lap['Compound'],
        int(lap['TyreLife']) if pd.notna(lap['TyreLife']) else None,
        int(lap['Stint']) if pd.notna(lap['Stint']) else None,
        bool(lap['IsPersonalBest']) if pd.notna(lap['IsPersonalBest']) else False,
        str(lap['TrackStatus']),
        int(lap['Position']) if pd.notna(lap['Position']) else None
    ))

cursor.executemany("""
    INSERT INTO laps
    (session_id, driver_id, lap_number, lap_time_seconds, sector1_time_seconds,
     sector2_time_seconds, sector3_time_seconds, speed_i1, speed_i2, speed_fl, speed_st,
     compound, tyre_life, stint, is_personal_best, track_status, position)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", laps_data)

print(f"✅ Imported {len(laps_data)} laps")

# Sample telemetry from fastest lap only (full telemetry is huge)
print(f"\n📡 Importing sample telemetry (fastest lap)...")
fastest_lap = laps.pick_fastest()
telemetry = fastest_lap.get_car_data()

telemetry_data = []
for idx, point in telemetry.iterrows():
    # Get distance if available, otherwise use None
    distance = float(point['Distance']) if 'Distance' in telemetry.columns and pd.notna(point.get('Distance')) else None

    telemetry_data.append((
        session_id,
        fastest_lap['Driver'],
        int(fastest_lap['LapNumber']),
        distance,
        float(point['Speed']) if pd.notna(point['Speed']) else None,
        float(point['RPM']) if pd.notna(point['RPM']) else None,
        int(point['nGear']) if pd.notna(point['nGear']) else None,
        float(point['Throttle']) if pd.notna(point['Throttle']) else None,
        bool(point['Brake']) if pd.notna(point['Brake']) else False,
        int(point['DRS']) if pd.notna(point['DRS']) else None
    ))

cursor.executemany("""
    INSERT INTO telemetry
    (session_id, driver_id, lap_number, distance, speed, rpm, gear, throttle, brake, drs)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", telemetry_data)

print(f"✅ Imported {len(telemetry_data)} telemetry points")

# Commit and close
conn.commit()
conn.close()

print("\n" + "=" * 80)
print(f"✅ Data successfully imported to: {DB_PATH}")
print("=" * 80)

# Print summary
print(f"\n📊 Import Summary:")
print(f"   Database: {DB_PATH}")
print(f"   Session: {session.event['EventName']} {YEAR}")
print(f"   Drivers: {len(drivers_data)}")
print(f"   Results: {len(results_data)}")
print(f"   Laps: {len(laps_data)}")
print(f"   Telemetry: {len(telemetry_data)} points (fastest lap only)")

print(f"\n💡 You can now query this data with:")
print(f"   sqlite3 {DB_PATH}")
print(f"   SELECT * FROM sessions;")
print(f"   SELECT * FROM drivers;")
print(f"   SELECT * FROM laps WHERE driver_id='VER' LIMIT 10;")
