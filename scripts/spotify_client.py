"""
Spotify Client Script
"""
import logging
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from storage import save_tracks_per_day
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = 'user-read-recently-played'

DATA_DIR = os.getenv('DATA_DIR', os.path.join(os.path.dirname(__file__), '../data'))
TOKEN_CACHE_PATH = os.getenv('TOKEN_CACHE_PATH', os.path.join(os.path.dirname(__file__)))

def ms_to_min_sec(ms):
    """
    Transform milliseconds to a string in the format "MM:SS".
    """
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    return f"{minutes}:{str(seconds).zfill(2)}"

def get_recent_tracks(return_data=False):
    """
    Fetch recent tracks from Spotify and save them to daily CSV files.
    """
    logging.info("Starting get_recent_tracks")
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=TOKEN_CACHE_PATH
    ))

    logging.info("Fetching recent tracks from Spotify API")
    results = sp.current_user_recently_played(limit=50)
    tracks = results['items']

    track_data = []
    for idx, item in enumerate(tracks):
        track = item['track']
        artists = ", ".join([artist['name'] for artist in track['artists']])
        played_at = item['played_at']
        duration = ms_to_min_sec(track['duration_ms'])
        track_data.append({
            'index': idx+1,
            'name': track['name'],
            'artists': artists,
            'duration': duration,
            'played_at': played_at,
            'id': track['id']
        })
    logging.info("Fetched %d tracks", len(track_data))

    logging.info("Saving tracks per day")
    save_tracks_per_day(track_data, os.path.abspath(DATA_DIR))

    if return_data:
        logging.info("Returning track data")
        return track_data
    for row in track_data:
        print(f"{row['index']}. {row['name']} - {row['artists']} [{row['duration']}] ({row['played_at']})")
    logging.info("Finished get_recent_tracks")

if __name__ == "__main__":
    get_recent_tracks()
