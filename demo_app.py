import streamlit as st
import random

# -- Demo credentials --
DEMO_EMAIL = "demo@cycologie.ca"
DEMO_PASSWORD = "DemoPass123!"

# Generate 30 dummy tracks with random BPMs between 80 and 200
random.seed(42)
DUMMY_TRACKS = [
    {"title": f"Track {i+1}", "bpm": random.randint(80, 200)}
    for i in range(30)
]

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "corrected_tracks" not in st.session_state:
    st.session_state.corrected_tracks = None
if "playlists" not in st.session_state:
    st.session_state.playlists = None

# Login screen
if not st.session_state.logged_in:
    st.title("Demo BPM Sorter Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if email == DEMO_EMAIL and password == DEMO_PASSWORD:
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid credentials. Try demo@cycologie.ca / DemoPass123!")

# Main app UI
else:
    st.title("Demo BPM Sorter (Dummy Data)")
    st.subheader("Your Liked Songs with Raw BPM")
    st.table(DUMMY_TRACKS)

    if st.button("Correct BPMs (Double if < 110)"):
        corrected = []
        for track in DUMMY_TRACKS:
            bpm = track["bpm"]
            corrected_bpm = bpm * 2 if bpm < 110 else bpm
            corrected.append({"title": track["title"], "bpm": corrected_bpm})
        st.session_state.corrected_tracks = corrected
        st.success("Corrected BPMs using doubling rule.")

    if st.session_state.corrected_tracks:
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
            st.session_state.playlists = playlists
            st.success("Tracks sorted into playlists.")

    if st.session_state.playlists:
        for label, tracks in st.session_state.playlists.items():
            st.subheader(f"Playlist: {label}")
            if tracks:
                st.write("\n".join(tracks))
            else:
                st.write("(No tracks matched this range.)")
