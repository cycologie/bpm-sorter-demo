import os
import streamlit as st
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import urlparse, parse_qs

# Load credentials from .env
load_dotenv()

# Initialize Spotify client credentials (no user login needed)
client_credentials = SpotifyClientCredentials()
sp = Spotify(auth_manager=client_credentials)

st.title("🎵 BPM Sorter - Public Spotify Playlist")

# Step: Ask for public playlist URL/ID
def extract_playlist_id(url):
    # If full URL, parse path /playlist/{id}
    try:
        parsed = urlparse(url)
        if 'playlist' in parsed.path:
            return parsed.path.split('/')[-1]
    except:
        pass
    return url  # assume user provided ID

playlist_input = st.text_input(
    "Enter a public Spotify playlist URL or ID:",
    placeholder="https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
)

if playlist_input:
    playlist_id = extract_playlist_id(playlist_input)
    try:
        # Fetch playlist tracks
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        tracks.extend(results['items'])
        while results.get('next'):
            results = sp.next(results)
            tracks.extend(results['items'])

        # Prepare track data
        track_data = []
        ids = []
        for item in tracks:
            track = item.get('track')
            if not track:
                continue
            title = track.get('name')
            tid = track.get('id')
            track_data.append({'title': title, 'id': tid})
            ids.append(tid)

        # Fetch BPMs individually to avoid batch 403
        bpm_map = {}
        for tid in ids:
            features = sp.audio_features([tid])[0]
            if features and features.get('tempo'):
                bpm_map[tid] = round(features['tempo'])

        # Display raw tempos
        table = [{'Title': t['title'], 'Raw BPM': bpm_map.get(t['id'], 'N/A')} for t in track_data]
        st.subheader("Tracks and Raw BPM")
        st.table(table)

        # Correct BPMs when clicking button
        if st.button("Correct BPMs (Double if < 110)"):
            corrected = []
            for row in table:
                bpm = row['Raw BPM']
                if bpm == 'N/A':
                    corrected_bpm = 'N/A'
                else:
                    corrected_bpm = bpm * 2 if bpm < 110 else bpm
                corrected.append({'Title': row['Title'], 'Corrected BPM': corrected_bpm})
            st.subheader("Corrected BPMs")
            st.table(corrected)

            # Define ranges and bucket
            st.subheader("Define BPM Ranges and Bucket")
            bucket_ranges = []
            for label, default in [
                ("110-155 Chill Opener", (110, 155)),
                ("156-165", (156, 165)),
                ("166-180", (166, 180)),
                ("181-220", (181, 220))
            ]:
                lo, hi = st.slider(label, 0, 300, default)
                bucket_ranges.append((label, lo, hi))

            if st.button("Bucket Tracks"):
                bmaps = {label: [] for label, _, _ in bucket_ranges}
                for row in corrected:
                    bpm = row['Corrected BPM']
                    if bpm == 'N/A':
                        continue
                    for label, lo, hi in bucket_ranges:
                        if lo <= bpm <= hi:
                            bmaps[label].append(f"{row['Title']} ({bpm} BPM)")
                            break
                # Show buckets
                for label, items in bmaps.items():
                    st.subheader(f"{label}")
                    if items:
                        st.write("\n".join(items))
                    else:
                        st.write("(No tracks)")

    except Exception as e:
        st.error(f"Error fetching playlist or audio features: {e}")
