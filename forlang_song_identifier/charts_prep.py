#this is a script to process the charts data gathered in the acharts project folder and prepare it for checklang.py
import json, os

unique = set(())
for fn in os.listdir("acharts/chart_data"):
    with open (f"acharts/chart_data/{fn}", "r", encoding="utf8") as f:
        data = json.load(f)
    
    for week in data.values():
        for song, artists in week:
            unique.add((song, artists[0]))

with open ("forlang_song_identifier/data/unique.json", "w", encoding="utf8") as f:
    json.dump(list(unique), f, indent=0)
