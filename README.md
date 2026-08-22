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

## Run locally (judge instructions)

### What you need

- Python 3.10 or newer (the project was tested with Python 3.12)
- A Spotify account with at least one playlist you own
- API credentials for Spotify, OpenAI, Tavily, and fal

The app writes real podcast episodes to the Spotify playlist selected in the UI. For a safe test, create a new empty Spotify playlist first (for example, `immer judge test`).

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/jolgan/techeuropeVEED.git
cd techeuropeVEED
python3 -m venv venv
source venv/bin/activate
```

On Windows PowerShell, activate with:

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API credentials

Create a `.env` file in the repository root. It is ignored by Git and must never be committed.

```dotenv
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
FAL_KEY=your_fal_api_key
```

Where to get each value:

- **Spotify:** create an app in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard). In that app's settings, add **exactly** `http://127.0.0.1:8888/callback` as a Redirect URI, then copy its Client ID and Client Secret into `.env`.
- **OpenAI:** create an API key in the OpenAI platform. It is used to classify candidate episode descriptions as British-accented or not.
- **Tavily:** create an API key in the Tavily dashboard. It broadens the podcast-show search beyond Spotify's own results.
- **fal:** create a fal API key. It is used only when generating the optional shareable playlist collage.

When first launched, Spotify opens a browser window asking the judge to authorise the app. Approve the requested playlist permissions. The OAuth callback then returns to `127.0.0.1:8888`; do not change the redirect URI in either Spotify or `.env`.

### 4. Start the app

```bash
streamlit run app.py
```

Streamlit will print a local URL, normally `http://localhost:8501`. Open it in a browser. To stop the app, press `Ctrl+C` in the terminal.

### Quick judging path

1. Authorise Spotify when prompted.
2. Select the empty test playlist created above.
3. Search for a topic such as `British comedy podcast`, `British history`, or `BBC science`.
4. Review the British matches and click **Add** on one or more episodes.
5. Use **Open playlist in Spotify ↗** to confirm the additions in Spotify (it opens in a new tab).
6. In **Share**, hover over **shimmer** to see it expand to **share immer**, then click it to generate a downloadable collage. The share step needs a valid `FAL_KEY`; searching and adding episodes do not depend on fal.

### Troubleshooting

- **Spotify redirect error:** ensure the callback in the Spotify Developer Dashboard and `SPOTIFY_REDIRECT_URI` are both exactly `http://127.0.0.1:8888/callback`.
- **Spotify login uses the wrong account:** sign out of Spotify in the browser or use a private window, then restart Streamlit and authorise again.
- **No results or an API error:** verify the relevant key in `.env`, then stop and restart Streamlit after changing it.
- **Collage falls back to a plain background:** the fal request was unavailable; playlist cover art and the Spotify scan code are still generated.
