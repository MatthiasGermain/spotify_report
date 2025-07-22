"""
Script to send daily Spotify reports via email.
"""
import logging
import os
import sys
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def format_report_html(report_content):
    """
    format_report_html formats the report content into HTML for better readability.
    """
    logging.info("Formatting report content to HTML")
    # Split report into sections
    lines = report_content.splitlines()
    html = []

    # Header
    html.append("<h2 style='color:#1DB954;'>Spotify Daily Report</h2>")

    # Stats and previous day
    prev_section = []
    stats_section = []
    in_prev = False
    for line in lines:
        if line.startswith('Previous day'):
            in_prev = True
            prev_section.append(f"<div style='font-size:15px;color:#888;'>{line}</div>")
        elif in_prev and (line.lstrip().startswith('Total listening time:') or line.lstrip().startswith('Total tracks listened:')):
            prev_section.append(f"<div style='font-size:15px;color:#888;'>{line}</div>")
        elif in_prev and line.lstrip().startswith('Change in'):
            prev_section.append(f"<div style='font-size:15px;color:#1DB954;font-weight:bold;'>{line}</div>")
        elif in_prev and line.strip() == '':
            in_prev = False
        elif line.startswith('Report for'):
            stats_section.append(f"<div style='font-size:18px;color:#333;margin-bottom:8px;'><b>{line}</b></div>")
        elif line.startswith('Total listening time:') or line.startswith('Total tracks listened:'):
            stats_section.append(f"<div style='font-size:16px;color:#444;margin-bottom:4px;'><b>{line}</b></div>")
    if prev_section:
        html.append("<div style='background:#eafbe7;padding:10px;border-radius:6px;margin-bottom:10px;'>" + "<br>".join(prev_section) + "</div>")
    html.extend(stats_section)

    # Tracks listened section
    if 'Tracks listened by count' in report_content:
        try:
            start = lines.index(next(l for l in lines if l.startswith('Tracks listened by count')))
        except StopIteration:
            start = -1
        if start != -1:
            track_lines = []
            for line in lines[start+1:]:
                if not line.strip():
                    break
                track_lines.append(line.strip())
            html.append("<div style='margin-top:10px;'><b style='color:#1DB954;'>Top 5 tracks by listen count:</b><ul style='font-size:15px;color:#222;'>")
            for line in track_lines[:5]:
                html.append(f"<li>{line}</li>")
            html.append("</ul></div>")
            if len(track_lines) > 5:
                html.append("<details style='margin-top:5px;'><summary style='font-size:15px;color:#888;'>Show all tracks</summary><ul style='font-size:15px;color:#222;'>")
                for line in track_lines[5:]:
                    html.append(f"<li>{line}</li>")
                html.append("</ul></details>")

    # Top artists section
    if 'Top artists by listen count:' in report_content:
        try:
            start = lines.index(next(l for l in lines if l.startswith('Top artists by listen count:')))
        except StopIteration:
            start = -1
        if start != -1:
            artist_lines = []
            for line in lines[start+1:]:
                if not line.strip():
                    break
                artist_lines.append(line.strip())
            html.append("<div style='margin-top:10px;'><b style='color:#1DB954;'>Top 5 artists by listen count:</b><ul style='font-size:15px;color:#222;'>")
            for line in artist_lines[:5]:
                html.append(f"<li>{line}</li>")
            html.append("</ul></div>")
            if len(artist_lines) > 5:
                html.append("<details style='margin-top:5px;'><summary style='font-size:15px;color:#888;'>Show all artists</summary><ul style='font-size:15px;color:#222;'>")
                for line in artist_lines[5:]:
                    html.append(f"<li>{line}</li>")
                html.append("</ul></details>")
    return "\n".join(html)

def send_report_email(report_path, date):
    """
    send_report_email sends the daily report via email.
    """
    logging.info("Sending report email for %s from %s", date, report_path)
    load_dotenv()
    logging.info("Loaded environment variables")
    sender = os.getenv('SENDER_MAIL')
    password = os.getenv('SENDER_APP_PASSWORD')
    receiver = os.getenv('RECEIVER_MAIL')
    subject = f"spotify_report - {date}"
    # Read report
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    logging.info("Read report content from file")
    # Format email
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    logging.info("Prepared email: From %s To %s Subject %s", sender, receiver, subject)
    # Improved HTML formatting
    html_body = f"""
    <html><body style='background:#f7f7f7;padding:20px;'>
    <div style='max-width:600px;margin:auto;background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 8px #ccc;'>
    {format_report_html(report_content)}
    </div>
    </body></html>
    """
    msg.attach(MIMEText(html_body, 'html'))
    # Send email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
    except Exception as e:
        logging.error("Failed to send email: %s", e)

if __name__ == "__main__":
    date = sys.argv[1] if len(sys.argv) > 1 else None
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    report_path = os.path.join(os.getenv('DATA_DIR', os.path.join(os.path.dirname(__file__), '../data')), f"{date}_report.txt")
    send_report_email(report_path, date)
