import streamlit as st

st.set_page_config(page_title="Unfiltered AI Generator", layout="wide", page_icon="🎨")

# Custom CSS for Spotify-inspired theme (orange/yellow)
st.markdown("""
<style>
    body {
        background-color: #121212;
        color: #f0f0f0;
    }
    .main {
        background-color: #121212;
    }
    h1, h2, h3, h4, h5 {
        color: #FFB800;
    }
    .card {
        background-color: #1e1e1e;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 4px 20px rgba(255, 184, 0, 0.1);
        transition: 0.3s ease;
    }
    .card:hover {
        box-shadow: 0 6px 24px rgba(255, 184, 0, 0.2);
        transform: translateY(-4px);
    }
    .highlight {
        color: #FFA500;
        font-weight: 600;
    }
    .stButton>button {
        background-color: #FFA500;
        color: #000000;
        border: none;
        padding: 12px 28px;
        border-radius: 999px;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FFB800;
        color: black;
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# Main title and subtext
st.markdown("""
<h1>🎨 Unfiltered AI Image Generator</h1>
<h3>Create anything. No filters. No watermarks. No limits.</h3>
""", unsafe_allow_html=True)

# Layout cards in columns
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <h4>🔓 No Censorship</h4>
        <p>MidJourney said <span class="highlight">no</span> — we said <span class="highlight">go</span>. Explore prompts others block.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h4>🎯 No Watermarks</h4>
        <p>Your image is 100% yours. No overlays, tags, or distractions. Pure output every time.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <h4>⚡ High Quality, Fast</h4>
        <p>Instant generation with high-res files. No paywall for quality.</p>
    </div>
    """, unsafe_allow_html=True)


st.markdown("""
<br><br>
<center>
    <a href="/imagegen">
        <button>✨ Launch the Generator</button>
    </a>
</center>
""", unsafe_allow_html=True)


st.markdown("""
<br><br>
---
<center style="color: #666; font-size: 0.9em">
Built with ❤️ using Ideogram API · Not affiliated with Ideogram · Streamlit powered
</center>
""", unsafe_allow_html=True)


