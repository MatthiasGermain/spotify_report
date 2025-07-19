# spotify_report

## Overview
`spotify_report` is a Python project that generates daily reports of your Spotify listening history. It fetches your recent tracks, organizes them by day, analyzes listening patterns, and produces a summary report. The report includes total listening time, track and artist counts, and day-to-day changes. Reports can be sent via email in a formatted HTML style.

## Features
- Fetches recent Spotify tracks using Spotipy
- Saves daily listening data to CSV files
- Generates text reports with stats and comparisons to previous days
- Sends reports via email with HTML formatting
- Avoids duplicate entries and tracks sent reports

## Project Structure
- `scripts/`
  - `main.py`: Orchestrates fetching, report generation, and email sending
  - `spotify_client.py`: Handles Spotify API authentication and data fetching
  - `storage.py`: Saves tracks to daily CSV files, avoids duplicates
  - `report.py`: Analyzes daily data and generates reports
  - `send_email.py`: Formats and sends reports via email
- `data/`: Contains daily CSVs and generated reports

## Usage
1. Set up your Spotify API credentials in a `.env` file (see Spotipy docs)
2. Run `main.py` to fetch new data, generate yesterday's report, and send it via email:
   ```powershell
   python scripts/main.py
   ```
3. Reports are saved in `data/` and sent only once per day.

## Requirements
- Python 3.7+
- Spotipy
- python-dotenv

## Environment Variables
Create a `.env` file with:
```
CLIENT_ID=your_spotify_client_id
CLIENT_SECRET=your_spotify_client_secret
REDIRECT_URI=your_redirect_uri
SENDER_MAIL=your_email@gmail.com
SENDER_APP_PASSWORD=your_app_password
RECEIVER_MAIL=recipient_email@gmail.com
```

## License
MIT