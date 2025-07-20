"""
Storage Script for Spotify Data
"""
import logging
import os
import csv
from collections import defaultdict

def save_listening_history(data, filename):
    """
    Save listening history to a CSV file.
    """
    logging.info("Saving listening history to %s", filename)
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Index', 'Track Name', 'Artists', 'Duration', 'Played At'])
        writer.writerows(data)


def save_tracks_per_day(tracks, data_dir):
    """
    Save tracks to daily CSV files, avoiding duplicates.
    Each track is a dict with keys: index, name, artists, duration, played_at, id
    """
    logging.info("Saving tracks per day to %s", data_dir)
    # Group tracks by date
    tracks_by_date = defaultdict(list)
    for track in tracks:
        date_str = track['played_at'][:10]  # YYYY-MM-DD
        tracks_by_date[date_str].append(track)

    for date, items in tracks_by_date.items():
        file_path = os.path.join(data_dir, f"{date}.csv")
        existing = set()
        rows = []
        # If file exists, read existing played_at+id
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing.add((row['Track ID'], row['Played At']))
                    rows.append(row)
        # Add new tracks if not duplicate
        for track in items:
            key = (track['id'], track['played_at'])
            if key not in existing:
                rows.append({
                    'Index': len(rows)+1,
                    'Track Name': track['name'],
                    'Artists': track['artists'],
                    'Duration': track['duration'],
                    'Played At': track['played_at'],
                    'Track ID': track['id']
                })
                existing.add(key)
        # Write all rows back
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Index', 'Track Name', 'Artists', 'Duration', 'Played At', 'Track ID'])
            writer.writeheader()
            for i, row in enumerate(rows, 1):
                row['Index'] = i
                writer.writerow(row)
