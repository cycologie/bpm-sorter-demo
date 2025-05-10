import streamlit as st

# Simple Demo BPM Sorter App (No Spotify Integration)
# Save this as demo_app.py and deploy on Streamlit Community Cloud.

# -- Demo credentials --
DEMO_EMAIL = "demo@cycologie.ca"
DEMO_PASSWORD = "DemoPass123!"

# Dummy Liked Songs data
DUMMY_TRACKS = [
    {"title": "Billie Jean", "bpm": 117},
    {"title": "Song A", "bpm": 85},
    {"title": "Song B", "bpm": 160},
]

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

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
    st.subheader("Your Liked Songs with BPM")
    st.table(DUMMY_TRACKS)

    st.subheader("Define BPM Ranges")
    ranges = []
    for label, default in [("110-155 Chill Opener", (110, 155)),
                           ("156-165", (156, 165)),
                           ("166-180", (166, 180)),
                           ("181-220", (181, 220))]:
        lo, hi = st.slider(label, 0, 300, default)
        ranges.append((label, (lo, hi)))

    if st.button("Sync Playlists"):
        # Dummy action
        st.success("Playlists created with your defined ranges!")
        st.info("(This is a demo app with no real Spotify integration.)")

