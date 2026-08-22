from agent import run_agent, TARGET_PLAYLIST_ID

log, inserted = run_agent(TARGET_PLAYLIST_ID, "British comedy podcast")

print("\n".join(log))

if inserted:
    print(f"\nFinal pick: {inserted['name']} — {inserted['show']}")