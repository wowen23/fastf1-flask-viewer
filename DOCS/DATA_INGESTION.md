# Data Ingestion Guide

This project uses [FastF1](https://docs.fastf1.dev/) to fetch Formula 1 race data and store it in a local SQLite database (`f1_data.db`).

## Prerequisites

You need to install the `fastf1` library:

```bash
pip install fastf1 pandas
```

## Using the Ingestion Script

We have provided a script `fastf1_to_sqlite.py` to automate the process of fetching data and populating the database.

### Configuration

Open `fastf1_to_sqlite.py` and modify the configuration section at the top to select the race you want to import:

```python
# Configuration
CACHE_DIR = '/tmp/fastf1_cache'  # Directory to cache downloaded data
DB_PATH = 'f1_data.db'           # Path to your SQLite database
YEAR = 2023                      # Season year
EVENT = 'Monaco'                 # Event name (e.g., 'Monaco', 'Silverstone')
SESSION_TYPE = 'Race'            # 'Race', 'Qualifying', 'FP1', etc.
```

### Running the Script

Run the script from the terminal:

```bash
python fastf1_to_sqlite.py
```

The script will:
1.  Enable caching to speed up subsequent runs.
2.  Connect to (or create) the SQLite database.
3.  Create the necessary tables (`sessions`, `drivers`, `session_results`, `laps`, `telemetry`) if they don't exist.
4.  Download the session data using FastF1.
5.  Insert the data into the database.

## About FastF1 Data

FastF1 provides access to:
*   **Timing Data & Telemetry**: Available from **2018 onwards**.
*   **Session Results & Schedule**: Available from **1950 onwards** (via Ergast/Jolpica integration).

For more detailed information on the available data objects and API, refer to the [official FastF1 documentation](https://docs.fastf1.dev/).

### Caching

FastF1 handles large amounts of data (~50-100MB per session). Caching is enabled by default in our script to improve performance and reduce load on the servers.
