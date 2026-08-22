import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="playlist-read-private playlist-modify-private playlist-modify-public",
    open_browser=True
))

me = sp.current_user()
print(f"✅ Logged in as: {me['display_name']} ({me['id']})")

print("\nSearching all your playlists for a match...")
target_name = "in regards to the scrumping"
offset = 0
found = None

while True:
    batch = sp.current_user_playlists(limit=50, offset=offset)
    items = batch["items"]
    if not items:
        break
    for pl in items:
        if pl["name"].strip().lower() == target_name.lower():
            found = pl
            break
    if found or not batch["next"]:
        break
    offset += 50

if found:
    print(f"✅ Found: {found['name']}  (id: {found['id']})")
else:
    print("❌ Not found — check the exact spelling/capitalisation.")

print("\nReading playlist contents...")
playlist_id = "3e0Hp2gcBiQJeWPGnZjoYB"
results = sp.playlist_items(playlist_id, limit=10)

for i, item in enumerate(results["items"]):
    content = item.get("item")
    if content is None:
        print(f"{i+1}. [unavailable item — skipped]")
        continue
    name = content.get("name", "Unknown")
    if content.get("episode"):
        show = content.get("show", {})
        creator = show.get("name", "Unknown show")
    elif "artists" in content:
        creator = ", ".join([a["name"] for a in content["artists"]])
    else:
        creator = "Unknown"
    print(f"{i+1}. {name} — {creator}")

print(f"\nTotal tracks in playlist: {results['total']}")

print("\nSearching for a test episode to insert...")
search_results = sp.search(q="No Such Thing As A Fish", type="episode", limit=5)
episodes = search_results["episodes"]["items"]

for i, ep in enumerate(episodes):
    show_name = ep.get("show", {}).get("name", "Unknown show")
    print(f"{i+1}. {ep['name']} — {show_name}  (uri: {ep['uri']})")

print("\nAdding test episode to playlist...")
test_uri = "spotify:episode:568CUup0BSOzyozvO0R7mI"  # "Have An Ice Cream Bird" episode
result = sp.playlist_add_items(playlist_id, [test_uri])
print(f"✅ Added! Snapshot ID: {result['snapshot_id']}")

#print("\n--- DEBUG: raw first item ---")
#import json
#print(json.dumps(results["items"][0], indent=2)[:1500])