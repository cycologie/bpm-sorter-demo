import os
import streamlit as st
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from urllib.parse import urlparse, parse_qs

# Load credentials from .env
load_dotenv()

# Set up Spotify auth manually for Streamlit Cloud
scope = "playlist-read-private user-library-read"
sp_oauth = SpotifyOAuth(
    scope=scope,
    redirect_uri="https://bpm-sorter-demo.streamlit.app",
    show_dialog=True
)

st.title("🎵 BPM Sorter - Real Spotify Playlist")

# Step 1: Get auth URL and show login button
auth_url = sp_oauth.get_authorize_url()
st.markdown(f"[Click here to log in with Spotify]({auth_url})")

# Automatically parse ?code=... from URL if present
query_params = st.experimental_get_query_params()
code = query_params.get("code", [None])[0]

if code:
    try:
        token_info = sp_oauth.get_access_token(code, as_dict=True)
        sp = Spotify(auth=token_info["access_token"])

        me = sp.current_user()
        st.markdown(f"**Logged in as:** {me['display_name']} ({me['id']})")

        playlists = sp.current_user_playlists(limit=50)["items"]
        playlist_names = [p["name"] for p in playlists]
        selected_playlist = st.selectbox("Select a playlist to analyze:", playlist_names)

        playlist_id = next(p["id"] for p in playlists if p["name"] == selected_playlist)

        # Get tracks from selected playlist
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        tracks.extend(results["items"])
        while results["next"]:
            results = sp.next(results)
            tracks.extend(results["items"])

        # Extract titles and IDs
        track_data = [{"title": t["track"]["name"], "id": t["track"]["id"]} for t in tracks if t["track"] and t["track"]["id"]]

        # Fetch BPMs immediately
        ids = [t["id"] for t in track_data]
        bpm_map = {}
        for i in range(0, len(ids), 100):
            audio_features = sp.audio_features(ids[i:i+100])
            for f in audio_features:
                if f:
                    bpm_map[f["id"]] = round(f["tempo"])

        # Add BPMs to display
        track_table = []
        for t in track_data:
            bpm = bpm_map.get(t["id"], "N/A")
            track_table.append({"title": t["title"], "bpm": bpm})

        st.subheader("Fetched Tracks with Raw BPM")
        st.table(track_table)

        # Correct BPMs
        if st.button("Correct BPMs (Double if < 110)"):
            ids = [t["id"] for t in track_data if t["id"] is not None]
            corrected_tracks = []
            for i in range(0, len(ids), 100):
                audio_features = sp.audio_features(ids[i:i+100])
                for track, features in zip(track_data[i:i+100], audio_features):
                    if not features:
                        continue
                    bpm = features["tempo"]
                    corrected_bpm = bpm * 2 if bpm < 110 else bpm
                    corrected_tracks.append({
                        "title": track["title"],
                        "bpm": round(corrected_bpm)
                    })
            st.session_state.corrected_tracks = corrected_tracks
            st.success("BPMs corrected!")

        # Show corrected BPMs and sort
        if "corrected_tracks" in st.session_state:
            st.subheader("Corrected BPMs")
            st.table(st.session_state.corrected_tracks)

            st.subheader("Define BPM Ranges")
            bpm_ranges = []
            for label, default in [
                ("110-155 Chill Opener", (110, 155)),
                ("156-165", (156, 165)),
                ("166-180", (166, 180)),
                ("181-220", (181, 220))
            ]:
                lo, hi = st.slider(label, 0, 300, default)
                bpm_ranges.append((label, lo, hi))

            if st.button("Sort Tracks into Playlists"):
                playlists = {label: [] for label, _, _ in bpm_ranges}
                for track in st.session_state.corrected_tracks:
                    bpm = track["bpm"]
                    for label, lo, hi in bpm_ranges:
                        if lo <= bpm <= hi:
                            playlists[label].append(f"{track['title']} ({bpm} BPM)")
                            break
                for label, tracks in playlists.items():
                    st.subheader(f"Playlist: {label}")
                    if tracks:
                        st.write("\n".join(tracks))
                    else:
                        st.write("(No tracks matched this range.)")

    except Exception as e:
        st.error("⚠️ Something went wrong with authentication. Please try logging in again.")
