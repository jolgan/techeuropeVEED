from agent import classify_accent

test_cases = [
    ("The Rest Is Football", "Gary Lineker, Alan Shearer and Micah Richards discuss the weekend's Premier League action from London."),
    ("The Bill Simmons Podcast", "Bill Simmons breaks down the NBA trade deadline with guests from ESPN."),
    ("Grounded with Louis Theroux", "Louis Theroux sits down with a guest for an intimate, wide-ranging conversation recorded in the UK."),
    ("Armchair Expert", "Dax Shepard talks with a Hollywood actor about their career and personal life."),
]

for title, desc in test_cases:
    label = classify_accent(title, desc)
    print(f"{title} → {label}")