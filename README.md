# immer — The Immersion Smuggler (Accent Edition)

**{Tech: Europe} x VEED Hackathon submission**

## What this does

Streaming platforms default to whichever content variant has the most volume — American-accented English podcasts, in this case — which quietly buries genuinely British-accented content even when that's exactly what a listener wants. `immer` is an agent that reaches into a real Spotify account, finds genuinely British-accented podcast content, and inserts it live into an existing playlist — not a new app to open, a correction to the feed you already use.

The name is German for "always," a small nod to the language-learning use case this generalises to (see Stretch goal, below).

## Architecture

The core loop:

1. **Auth** — OAuth (Authorization Code flow) against a real Spotify account via `spotipy`, scoped to read and modify playlists.
2. **Search** — query Spotify's catalogue for candidate podcast episodes matching a target playlist's vibe.
3. **Classify** — score each candidate: is this genuinely British-accented content, or "English" content that's actually American (or another variant)?
4. **Insert** — add the highest-scoring genuinely-British candidate into the real playlist via the Spotify Web API.
5. **Observe** — (stretch goal, not built this session) track skip vs. full-listen behaviour as a signal for match quality.

## Partner technologies used

- **Spotify Web API** (via `spotipy`) — OAuth, playlist read, playlist write. Fully working end-to-end against a real account and a real playlist (`in regards to the scrumping`).
- **Web search** — used in place of a literal Tavily API call to source lists of well-known British and American podcasts/shows for the training dataset, and to research the Pioneer API's real endpoint contracts mid-build.
- **Pioneer (Fastino)** — attempted: see "What I tried and why it's not in the final demo" below.
- **OpenAI** — [used for the classification step in the final working demo / see below]
- **fal** — used for [demo video visual/audio polish, if applicable]
- **h (computer-use agents)** — considered for browser-based podcast sourcing where no API exists, but the core loop here is fully API-native (Spotify + classifier), so I didn't force it in. Noted here for transparency about what we evaluated.

## What I tried and why it's not in the final demo: the Pioneer classifier

I built a full, working pipeline against Pioneer's real API:

- Assembled a 150-row labelled dataset (75 British / 75 not-British) from real Spotify episode metadata across 30 well-known shows (e.g. *No Such Thing As A Fish*, *The Rest Is History* vs. *The Joe Rogan Experience*, *Crime Junkie*).
- Uploaded it via Pioneer's three-step dataset flow (`/felix/datasets/upload/url` → S3 PUT → `/felix/datasets/upload/process`), confirmed `status: ready`.
- Fine-tuned `fastino/gliner2-base-v1` via `POST /felix/training-jobs` (LoRA, single-label classification) — four separate training runs, iterating on:
  - default settings,
  - shuffled data (in case of ordering bias in the train/validation split),
  - titles-only text (in case long sponsor-boilerplate descriptions were diluting signal).

Every run trained "successfully" (loss curves looked plausible) but the resulting classifier collapsed to predicting **"british" for every input**, including unambiguous American shows like *Armchair Expert* and *The Bill Simmons Podcast*, at 97–99.99% confidence. This persisted across all four variations, which rules out my data prep as the cause and points to either a training configuration issue specific to this task shape on Pioneer's platform, or a GLiNER2 limitation for this kind of subtle binary text classification — I didn't have time to isolate which, within the hackathon window.

I'm including this rather than hiding it: the failed job IDs are real and inspectable via Pioneer's API (`GET /felix/training-jobs/:id`) if useful for debugging, and I think a transparent account of a legitimate ML attempt that didn't pan out is more honest than a black-box "it works" claim.

## Known limitations

- Real-time skip/listen adaptation (the "observe and adapt" step) is not built — out of scope for the time available.
- The Pioneer-based classifier does not work reliably (see above); [the demo uses an OpenAI-based classifier instead / see final architecture note].
- The dataset's `show` field is "Unknown show" for all rows due to a Spotify search API limitation (the episode search endpoint doesn't return show metadata) — classification was trained on title + description text only, which was sufficient signal for a human reviewing the data but apparently not for the fine-tuned model.

## Setup

```bash
pip3 install spotipy python-dotenv requests
```

`.env` file:
```
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
PIONEER_API_KEY=...
```

Run `python3 agent.py` to authenticate and sanity-check playlist read access.
