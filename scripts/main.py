"""
Main script to generate and send daily Spotify reports.
"""
import logging
import os
import csv
from datetime import datetime, timedelta
from storage import save_tracks_per_day
from spotify_client import get_recent_tracks
from report import generate_daily_report
from send_email import send_report_email

def get_sent_report_dates(send_report_path):
    """
    get_sent_report_dates retrieves the dates for which reports have already been sent.
    """
    logging.info("Checking sent report dates in %s", send_report_path)
    if not os.path.exists(send_report_path):
        return set()
    with open(send_report_path, 'r', encoding='utf-8') as f:
        return set(row[0] for row in csv.reader(f) if row)

def add_sent_report_date(send_report_path, date):
    """
    add_sent_report_date appends a date to the send report CSV file.
    """
    logging.info("Adding sent report date %s to %s", date, send_report_path)
    with open(send_report_path, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([date])

def main():
    """
    Main function to orchestrate the daily report generation and sending process.
    """
    logging.info("Starting main orchestration")
    data_dir = os.getenv('DATA_DIR', os.path.abspath(os.path.join(os.path.dirname(__file__), '../data')))
    send_report_path = os.path.join(data_dir, 'send_report.csv')

    # 1. Get last 50 listens and update daily CSVs
    logging.info("Getting recent tracks and updating daily CSVs")
    track_data = get_recent_tracks(return_data=True)  # update CSVs and get track data
    save_tracks_per_day(track_data, data_dir)

    # 2. Check if yesterday's report was sent
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    sent_dates = get_sent_report_dates(send_report_path)
    if yesterday in sent_dates:
        logging.info("Report for %s already sent.", yesterday)
        return

    # 3. Generate, send, and record report
    logging.info("Generating, sending, and recording report")
    generate_daily_report(yesterday, data_dir)
    report_path = os.path.join(data_dir, f"{yesterday}_report.txt")
    send_report_email(report_path, yesterday)
    add_sent_report_date(send_report_path, yesterday)
    logging.info("Report for %s sent and recorded.", yesterday)

if __name__ == "__main__":
    main()
