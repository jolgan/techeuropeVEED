# immer

**{Tech: Europe} x VEED Hackathon submission, solo build by Jolene Gan**

## What this does

Streaming platforms default to whichever content variant has the most volume, usually American accented English podcasts. This quietly buries genuinely British accented content even when that is exactly what a listener wants. `immer` is an agent, wrapped in a real web app, that reaches into your Spotify account, finds genuinely British accented podcast content, and lets you insert it directly into an existing playlist.

The name is German for "always," a small nod to the language learning use case this generalises to.

## How it works

1. **Connect**: OAuth against your real Spotify account, scoped to read and modify playlists.
2. **Choose a playlist**: pick from your own owned playlists (not ones you have just saved from other people).
3. **Search**: enter a genre or topic. The agent searches Spotify's own catalogue, plus additional shows surfaced by Tavily web search that Spotify's own search under serves.
4. **Classify**: each candidate episode is scored by OpenAI (`gpt-4o-mini`) for whether it is genuinely British accented content, not just "English."
5. **Choose and add**: genuinely British matches are shown with a play button for a quick audio preview, plus an "Add" button, so you decide what actually goes into your playlist rather than the agent forcing a single pick.
6. **Share**: once you are happy with your playlist, generate a shareable collage of the playlist's real cover art, scattered like polaroids on a fal generated sticker bomb background, with a Spotify scan code so anyone can scan straight into the playlist.

## Technology used

- **Spotify Web API** (via `spotipy`), OAuth, playlist read, playlist write. The whole product is built around this.
- **OpenAI** (`gpt-4o-mini`), the classification step that decides genuinely British versus not, running live for every candidate.
- **Tavily**, sources lesser known British podcast shows that Spotify's own in app search does not surface well, widening the candidate pool beyond what Spotify would show on its own.
- **fal** (`fal-ai/flux/schnell`), generates the abstract sticker bomb style background art for the shareable collage. The album and podcast covers themselves are real, pulled from the actual playlist, not generated.

## What we tried that did not make the final cut: Pioneer

We attempted a fine tuned classifier on Pioneer (Fastino), training `fastino/gliner2-base-v1` on a labelled dataset of 300 real Spotify episode descriptions, split evenly between British and not British shows. Across five separate training runs (varying epochs, shuffling, text length, and dataset size), the resulting classifier consistently collapsed to predicting "British" for every input, including unambiguous American shows.

We are including this honestly rather than hiding it. The training jobs are real and inspectable via Pioneer's API if useful for debugging. When it did not resolve within the time available, the classification step in the live product uses OpenAI instead, which performs correctly.

## Known limitations

- The playlist's total episode count is not shown, since Spotify's API does not reliably return this field for all playlist types.
- Audio previews are only available for episodes where Spotify provides a preview URL. Not every episode has one.
- Real time skip or listen based adaptation was part of the original stretch goal but was not built in the time available.

## Setup

```bash
pip install spotipy python-dotenv openai tavily-python fal-client Pillow streamlit
```

`.env` file:
```
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
OPENAI_API_KEY=...
TAVILY_API_KEY=...
FAL_KEY=...
```

Run with:
```bash
streamlit run app.py
```
