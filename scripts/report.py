"""
Report script to generate daily Spotify listening reports.
"""
import logging
import csv
import os
from datetime import datetime, timedelta
from collections import Counter

def parse_datetime(dt_str):
    """
    parse_datetime converts a Spotify datetime string to a datetime object.
    """
    logging.info("Parsing datetime string: %s", dt_str)
    # Example: 2025-07-19T15:23:58.240Z
    return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ")

def min_sec_to_seconds(min_sec):
    """
    min_sec_to_seconds converts a string in "MM:SS" format to total seconds.
    """
    m, s = min_sec.split(":")
    return int(m) * 60 + int(s)

def generate_daily_report(date_str, data_dir):
    """
    generate_daily_report generates a daily report for the given date.
    """
    logging.info("Generating daily report for %s in %s", date_str, data_dir)
    file_path = os.path.join(os.getenv('DATA_DIR', data_dir), f"{date_str}.csv")
    logging.info("Looking for file: %s", file_path)
    if not os.path.exists(file_path):
        logging.warning("No data for %s", date_str)
        print(f"No data for {date_str}")
        return
    tracks = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tracks.append(row)
    logging.info("Found %d tracks for %s", len(tracks), date_str)
    if not tracks:
        logging.warning("No tracks found for %s", date_str)
        print(f"No tracks found for {date_str}")
        return
    # Count listens for all tracks

    track_names = [t['Track Name'] for t in tracks]
    track_counts = Counter(track_names)
    logging.info("Track counts: %s", track_counts)
    # Count listens for all artists
    artist_list = []
    for t in tracks:
        # Split artists by comma and strip whitespace
        artist_list.extend([a.strip() for a in t['Artists'].split(',')])
    artist_counts = Counter(artist_list)
    logging.info("Artist counts: %s", artist_counts)
    # Calculate total listening time
    total_seconds = 0
    for i, track in enumerate(tracks):
        duration = min_sec_to_seconds(track['Duration'])
        played_at = parse_datetime(track['Played At'])
        if i+1 < len(tracks):
            next_played_at = parse_datetime(tracks[i+1]['Played At'])
            diff = (played_at - next_played_at).total_seconds()
            listened = min(duration, int(diff)) if diff > 0 else duration
        else:
            listened = duration
        total_seconds += listened
    logging.info("Total listening time (seconds): %d", total_seconds)
    # Get previous day
    prev_date = (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime('%Y-%m-%d')
    prev_file = os.path.join(os.getenv('DATA_DIR', data_dir), f"{prev_date}.csv")
    prev_total_seconds = None
    prev_total_tracks = None
    logging.info("Looking for previous day file: %s", prev_file)
    if os.path.exists(prev_file):
        prev_tracks = []
        with open(prev_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                prev_tracks.append(row)
        prev_total_tracks = len(prev_tracks)
        prev_total_seconds = 0
        for i, track in enumerate(prev_tracks):
            duration = min_sec_to_seconds(track['Duration'])
            played_at = parse_datetime(track['Played At'])
            if i+1 < len(prev_tracks):
                next_played_at = parse_datetime(prev_tracks[i+1]['Played At'])
                diff = (played_at - next_played_at).total_seconds()
                listened = min(duration, int(diff)) if diff > 0 else duration
            else:
                listened = duration
            prev_total_seconds += listened
    # Write report
    report_path = os.path.join(os.getenv('DATA_DIR', data_dir), f"{date_str}_report.txt")
    logging.info("Writing report to %s", report_path)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"Report for {date_str}\n")
        if prev_total_seconds is not None and prev_total_tracks is not None:
            f.write(f"Previous day ({prev_date}):\n")
            f.write(f"Total listening time: {prev_total_seconds//60} min {prev_total_seconds%60} sec\n")
            f.write(f"Total tracks listened: {prev_total_tracks}\n")
            # Percent change
            time_pct = ((total_seconds - prev_total_seconds) / prev_total_seconds * 100) if prev_total_seconds else 0
            tracks_pct = ((len(tracks) - prev_total_tracks) / prev_total_tracks * 100) if prev_total_tracks else 0
            f.write(f"Change in listening time: {time_pct:+.1f}%\n")
            f.write(f"Change in tracks listened: {tracks_pct:+.1f}%\n\n")
        f.write(f"Total listening time: {total_seconds//60} min {total_seconds%60} sec\n")
        f.write(f"Total tracks listened: {len(tracks)}\n\n")
        f.write("Tracks listened by count (ordered):\n")
        for name, count in track_counts.most_common():
            f.write(f"  {name}: {count} listens\n")
        f.write("\nTop artists by listen count:\n")
        for artist, count in artist_counts.most_common():
            f.write(f"  {artist}: {count} listens\n")
    logging.info("Report written to %s", report_path)

if __name__ == "__main__":
    # Example usage: generate_daily_report('2025-07-19', '../data')
    import sys
    date = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime('%Y-%m-%d')
    generate_daily_report(date, os.path.join(os.path.dirname(__file__), '../data'))
