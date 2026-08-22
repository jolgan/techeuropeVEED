import csv
from agent import search_episodes

BRITISH_SHOWS = [
    "No Such Thing As A Fish",
    "The Rest Is History",
    "Off Menu with Ed Gamble and James Acaster",
    "The Rest Is Politics",
    "Desert Island Discs",
    "The Adam Buxton Podcast",
    "In Our Time",
    "Kermode and Mayo's Film Review",
    "The Diary Of A CEO with Steven Bartlett",
    "Grounded with Louis Theroux",
    "Elis James and John Robins",
    "The News Agents",
    "Table Manners with Jessie and Lennie Ware",
    "You're Dead to Me",
    "The Infinite Monkey Cage",
    "RedHanded",
    "The Peter Crouch Podcast",
    "How to Fail with Elizabeth Day",
    "Sh**ged Married Annoyed",
    "The Traitors Uncloaked",
    "Answer Me This",
    "My Dad Wrote a Porno",
    "Griefcast",
    "Have A Word",
    "The News Quiz",
    "Murder Mile UK True Crime",
    "Drunk Women Solving Crime",
    "Bad People BBC Sounds",
    "The Spectator Podcast",
    "The Rest Is Entertainment",
]

AMERICAN_SHOWS = [
    "The Joe Rogan Experience",
    "Crime Junkie",
    "The Daily",
    "SmartLess",
    "Call Her Daddy",
    "This American Life",
    "Huberman Lab",
    "Pardon My Take",
    "This Past Weekend with Theo Von",
    "Pod Save America",
    "Serial",
    "Up First from NPR",
    "The Ben Shapiro Show",
    "Armchair Expert",
    "Conan O'Brien Needs a Friend",
    "My Favorite Murder",
    "Good Hang with Amy Poehler",
    "The Bill Simmons Podcast",
    "Dateline NBC",
    "The Herd with Colin Cowherd",
    "Fantasy Footballers",
    "The Dan Bongino Show",
    "Wait Wait Dont Tell Me",
    "The Dr John Delony Show",
    "Passion Struck with John R Miles",
    "Two Hot Takes",
    "Morbid A True Crime Podcast",
    "The Ramsey Show",
    "Office Ladies",
    "Chicks in the Office",
]

rows = []

for show in BRITISH_SHOWS:
    print(f"Searching: {show}")
    episodes = search_episodes(show, limit=5)
    for ep in episodes:
        rows.append({
            "title": ep["name"],
            "description": ep["description"][:500],  # trim long descriptions
            "show": ep["show"],
            "label": "british"
        })

for show in AMERICAN_SHOWS:
    print(f"Searching: {show}")
    episodes = search_episodes(show, limit=5)
    for ep in episodes:
        rows.append({
            "title": ep["name"],
            "description": ep["description"][:500],
            "show": ep["show"],
            "label": "not_british"
        })

with open("dataset.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "description", "show", "label"])
    writer.writeheader()
    writer.writerows(rows)

print(f"\n✅ Done. {len(rows)} rows written to dataset.csv")
print(f"British: {sum(1 for r in rows if r['label'] == 'british')}")
print(f"Not British: {sum(1 for r in rows if r['label'] == 'not_british')}")