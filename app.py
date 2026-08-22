import streamlit as st
import os
import io
import random
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFilter
import requests

load_dotenv()

# --- Page config (must be first Streamlit call) ---
st.set_page_config(
    page_title="immer: accent-aware podcast discovery",
    page_icon="🎧",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Spotify-themed CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Global */
.stApp {
    background-color: #121212;
    color: #FFFFFF;
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}

/* Custom header */
.immer-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
}
.immer-logo {
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: #1DB954;
    margin-bottom: 0.2rem;
}
.immer-tagline {
    font-size: 1.05rem;
    color: #B3B3B3;
    font-weight: 400;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.5;
}

/* Cards */
.spotify-card {
    background: #181818;
    border-radius: 8px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
    transition: background 0.2s;
}
.spotify-card:hover {
    background: #282828;
}

/* Candidate results */
.candidate-row {
    background: #181818;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.candidate-title {
    color: #FFFFFF;
    font-weight: 500;
    font-size: 0.95rem;
    flex: 1;
    margin-right: 1rem;
}
.badge-british {
    background: #1DB954;
    color: #000000;
    padding: 0.25rem 0.75rem;
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: 600;
    white-space: nowrap;
}
.badge-not-british {
    background: #404040;
    color: #B3B3B3;
    padding: 0.25rem 0.75rem;
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: 600;
    white-space: nowrap;
}

/* Selected pick */
.selected-card {
    background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%);
    border-radius: 8px;
    padding: 1.2rem 1.4rem;
    margin-top: 1rem;
    color: #000000;
}
.selected-title {
    font-weight: 700;
    font-size: 1.1rem;
    margin-bottom: 0.3rem;
}
.selected-sub {
    font-weight: 400;
    font-size: 0.9rem;
    opacity: 0.8;
}

/* Playlist items */
.playlist-item {
    color: #B3B3B3;
    font-size: 0.9rem;
    padding: 0.4rem 0;
    border-bottom: 1px solid #282828;
}
.playlist-item:last-child {
    border-bottom: none;
}

/* Section headers */
.section-header {
    color: #FFFFFF;
    font-size: 1.3rem;
    font-weight: 700;
    margin: 1.5rem 0 0.8rem 0;
    letter-spacing: -0.02em;
}

/* Subtitle text */
.muted {
    color: #B3B3B3;
    font-size: 0.85rem;
}

/* Text input styling */
.stTextInput > div > div > input {
    background-color: #282828 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.7rem 1.2rem !important;
    font-family: 'Inter', sans-serif !important;
    outline: none !important;
    box-shadow: none !important;
}
.stTextInput > div > div > input::placeholder {
    color: #727272 !important;
}
.stTextInput > div > div > input:focus,
.stTextInput > div > div > input:focus-visible {
    outline: none !important;
    box-shadow: 0 0 0 2px #1DB954 !important;
}

/* Selectbox styling */
.stSelectbox [data-baseweb="select"] > div {
    background-color: #282828 !important;
    border: none !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    outline: none !important;
    box-shadow: none !important;
    transition: box-shadow 0.2s ease;
}
.stSelectbox [data-baseweb="select"] > div:hover {
    border: none !important;
    box-shadow: 0 0 0 1px #1DB954 !important;
    cursor: pointer;
}
.stSelectbox [data-baseweb="select"] > div:focus,
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stSelectbox [data-baseweb="select"] > div:focus-visible {
    outline: none !important;
    box-shadow: 0 0 0 2px #1DB954 !important;
    border: none !important;
}
/* Selectbox dropdown list */
[data-baseweb="popover"] {
    background-color: #282828 !important;
}
[data-baseweb="menu"] {
    background-color: #282828 !important;
}
[data-baseweb="menu"] li,
[data-baseweb="menu"] [role="option"] {
    background-color: #282828 !important;
    color: #FFFFFF !important;
}
[data-baseweb="menu"] li:hover,
[data-baseweb="menu"] [role="option"]:hover,
[data-baseweb="menu"] [aria-selected="true"] {
    background-color: #1DB954 !important;
    color: #000000 !important;
}

/* Button styling (all buttons) */
.stButton > button {
    background-color: #1DB954 !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s !important;
    width: auto !important;
}
.stButton > button:hover {
    background-color: #1ed760 !important;
    transform: scale(1.04);
}

/* Share immer button: "immer" label, "Share " prefix slides in on hover */
.share-btn-wrap .stButton > button {
    position: relative !important;
    overflow: hidden !important;
    transition: padding-left 0.3s ease, background-color 0.2s ease !important;
}
.share-btn-wrap .stButton > button::before {
    content: 'Share\00a0';
    position: absolute;
    left: -4rem;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0;
    font-weight: 700;
    font-size: 0.95rem;
    color: #000000;
    transition: left 0.3s ease, opacity 0.25s ease;
    pointer-events: none;
    white-space: nowrap;
}
.share-btn-wrap .stButton > button:hover {
    padding-left: 4.5rem !important;
    background-color: #1ed760 !important;
    transform: scale(1.04);
}
.share-btn-wrap .stButton > button:hover::before {
    left: 1.1rem;
    opacity: 1;
}

/* Spinner */
.stSpinner > div {
    border-top-color: #1DB954 !important;
}

/* Divider */
hr {
    border-color: #282828 !important;
}
</style>
""", unsafe_allow_html=True)


# --- Clients (after dotenv loads) ---
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from openai import OpenAI
from tavily import TavilyClient
import fal_client

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="playlist-read-private playlist-modify-private playlist-modify-public",
    open_browser=True
))

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# --- Helper functions ---

def get_user_playlists():
    current_user_id = sp.current_user().get("id", "")
    playlists = []
    offset = 0
    while True:
        results = sp.current_user_playlists(limit=50, offset=offset)
        for pl in results.get("items", []):
            if pl.get("owner", {}).get("id") == current_user_id:
                playlists.append({
                    "id": pl.get("id", ""),
                    "name": pl.get("name", "Unknown Playlist"),
                })
        if results.get("next") is None:
            break
        offset += 50
    return playlists


def find_shows_via_tavily(topic):
    try:
        results = tavily_client.search(
            f"{topic} British podcast show",
            max_results=5,
            search_depth="basic"
        )
        show_names = []
        for r in results.get("results", []):
            title = r.get("title", "")
            if title:
                name = title.split("|")[0].split(" - ")[0].strip()
                if name:
                    show_names.append(name)
        return list(dict.fromkeys(show_names))[:5]
    except Exception:
        return []


def _parse_episode(ep):
    return {
        "name": ep.get("name", "Unknown"),
        "description": ep.get("description", ""),
        "uri": ep.get("uri", ""),
        "show": ep.get("show", {}).get("name", "Unknown show"),
    }


def search_episodes(query, limit=6, extra_queries=None):
    results = sp.search(q=query, type="episode", limit=limit)
    candidates = []
    seen_uris = set()

    for ep in results.get("episodes", {}).get("items", []):
        uri = ep.get("uri", "")
        if uri and uri not in seen_uris:
            seen_uris.add(uri)
            candidates.append(_parse_episode(ep))

    tavily_added = 0
    if extra_queries:
        for show_name in extra_queries:
            try:
                r2 = sp.search(q=show_name, type="episode", limit=2)
                for ep in r2.get("episodes", {}).get("items", []):
                    uri = ep.get("uri", "")
                    if uri and uri not in seen_uris:
                        seen_uris.add(uri)
                        candidates.append(_parse_episode(ep))
                        tavily_added += 1
            except Exception:
                continue

    return candidates, tavily_added


def classify_accent(title, description):
    prompt = f"""You are classifying podcast content for accent/variant, not just language.

Episode title: {title}
Episode description: {description}

Is this podcast genuinely British-accented content (British hosts, British production,
British cultural context), as opposed to American, Australian, Irish, Canadian, or
generically "English" content that is not specifically British?

Respond with ONLY one word: "british" or "not_british" """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=5
    )
    label = response.choices[0].message.content.strip().lower()
    if label not in ("british", "not_british"):
        label = "not_british"
    return label


def add_to_playlist(playlist_id, uri):
    result = sp.playlist_add_items(playlist_id, [uri])
    return result.get("snapshot_id", "")


def read_playlist(playlist_id, limit=10):
    results = sp.playlist_items(playlist_id, limit=limit)
    items = []
    for entry in results.get("items", []):
        content = entry.get("track")
        if content is None:
            content = entry.get("item")
        if content is None:
            continue
        name = content.get("name", "Unknown")
        if content.get("type") == "episode":
            creator = content.get("show", {}).get("name", "Unknown show")
        elif content.get("artists"):
            creator = ", ".join(a.get("name", "Unknown") for a in content.get("artists", []))
        else:
            creator = "Unknown"
        items.append((name, creator))
    return items


def get_playlist_cover_urls(playlist_id, limit=14):
    results = sp.playlist_items(playlist_id, limit=limit)
    urls = []
    for entry in results.get("items", []):
        content = entry.get("track") or entry.get("item")
        if content is None:
            continue
        images = content.get("images") or content.get("album", {}).get("images", [])
        if images:
            url = images[0].get("url")
            if url:
                urls.append(url)
    return urls


def _fallback_bg(size):
    bg = Image.new("RGB", size, (18, 18, 18))
    draw = ImageDraw.Draw(bg)
    for i in range(0, size[0], 40):
        for j in range(0, size[1], 40):
            shade = random.randint(20, 38)
            draw.rectangle([i, j, i + 20, j + 20], fill=(shade, shade, shade))
    return bg.convert("RGBA")


def _paste_rgba(canvas, layer, pos):
    x, y = pos
    cw, ch = canvas.size
    lw, lh = layer.size
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(cw, x + lw), min(ch, y + lh)
    if x1 <= x0 or y1 <= y0:
        return
    region = layer.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    bg_region = canvas.crop((x0, y0, x1, y1)).convert("RGBA")
    composited = Image.alpha_composite(bg_region, region.convert("RGBA"))
    canvas.paste(composited, (x0, y0))


def generate_fal_background(width=800, height=800):
    try:
        result = fal_client.subscribe(
            "fal-ai/flux/schnell",
            arguments={
                "prompt": (
                    "90s indie zine sticker-bomb abstract background, bright halftone dots, "
                    "scratchy grain texture, hand-drawn doodle marks, messy collage paper texture, "
                    "no text, no real objects, abstract art, vibrant colors, psychedelic, "
                    "deliberately messy, punk aesthetic"
                ),
                "image_size": {"width": width, "height": height},
                "num_inference_steps": 4,
                "num_images": 1,
            }
        )
        return result["images"][0]["url"]
    except Exception:
        return None


def make_collage(bg_url, cover_urls, canvas_size=(800, 800)):
    if bg_url:
        try:
            r = requests.get(bg_url, timeout=15)
            bg = Image.open(io.BytesIO(r.content)).convert("RGBA").resize(canvas_size, Image.LANCZOS)
        except Exception:
            bg = _fallback_bg(canvas_size)
    else:
        bg = _fallback_bg(canvas_size)

    canvas = bg.copy()

    COVER = 150
    PAD = 10
    BOTTOM_PAD = 28

    for url in cover_urls:
        try:
            r = requests.get(url, timeout=8)
            cover = Image.open(io.BytesIO(r.content)).convert("RGBA").resize(
                (COVER, COVER), Image.LANCZOS
            )
        except Exception:
            continue

        pw = COVER + PAD * 2
        ph = COVER + PAD + BOTTOM_PAD

        pol = Image.new("RGBA", (pw, ph), (255, 255, 255, 255))
        pol.paste(cover, (PAD, PAD))

        angle = random.uniform(-20, 20)
        pol_rot = pol.rotate(angle, expand=True, resample=Image.BICUBIC)

        shadow_src = Image.new("RGBA", (pw, ph), (0, 0, 0, 110))
        shadow_rot = shadow_src.rotate(angle, expand=True, resample=Image.BICUBIC)
        shadow_rot = shadow_rot.filter(ImageFilter.GaussianBlur(7))

        rw, rh = pol_rot.size
        x = random.randint(-rw // 4, canvas_size[0] - rw * 3 // 4)
        y = random.randint(-rh // 4, canvas_size[1] - rh * 3 // 4)

        _paste_rgba(canvas, shadow_rot, (x + 8, y + 8))
        _paste_rgba(canvas, pol_rot, (x, y))

    return canvas.convert("RGB")


# ── UI ────────────────────────────────────────────────────────────────────────

# --- Header ---
st.markdown("""
<div class="immer-header">
    <div class="immer-logo">🎧 immer</div>
    <div class="immer-tagline">
        Accent-aware podcast discovery for your Spotify.
        Finds genuinely British content buried under platform defaults.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- Playlist selector ---
user_playlists = get_user_playlists()
playlist_name_to_id = {pl["name"]: pl["id"] for pl in user_playlists}
playlist_names = [pl["name"] for pl in user_playlists]

selected_name = st.selectbox("Choose a playlist", playlist_names)
target_playlist_id = playlist_name_to_id.get(selected_name, "")
st.session_state["selected_playlist_id"] = target_playlist_id

st.markdown("---")

# --- Current playlist preview ---
st.markdown('<div class="section-header">Your target playlist</div>', unsafe_allow_html=True)

playlist_info = sp.playlist(target_playlist_id, fields="name,images,tracks.total")
playlist_name = playlist_info.get("name", "Unknown Playlist")
total_tracks = playlist_info.get("tracks", {}).get("total", "?")
cover_url = playlist_info.get("images", [{}])[0].get("url")

if cover_url:
    st.image(cover_url, width=120)

st.markdown(f"""
<div class="spotify-card">
    <div style="font-weight:700; font-size:1.1rem;">📋 {playlist_name}</div>
    <div class="muted">{total_tracks} episodes</div>
</div>
""", unsafe_allow_html=True)

with st.expander("Preview current episodes"):
    items = read_playlist(target_playlist_id, limit=5)
    for name, creator in items:
        st.markdown(
            f'<div class="playlist-item">🎙️ {name}, <span class="muted">{creator}</span></div>',
            unsafe_allow_html=True
        )

st.markdown("---")

# --- Search + agent loop ---
st.markdown('<div class="section-header">Find British content</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="muted">Search for a genre or topic. immer will find genuinely British-accented '
    'episodes and add the best match to your playlist.</div>',
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)

query = st.text_input(
    "", placeholder="e.g. British comedy podcast, history, true crime...",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    run_button = st.button("🔍  Discover", use_container_width=True)

if run_button and query:
    st.markdown("---")
    st.markdown('<div class="section-header">Scanning candidates</div>', unsafe_allow_html=True)

    with st.spinner("Finding British shows via Tavily..."):
        tavily_shows = find_shows_via_tavily(query)

    with st.spinner("Searching Spotify..."):
        candidates, tavily_added = search_episodes(query, limit=6, extra_queries=tavily_shows)

    if tavily_shows:
        st.markdown(
            f'<div class="muted">Tavily surfaced {len(tavily_shows)} additional shows'
            f'{f", adding {tavily_added} new episodes" if tavily_added else ""}.</div>',
            unsafe_allow_html=True
        )

    if not candidates:
        st.warning("No episodes found for that query. Try a different search.")
    else:
        st.markdown(
            f'<div class="muted">{len(candidates)} candidates found. Classifying each...</div>',
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)

        best_match = None
        british_count = 0
        results_container = st.container()

        for ep in candidates:
            with st.spinner(f"Classifying: {ep['name'][:50]}..."):
                label = classify_accent(ep["name"], ep["description"])

            if label == "british":
                badge = '<span class="badge-british">British</span>'
                british_count += 1
                if best_match is None:
                    best_match = ep
            else:
                badge = '<span class="badge-not-british">Not British</span>'

            title_display = ep["name"][:65] + ("..." if len(ep["name"]) > 65 else "")

            results_container.markdown(f"""
            <div class="candidate-row">
                <span class="candidate-title">{title_display}</span>
                {badge}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        if best_match and british_count > 1:
            others = british_count - 1
            word = "match" if others == 1 else "matches"
            st.markdown(
                f'<div class="muted">Added the top match. {others} other British {word} '
                f'were also found this search.</div>',
                unsafe_allow_html=True
            )

        if best_match:
            st.markdown(
                '<div class="section-header">Inserting into your playlist</div>',
                unsafe_allow_html=True
            )

            with st.spinner("Adding to playlist..."):
                snapshot_id = add_to_playlist(target_playlist_id, best_match["uri"])

            st.markdown(f"""
            <div class="selected-card">
                <div class="selected-title">✅ Added: {best_match['name']}</div>
                <div class="selected-sub">Inserted into "{playlist_name}". Check your Spotify app.</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f'<div class="muted" style="text-align:center;">'
                f'<a href="https://open.spotify.com/playlist/{target_playlist_id}" '
                f'target="_blank" style="color:#1DB954; text-decoration:none; font-weight:600;">'
                f'Open playlist in Spotify ↗</a></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown("""
            <div class="spotify-card">
                <div style="font-weight:600;">No genuinely British content found</div>
                <div class="muted">Try a more specific query, e.g. "British history podcast" or "BBC comedy"</div>
            </div>
            """, unsafe_allow_html=True)

elif run_button and not query:
    st.warning("Enter a search query first.")

# --- Share immer collage ---
st.markdown("---")
st.markdown('<div class="section-header">Share</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="muted">Generate a shareable collage: fal-generated background with your '
    'playlist cover art scattered on top.</div>',
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    st.markdown('<div class="share-btn-wrap">', unsafe_allow_html=True)
    share_clicked = st.button("immer", key="share_btn", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

if share_clicked:
    fal_warning = None

    with st.spinner("Generating background via fal..."):
        bg_url = generate_fal_background()

    if bg_url is None:
        fal_warning = "fal generation failed. Using a plain dark background instead."

    with st.spinner("Fetching playlist cover art..."):
        cover_urls = get_playlist_cover_urls(target_playlist_id, limit=14)

    with st.spinner("Compositing collage..."):
        collage = make_collage(bg_url, cover_urls)

    if fal_warning:
        st.warning(fal_warning)

    st.image(collage, caption=f"immer collage for {playlist_name}", use_container_width=True)

    buf = io.BytesIO()
    collage.save(buf, format="PNG")
    buf.seek(0)

    st.download_button(
        label="Download collage",
        data=buf,
        file_name="immer_collage.png",
        mime="image/png",
    )

# --- Footer ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; padding: 1rem 0;">
    <div class="muted">
        Built for {Tech: Europe} x VEED Hackathon. Powered by Spotify Web API, OpenAI, and Pioneer.
    </div>
</div>
""", unsafe_allow_html=True)
