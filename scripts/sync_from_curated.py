#!/usr/bin/env python3
"""Sync images from zen-wallpapers s-grade-curated.json to zen-feeds."""
import json
import os

CURATED_PATH = "../zen-wallpapers/s-grade-curated.json"
OUTPUT_PATH = "feeds.json"

# Zen quotes for variety
QUOTES = [
    ("Stillness Speaks", "In the space between thoughts, wisdom emerges."),
    ("The Present Moment", "Now is the only time that truly exists."),
    ("Inner Peace", "Calm waters reflect the sky perfectly."),
    ("Letting Go", "Release attachment to find freedom."),
    ("Mindful Breath", "Each breath is a new beginning."),
    ("Silent Wisdom", "Listen to the silence within."),
    ("Natural Flow", "Move with life, not against it."),
    ("Empty Mind", "An open mind receives infinite possibilities."),
    ("Simple Beauty", "Elegance lies in simplicity."),
    ("Timeless Now", "The eternal exists in this moment."),
]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(script_dir))  # Go to zen-feeds root
    
    with open(CURATED_PATH, 'r') as f:
        curated = json.load(f)
    
    feeds = {}
    for i, item in enumerate(curated):
        title, summary = QUOTES[i % len(QUOTES)]
        feeds[item['id']] = {
            "id": item['id'],
            "url": item['url'],
            "author": item.get('author', 'Unknown'),
            "title": title,
            "summary": summary,
            "score": item.get('score', 85),
            "date": "Feb 2026"
        }
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(feeds, f, indent=2, ensure_ascii=False)
    
    print(f"Synced {len(feeds)} images to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
