import os
import streamlit as st
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import urlparse

# Load credentials from .env
load_dotenv()

# Initialize Spotify client credentials (no user login needed)
client_credentials = SpotifyClientCredentials()
sp = Spotify(auth_manager=client_credentials)

st.title("🎵 BPM Sorter - Public Spotify Playlist")

# Helper: extract playlist ID from URL or ID input
def extract_playlist_id(url_or_id):
    try:
        parsed = urlparse(url_or_id)
        if 'playlist' in parsed.path:
            return parsed.path.split('/')[-1]
    except:
        pass
    return url_or_id

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
        for item in tracks:
            track = item.get('track')
            if not track:
                continue
            title = track.get('name')
            tid = track.get('id')
            track_data.append({'title': title, 'id': tid})

                        # Fetch BPMs one-by-one using the single-track endpoint
        bpm_map = {}
        for t in track_data:
            tid = t['id']
            try:
                feature = sp.audio_features([tid])[0] or {}
                tempo = feature.get('tempo')
                bpm_map[tid] = round(tempo) if tempo else 'N/A'
            except Exception:
                bpm_map[tid] = 'N/A'

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
                    if isinstance(bpm, int):
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

