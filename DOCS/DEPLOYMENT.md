# Deployment Guide (Render)

This application is configured for deployment on [Render](https://render.com/).

## Prerequisites

1.  A GitHub repository containing this project.
2.  A Render account.

## Deployment Steps

1.  **Push to GitHub**: Ensure your latest code (including `f1_data.db`, `requirements.txt`, and `render.yaml`) is pushed to your GitHub repository.
    *   *Note: Since this is a viewer app, we commit the SQLite database (`f1_data.db`) directly to the repository. Render's file system is ephemeral, meaning any changes made to the database *while the app is running* on Render will be lost on the next deploy/restart. This is fine for a read-only viewer.*

2.  **Create a Web Service on Render**:
    *   Go to the Render Dashboard.
    *   Click **New +** and select **Web Service**.
    *   Connect your GitHub repository.
    *   Render should automatically detect the `render.yaml` file (Blueprint) or you can configure it manually:
        *   **Runtime**: Python 3
        *   **Build Command**: `pip install -r requirements.txt`
        *   **Start Command**: `gunicorn app:app`

3.  **Deploy**: Click **Create Web Service**. Render will build your app and deploy it.

## Updating Data

To update the data on the live site:
1.  Run `python fastf1_to_sqlite.py` locally to fetch new race data.
2.  Commit the updated `f1_data.db` to git.
3.  Push to GitHub.
4.  Render will automatically redeploy with the new data.
