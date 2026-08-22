import streamlit as st
import streamlit.components.v1 as components
import os
import io
import random
import base64
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import requests
import fal_client

load_dotenv()

# --- Page config (must be first Streamlit call) ---
st.set_page_config(
    page_title="immer: accent-aware podcast discovery",
    page_icon="🎧",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Ambient background ────────────────────────────────────────────────────────
_BG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "background.png")

def _ensure_background():
    if os.path.exists(_BG_PATH):
        return
    try:
        result = fal_client.subscribe(
            "fal-ai/flux/schnell",
            arguments={
                "prompt": (
                    "dark atmospheric abstract background art, near-black charcoal base colour, "
                    "soft glowing blurred gradients of muted deep purple and teal and forest green, "
                    "very low opacity ambient light bleeding through like coloured stage lighting in fog, "
                    "no text, no objects, no faces, no logos, cinematic dark texture, "
                    "moody ambient, luma.com event page aesthetic, subtle grain"
                ),
                "image_size": {"width": 1280, "height": 720},
                "num_inference_steps": 4,
                "num_images": 1,
            },
        )
        r = requests.get(result["images"][0]["url"], timeout=15)
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        img = img.resize((1280, 720), Image.LANCZOS)
        img.save(_BG_PATH, "PNG", optimize=True)
    except Exception:
        # Fallback: dark gradient placeholder
        img = Image.new("RGB", (1280, 720), (10, 10, 16))
        img.save(_BG_PATH, "PNG")

def _bg_b64():
    with open(_BG_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode()

@st.cache_resource(show_spinner="Preparing ambient background...")
def _load_bg_b64():
    _ensure_background()
    return _bg_b64()

_BG = _load_bg_b64()

st.markdown(f"""<style>
.stApp {{
    background-image:
        linear-gradient(rgba(0,0,0,0.42), rgba(0,0,0,0.42)),
        url('data:image/png;base64,{_BG}');
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
}}
</style>""", unsafe_allow_html=True)

# --- CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Global ─────────────────────────────────────── */
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

/* ── Scorched-earth: kill ALL red focus outlines ── */
/* Step 1: remove every focus outline globally */
* { outline: none !important; outline-color: #1DB954 !important; }
*:focus { outline: none !important; box-shadow: none !important; }
*:focus-visible { outline: none !important; }
*:active { outline: none !important; }

/* Nuclear: override [data-baseweb] inline styles */
[data-baseweb] *, [data-baseweb] *:focus,
[data-baseweb] *:focus-within, [data-baseweb] *:focus-visible {
    outline: none !important;
    outline-color: #1DB954 !important;
}
[data-baseweb="select"] > div,
[data-baseweb="select"] > div > div,
[data-baseweb="select"] div[class] {
    border-color: #404040 !important;
    box-shadow: none !important;
}
[data-baseweb="select"] > div:focus-within,
[data-baseweb="select"] div[class]:focus-within {
    border-color: #1DB954 !important;
    box-shadow: 0 0 0 2px #1DB954 !important;
}

/* Step 2: suppress browser validation red */
input:invalid, select:invalid, textarea:invalid {
    box-shadow: none !important;
    border-color: #404040 !important;
}

/* Step 3: default state for all input-like elements */
[data-baseweb="input"],
[data-baseweb="input"] > div,
[data-baseweb="input"] input,
[data-baseweb="select"] > div,
[data-baseweb="textarea"],
[data-baseweb="textarea"] textarea,
.stTextInput > div > div,
.stTextInput > div > div > input,
.stSelectbox [data-baseweb="select"] > div {
    outline: none !important;
    box-shadow: none !important;
    border: 1px solid #404040 !important;
    border-color: #404040 !important;
}

/* Step 4: focus states — green only */
[data-baseweb="input"]:focus-within,
[data-baseweb="input"] > div:focus-within,
[data-baseweb="input"] input:focus,
[data-baseweb="input"] input:focus-visible,
[data-baseweb="select"] > div:focus,
[data-baseweb="select"] > div:focus-within,
[data-baseweb="select"] > div:focus-visible,
[data-baseweb="textarea"]:focus-within,
[data-baseweb="textarea"] textarea:focus,
.stTextInput > div > div:focus-within,
.stSelectbox [data-baseweb="select"] > div:focus,
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stSelectbox [data-baseweb="select"] > div:focus-visible {
    outline: none !important;
    border-color: #1DB954 !important;
    box-shadow: 0 0 0 2px #1DB954 !important;
}

/* Step 5: hover states */
[data-baseweb="select"] > div:hover,
.stSelectbox [data-baseweb="select"] > div:hover {
    border-color: #1DB954 !important;
    box-shadow: 0 0 0 1px #1DB954 !important;
    cursor: pointer;
}

/* ── Text input ──────────────────────────────────── */
.stTextInput > div > div > input {
    background-color: #282828 !important;
    color: #FFFFFF !important;
    border-radius: 50px !important;
    padding: 0.7rem 1.2rem !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input::placeholder {
    color: #727272 !important;
}

/* ── Selectbox ───────────────────────────────────── */
.stSelectbox [data-baseweb="select"] > div {
    background-color: #282828 !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
}
[data-baseweb="popover"],
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

/* ── Header ──────────────────────────────────────── */
.immer-header { text-align: center; padding: 2rem 0 1rem 0; }
.immer-logo {
    font-size: 2.8rem; font-weight: 800; letter-spacing: -0.04em;
    color: #1DB954; margin-bottom: 0.2rem;
}
.immer-tagline {
    font-size: 1.05rem; color: #B3B3B3; font-weight: 400;
    max-width: 500px; margin: 0 auto; line-height: 1.5;
}

/* ── Cards ───────────────────────────────────────── */
.spotify-card {
    background: #181818; border-radius: 8px;
    padding: 1.2rem 1.4rem; margin-bottom: 0.8rem; transition: background 0.2s;
}
.spotify-card:hover { background: #282828; }

/* ── Candidate rows ──────────────────────────────── */
.candidate-row {
    background: #181818; border-radius: 8px; padding: 1rem 1.2rem;
    margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;
}
.candidate-title {
    color: #FFFFFF; font-weight: 500; font-size: 0.95rem;
    flex: 1; margin-right: 1rem;
}
.badge-british {
    background: #1DB954; color: #000000; padding: 0.25rem 0.75rem;
    border-radius: 50px; font-size: 0.8rem; font-weight: 600; white-space: nowrap;
}

/* ── Selected card ───────────────────────────────── */
.selected-card {
    background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%);
    border-radius: 8px; padding: 1.2rem 1.4rem; margin-top: 1rem; color: #000000;
}
.selected-title { font-weight: 700; font-size: 1.1rem; margin-bottom: 0.3rem; }
.selected-sub { font-weight: 400; font-size: 0.9rem; opacity: 0.8; }

/* ── Playlist items ──────────────────────────────── */
.playlist-item {
    color: #B3B3B3; font-size: 0.9rem;
    padding: 0.4rem 0; border-bottom: 1px solid #282828;
}
.playlist-item:last-child { border-bottom: none; }

/* ── Section headers / utility ───────────────────── */
.section-header {
    color: #FFFFFF; font-size: 1.3rem; font-weight: 700;
    margin: 1.5rem 0 0.8rem 0; letter-spacing: -0.02em;
}
.muted { color: #B3B3B3; font-size: 0.85rem; }

/* ── Buttons (all) ───────────────────────────────── */
.stButton > button {
    background: #1DB954 !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: 0.02em !important;
    transition: transform 0.2s, background 0.2s !important;
    width: auto !important;
    white-space: nowrap !important;
}
.stButton > button:hover {
    background: #1ed760 !important;
    transform: scale(1.04);
}
.stButton > button:disabled {
    background: #282828 !important;
    color: #B3B3B3 !important;
    cursor: default !important;
    transform: none !important;
}

/* ── Share button: a self-contained, slow background shimmer ───────────── */
@keyframes share-shimmer {
    from { background-position: 200% 0, 0 0; }
    to   { background-position: -200% 0, 0 0; }
}

/* Streamlit adds st-key-share_btn to the keyed widget wrapper. */
.st-key-share_btn {
    display: flex;
    justify-content: center;
}
.st-key-share_btn button {
    position: relative !important;
    overflow: hidden !important;
    width: 8.5rem !important;
    min-width: 8.5rem !important;
    padding: 0.6rem 1rem !important;
    border-radius: 50px !important;
    background-color: #1DB954 !important;
    background-image:
        linear-gradient(110deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.12) 45%, rgba(255,255,255,0.12) 55%, rgba(255,255,255,0) 100%),
        linear-gradient(#1DB954, #1DB954) !important;
    background-size: 200% 100%, 100% 100% !important;
    background-repeat: no-repeat !important;
    animation: share-shimmer 5s linear infinite !important;
    transition: width 260ms ease, min-width 260ms ease, background-color 200ms ease !important;
    transform: none !important;
}
.st-key-share_btn button > div,
.st-key-share_btn button p {
    font-size: 0 !important;
    line-height: 1 !important;
}
.st-key-share_btn button::after {
    content: "shimmer";
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    color: #000000;
    font: 700 0.95rem/1 'Inter', sans-serif;
    letter-spacing: 0.02em;
    white-space: nowrap;
    pointer-events: none;
}
.st-key-share_btn button:hover {
    width: 10.75rem !important;
    min-width: 10.75rem !important;
    background-color: #1ed760 !important;
    transform: none !important;
}
.st-key-share_btn button:hover::after {
    content: "share immer";
}


/* ── Spinner / Divider ───────────────────────────── */
.stSpinner > div { border-top-color: #1DB954 !important; }
hr { border-color: #282828 !important; }
</style>
""", unsafe_allow_html=True)


# ── MutationObserver: strip any dynamically-injected red borders ──────────────
st.markdown(r"""
<script>
(function() {
  function fixEl(el) {
    if (!el || !el.style) return;
    var s = el.getAttribute('style') || '';
    if (/red|#[eE][0-9a-fA-F]{4}[0-9a-fA-F]{0,1}|rgb\s*\(\s*2[0-9]{2}\s*,\s*[0-5]/.test(s)) {
      el.style.setProperty('border-color', '#1DB954', 'important');
      el.style.setProperty('box-shadow', '0 0 0 2px #1DB954', 'important');
      el.style.setProperty('outline', 'none', 'important');
    }
  }
  function scanAll() {
    document.querySelectorAll('[style]').forEach(fixEl);
  }
  var obs = new MutationObserver(function(ms) {
    ms.forEach(function(m) {
      if (m.type === 'attributes') fixEl(m.target);
      if (m.type === 'childList') { m.addedNodes.forEach(function(n) {
        if (n.nodeType === 1) { fixEl(n); n.querySelectorAll && n.querySelectorAll('[style]').forEach(fixEl); }
      }); }
    });
  });
  if (document.body) obs.observe(document.body, {attributes: true, attributeFilter: ['style'], subtree: true, childList: true});
  else document.addEventListener('DOMContentLoaded', function() {
    obs.observe(document.body, {attributes: true, attributeFilter: ['style'], subtree: true, childList: true});
  });
  scanAll();
})();
</script>
""", unsafe_allow_html=True)

# ── Clients ───────────────────────────────────────────────────────────────────
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from openai import OpenAI
from tavily import TavilyClient

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="playlist-read-private playlist-modify-private playlist-modify-public",
    open_browser=True
))

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# ── Helper functions ──────────────────────────────────────────────────────────

def get_user_playlists():
    current_user_id = sp.current_user().get("id", "")
    playlists = []
    offset = 0
    while True:
        results = sp.current_user_playlists(limit=50, offset=offset)
        for pl in results.get("items", []):
            if pl.get("owner", {}).get("id") == current_user_id:
                playlists.append({"id": pl.get("id", ""), "name": pl.get("name", "Unknown Playlist")})
        if results.get("next") is None:
            break
        offset += 50
    return playlists


def find_shows_via_tavily(topic):
    try:
        results = tavily_client.search(f"{topic} British podcast show", max_results=5, search_depth="basic")
        names = []
        for r in results.get("results", []):
            title = r.get("title", "")
            if title:
                name = title.split("|")[0].split(" - ")[0].strip()
                if name:
                    names.append(name)
        return list(dict.fromkeys(names))[:5]
    except Exception:
        return []


def _parse_episode(ep):
    return {
        "name": ep.get("name", "Unknown"),
        "description": ep.get("description", ""),
        "uri": ep.get("uri", ""),
        "show": ep.get("show", {}).get("name", "Unknown show"),
        "audio_preview_url": ep.get("audio_preview_url"),
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
    return label if label in ("british", "not_british") else "not_british"


def add_to_playlist(playlist_id, uri):
    result = sp.playlist_add_items(playlist_id, [uri])
    return result.get("snapshot_id", "")


def read_playlist(playlist_id, limit=5):
    results = sp.playlist_items(playlist_id, limit=limit)
    items = []
    for entry in results.get("items", []):
        content = entry.get("track") or entry.get("item")
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


def _get_font(size=18):
    for path in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


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
    region = layer.crop((x0 - x, y0 - y, x1 - x, y1 - y)).convert("RGBA")
    bg_region = canvas.crop((x0, y0, x1, y1)).convert("RGBA")
    canvas.paste(Image.alpha_composite(bg_region, region), (x0, y0))


def generate_fal_background(width=800, height=800):
    try:
        result = fal_client.subscribe(
            "fal-ai/flux/schnell",
            arguments={
                "prompt": (
                    "90s indie zine sticker-bomb abstract background, bright halftone dots, "
                    "scratchy grain texture, hand-drawn doodle marks, messy collage paper texture, "
                    "absolutely no text, no words, no letters, no numbers, no writing of any kind, "
                    "no real objects, abstract art, vibrant colors, psychedelic, "
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


def make_collage(bg_url, cover_urls, playlist_id, canvas_size=(800, 800)):
    # Background
    if bg_url:
        try:
            r = requests.get(bg_url, timeout=15)
            bg = Image.open(io.BytesIO(r.content)).convert("RGBA").resize(canvas_size, Image.LANCZOS)
        except Exception:
            bg = _fallback_bg(canvas_size)
    else:
        bg = _fallback_bg(canvas_size)

    canvas = bg.copy()

    COVER, PAD, BOTTOM_PAD = 150, 10, 28

    for url in cover_urls:
        try:
            r = requests.get(url, timeout=8)
            cover = Image.open(io.BytesIO(r.content)).convert("RGBA").resize(
                (COVER, COVER), Image.LANCZOS
            )
        except Exception:
            continue

        pw, ph = COVER + PAD * 2, COVER + PAD + BOTTOM_PAD
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

    # Spotify scan code — 400px wide, upper-centre of canvas
    try:
        scan_url = (
            f"https://scannables.scdn.co/uri/plain/png/000000/white/640/"
            f"spotify:playlist:{playlist_id}"
        )
        r = requests.get(scan_url, timeout=10)
        scan = Image.open(io.BytesIO(r.content)).convert("RGBA")
        target_w = 400
        ratio = target_w / scan.width
        scan = scan.resize((target_w, int(scan.height * ratio)), Image.LANCZOS)
        sx = (canvas_size[0] - target_w) // 2
        sy = int(canvas_size[1] * 0.18)
        _paste_rgba(canvas, scan, (sx, sy))
    except Exception:
        pass

    # "immer" watermark — bottom-right, subtle
    try:
        font = _get_font(18)
        overlay = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        text = "immer"
        bbox = d.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(
            (canvas_size[0] - tw - 16, canvas_size[1] - th - 16),
            text, font=font, fill=(255, 255, 255, 150)
        )
        canvas = Image.alpha_composite(canvas, overlay)
    except Exception:
        pass

    return canvas.convert("RGB")




# ── Session state init ────────────────────────────────────────────────────────
if "candidates" not in st.session_state:
    st.session_state["candidates"] = []
if "added_uris" not in st.session_state:
    st.session_state["added_uris"] = set()
if "tavily_info" not in st.session_state:
    st.session_state["tavily_info"] = None


# ── UI ────────────────────────────────────────────────────────────────────────

# Header
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

# Playlist selector
user_playlists = get_user_playlists()
playlist_name_to_id = {pl["name"]: pl["id"] for pl in user_playlists}
playlist_names = [pl["name"] for pl in user_playlists]

selected_name = st.selectbox("Choose a playlist", playlist_names)
target_playlist_id = playlist_name_to_id.get(selected_name, "")
st.session_state["selected_playlist_id"] = target_playlist_id

st.markdown("---")

# Playlist preview — horizontal layout
st.markdown('<div class="section-header">Your target playlist</div>', unsafe_allow_html=True)

playlist_info = sp.playlist(target_playlist_id, fields="name,images,tracks.total")
playlist_name = playlist_info.get("name", "Unknown Playlist")
cover_url = playlist_info.get("images", [{}])[0].get("url")

col_img, col_meta = st.columns([1, 3])
with col_img:
    if cover_url:
        st.image(cover_url, width=120)
with col_meta:
    st.markdown(
        f'<div style="display:flex; align-items:center; height:120px;">'
        f'<div style="font-weight:700; font-size:1.1rem;">{playlist_name}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with st.expander("View 5 most recently added"):
    items = read_playlist(target_playlist_id, limit=5)
    for name, creator in items:
        st.markdown(
            f'<div class="playlist-item">🎙️ {name}, <span class="muted">{creator}</span></div>',
            unsafe_allow_html=True
        )

st.markdown("---")

# Search section
st.markdown('<div class="section-header">Find British content</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="muted">Search for a genre or topic. immer will find genuinely British-accented '
    'episodes for you to add to your playlist.</div>',
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)

query = st.text_input(
    "", placeholder="e.g. British comedy podcast, history, true crime...",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    run_button = st.button("🔍  Discover", use_container_width=True)

if run_button and query:
    # Reset for new search
    st.session_state["candidates"] = []
    st.session_state["added_uris"] = set()
    st.session_state["tavily_info"] = None

    st.markdown("---")
    st.markdown('<div class="section-header">Scanning candidates</div>', unsafe_allow_html=True)

    with st.spinner("Searching Spotify and Tavily..."):
        tavily_shows = find_shows_via_tavily(query)
        candidates, tavily_added = search_episodes(query, limit=6, extra_queries=tavily_shows)

    if tavily_shows:
        st.session_state["tavily_info"] = (len(tavily_shows), tavily_added)

    if not candidates:
        st.warning("No episodes found for that query. Try a different search.")
    else:
        st.markdown(
            f'<div class="muted">{len(candidates)} candidates found. Classifying each...</div>',
            unsafe_allow_html=True
        )
        with st.spinner("Classifying candidates..."):
            for ep in candidates:
                label = classify_accent(ep["name"], ep["description"])
                st.session_state["candidates"].append({"ep": ep, "label": label})
        st.rerun()

elif run_button and not query:
    st.warning("Enter a search query first.")

# Results — always shown if session state has candidates
if st.session_state.get("candidates"):
    st.markdown("---")

    if st.session_state.get("tavily_info"):
        n_shows, n_eps = st.session_state["tavily_info"]
        st.markdown(
            f'<div class="muted">Tavily surfaced {n_shows} additional shows'
            + (f', adding {n_eps} new episodes' if n_eps else '') + '.</div>',
            unsafe_allow_html=True
        )

    british = [c for c in st.session_state["candidates"] if c["label"] == "british"]
    added_uris = st.session_state.get("added_uris", set())

    if not british:
        st.markdown("""
        <div class="spotify-card">
            <div style="font-weight:600;">No genuinely British content found</div>
            <div class="muted">Try a more specific query, e.g. "British history podcast" or "BBC comedy"</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-header">British matches</div>', unsafe_allow_html=True)
        for c in british:
            ep = c["ep"]
            uri = ep["uri"]

            col_info, col_btn = st.columns([4, 1])
            with col_info:
                title_display = ep["name"][:70] + ("..." if len(ep["name"]) > 70 else "")
                show_name = ep["show"]
                show_line = (
                    f'<div class="muted">{show_name}</div>'
                    if show_name and show_name != "Unknown show" else ""
                )
                st.markdown(
                    f'<div style="color:#fff;font-weight:500;font-size:0.95rem;margin-bottom:0.15rem;">'
                    f'{title_display}</div>'
                    f'{show_line}',
                    unsafe_allow_html=True
                )
                if ep.get("description"):
                    with st.expander("Episode description"):
                        desc = ep["description"][:200]
                        st.markdown(f'<div class="muted">{desc}{"..." if len(ep["description"]) > 200 else ""}</div>', unsafe_allow_html=True)
                if ep.get("audio_preview_url"):
                    st.audio(ep["audio_preview_url"])

            with col_btn:
                already_added = uri in added_uris
                if already_added:
                    st.button("✅ Added", key=f"btn_{uri}", disabled=True)
                else:
                    if st.button("+ Add", key=f"btn_{uri}"):
                        with st.spinner("Adding to playlist..."):
                            add_to_playlist(target_playlist_id, uri)
                        st.session_state["added_uris"].add(uri)
                        st.rerun()

            st.markdown('<hr style="border-color:#282828;margin:0.4rem 0;">', unsafe_allow_html=True)

# Share section
st.markdown("---")
st.markdown('<div class="section-header">Share</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="muted">Generate a shareable collage: fal-generated background with your '
    'playlist cover art scattered on top as polaroids.</div>',
    unsafe_allow_html=True
)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    share_clicked = st.button("Share immer", key="share_btn")

if share_clicked:
    fal_warning = None

    with st.spinner("Generating your collage..."):
        bg_url = generate_fal_background()
        if bg_url is None:
            fal_warning = "fal generation failed. Using a plain dark background instead."
        cover_urls = get_playlist_cover_urls(target_playlist_id, limit=14)
        collage = make_collage(bg_url, cover_urls, target_playlist_id)

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

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; padding: 1rem 0;">
    <div class="muted">
        Built for {Tech: Europe} x VEED Hackathon. Powered by Spotify Web API, OpenAI, and Pioneer.
    </div>
</div>
""", unsafe_allow_html=True)
