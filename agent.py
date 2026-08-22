import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from openai import OpenAI

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="playlist-read-private playlist-modify-private playlist-modify-public",
    open_browser=True
))

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TARGET_PLAYLIST_ID = "3e0Hp2gcBiQJeWPGnZjoYB"  # "in regards to the scrumping"


def get_current_user():
    return sp.current_user()

def classify_accent(title, description):
    """
    Classify a podcast episode as genuinely British-accented or not,
    based on title and description text. Returns (label, confidence_reasoning).
    """
    prompt = f"""You are classifying podcast content for accent/variant, not just language.

Episode title: {title}
Episode description: {description}

Is this podcast genuinely British-accented content (British hosts, British production, 
British cultural context) — as opposed to American, Australian, Irish, Canadian, or 
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
        label = "not_british"  # safe default on unexpected output
    return label

def run_agent(playlist_id, search_query, max_candidates=5):
    """
    The core loop: search for candidate episodes, classify each for
    genuine British accent, and insert the best match into the playlist.
    Returns a log of what happened for demo narration.
    """
    log = []
    log.append(f"Searching Spotify for: '{search_query}'")
    candidates = search_episodes(search_query, limit=max_candidates)
    log.append(f"Found {len(candidates)} candidates")

    best_match = None
    for ep in candidates:
        label = classify_accent(ep["name"], ep["description"])
        log.append(f"  '{ep['name']}' → classified as {label}")
        if label == "british" and best_match is None:
            best_match = ep

    if best_match is None:
        log.append("No genuinely British candidate found in this batch.")
        return log, None

    log.append(f"Selected: '{best_match['name']}' — inserting into playlist")
    snapshot_id = add_to_playlist(playlist_id, best_match["uri"])
    log.append(f"✅ Inserted successfully (snapshot: {snapshot_id})")

    return log, best_match

def read_playlist(playlist_id, limit=10):
    """Return a list of (name, creator) tuples from a playlist."""
    results = sp.playlist_items(playlist_id, limit=limit)
    items = []
    for entry in results["items"]:
        content = entry.get("item")
        if content is None:
            continue
        name = content.get("name", "Unknown")
        if content.get("episode"):
            creator = content.get("show", {}).get("name", "Unknown show")
        elif "artists" in content:
            creator = ", ".join(a["name"] for a in content["artists"])
        else:
            creator = "Unknown"
        items.append((name, creator))
    return items


def search_episodes(query, limit=5):
    """Search Spotify for candidate episodes. Returns list of dicts."""
    results = sp.search(q=query, type="episode", limit=limit)
    candidates = []
    for ep in results["episodes"]["items"]:
        candidates.append({
            "name": ep["name"],
            "description": ep.get("description", ""),
            "uri": ep["uri"],
            "show": ep.get("show", {}).get("name", "Unknown show"),
        })
    return candidates


def add_to_playlist(playlist_id, uri):
    """Add a single track/episode URI to a playlist. Returns snapshot_id."""
    result = sp.playlist_add_items(playlist_id, [uri])
    return result["snapshot_id"]


if __name__ == "__main__":
    # Quick sanity check that everything still works
    me = get_current_user()
    print(f"✅ Logged in as: {me['display_name']} ({me['id']})")

    tracks = read_playlist(TARGET_PLAYLIST_ID, limit=5)
    print(f"\nFirst 5 items in target playlist:")
    for name, creator in tracks:
        print(f"  - {name} — {creator}")