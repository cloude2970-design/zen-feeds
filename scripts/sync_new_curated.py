#!/usr/bin/env python3
"""Sync new images from zen-wallpapers s-grade-curated.json to zen-feeds."""
import json
import os
import random
import re

CURATED_PATH = "../zen-wallpapers/s-grade-curated.json"
OUTPUT_PATH = "feeds.json"

# Map curation themes to categories
THEME_TO_CATEGORY = {
    "Zen/Nature": "nature",
    "Food/Culinary": "food",
    "Travel/Landscape": "travel"
}

# Zen content pools
ZEN_TITLES = [
    "Morning Dew", "Silent Dawn", "Gentle Breeze", "Moonlit Path", "Quiet Stream",
    "Ancient Wisdom", "Floating Clouds", "Still Waters", "Empty Sky", "Soft Light",
    "Distant Mountains", "Bamboo Grove", "Stone Garden", "Autumn Leaf", "Spring Rain",
    "Winter Snow", "Summer Heat", "Fading Twilight", "Rising Sun", "Setting Moon",
    "Wandering Mind", "Grounded Heart", "Open Spirit", "Clear Vision", "Pure Essence",
    "Infinite Space", "Timeless Moment", "Sacred Pause", "Deep Roots", "High Branches",
    "River Song", "Wind Whisper", "Earth Breath", "Fire Dance", "Water Mirror",
    "Mountain Silence", "Valley Echo", "Forest Dream", "Desert Bloom", "Ocean Calm",
    "Starlit Night", "Sunlit Morning", "Golden Hour", "Blue Moment", "Green Shade",
    "First Step", "New Beginning", "Simple Truth", "Hidden Path", "Open Door",
    "Walking Meditation", "Sitting Still", "Standing Tall", "Rising Up", "Letting Be",
    "Before Thought", "Beyond Time", "Into Light", "Under Stars", "Over Mountains",
    "Gentle Awakening", "Soft Landing", "Slow Unfolding", "Deep Knowing", "True Nature",
    "Original Face", "Beginner Mind", "Complete Stillness", "Woven Peace", "Painted Sky",
    "Unspoken Bond", "Remembered Dream", "Found Treasure", "Shared Wisdom", "Daily Practice",
    "Eternal Now", "Fleeting Beauty", "Lasting Peace", "Growing Edge", "Balanced Center",
    "Harmonious Flow", "Silent Song", "Clear Present", "Warm Embrace", "Fresh Start",
]

ZEN_SUMMARIES = [
    "In stillness, the world reveals its secrets.",
    "Each moment holds infinite possibility.",
    "Breathe in peace, breathe out worry.",
    "The path appears when you stop searching.",
    "Silence speaks louder than words.",
    "Let go of what no longer serves you.",
    "Find the extraordinary in the ordinary.",
    "Wisdom grows in the garden of patience.",
    "Peace begins with a single breath.",
    "In simplicity, find true abundance.",
    "Nature teaches without speaking.",
    "Rest in the space between thoughts.",
    "Acceptance opens every door.",
    "The present moment is always enough.",
    "Clarity comes when the mind settles.",
    "The heart knows what the mind forgets.",
    "Gratitude transforms what you have into enough.",
    "Every breath is a fresh start.",
    "The deepest truths are the simplest.",
    "In emptiness, find fullness.",
    "Your thoughts are clouds, not the sky.",
    "What you seek is seeking you.",
    "In chaos, find your still point.",
    "The flower does not compete with the one beside it.",
]

# Category-specific articles
ARTICLES = {
    "nature": [
        {
            "headline": "The Art of Forest Bathing",
            "content": "Shinrin-yoku, the Japanese practice of forest bathing, isn't about hiking or exercise. It's about being present among trees.\n\nWalk slowly. Touch bark. Smell the air. Let nature absorb your attention.",
            "tips": ["Leave your phone behind", "Walk without destination", "Engage all five senses"]
        },
        {
            "headline": "Learning From Still Water",
            "content": "A calm lake reflects perfectly. A disturbed surface distorts everything. Your mind works the same way.\n\nCultivate stillness not by force, but by releasing agitation.",
            "tips": ["Watch water for five minutes daily", "Notice what disturbs your inner lake", "Practice non-reaction"]
        },
        {
            "headline": "Reading the Language of Clouds",
            "content": "Clouds are nature's meditation. They form, drift, and dissolve without clinging to any shape.\n\nWatch them. Learn from their impermanence. Let your thoughts move like clouds.",
            "tips": ["Spend ten minutes cloud-watching", "Notice shapes without naming them", "Let thoughts pass like clouds"]
        },
    ],
    "food": [
        {
            "headline": "The Meditation of Cooking",
            "content": "Cooking is not just preparation—it's presence. The sound of sizzling, the colors transforming, the aromas rising.\n\nCook without rushing. Each step is complete in itself.",
            "tips": ["Put away your phone while cooking", "Focus on one task at a time", "Taste mindfully as you go"]
        },
        {
            "headline": "Eating as Practice",
            "content": "Most meals are eaten on autopilot. True nourishment begins with attention.\n\nNotice textures. Taste fully. Chew slowly. Each bite is a gift.",
            "tips": ["Take three breaths before eating", "Put down utensils between bites", "Notice when you feel satisfied"]
        },
        {
            "headline": "The Beauty of Simple Ingredients",
            "content": "A perfect tomato needs nothing. A ripe apple is already complete. The best cooking honors what's already there.\n\nSimplicity reveals rather than conceals.",
            "tips": ["Choose one ingredient to celebrate", "Use fewer seasonings, taste more", "Let the food speak"]
        },
    ],
    "travel": [
        {
            "headline": "The Journey Within",
            "content": "Every external journey mirrors an internal one. New places reveal new parts of ourselves.\n\nTravel not to escape yourself, but to meet yourself in unfamiliar territory.",
            "tips": ["Journal in new places", "Notice what draws your attention", "Embrace disorientation"]
        },
        {
            "headline": "Being a Guest in the World",
            "content": "Travelers are perpetual guests. We arrive, appreciate, and move on. This is true for life itself.\n\nTreat every place with the respect of a guest who may never return.",
            "tips": ["Learn three local words", "Observe before participating", "Leave places better than you found them"]
        },
        {
            "headline": "The Wisdom of Getting Lost",
            "content": "Getting lost strips away plans and exposes presence. You must pay attention when you don't know where you are.\n\nSometimes the best discoveries come from the detours.",
            "tips": ["Put away the map occasionally", "Follow your curiosity", "Trust that you'll find your way"]
        },
    ]
}

def extract_category(reason):
    """Extract category from curation reason."""
    for theme, cat in THEME_TO_CATEGORY.items():
        if theme in reason:
            return cat
    return "nature"  # default

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(script_dir))  # Go to zen-feeds root
    
    # Load existing feeds
    with open(OUTPUT_PATH, 'r') as f:
        feeds = json.load(f)
    
    existing_ids = set(feeds.keys())
    print(f"Existing feeds: {len(existing_ids)}")
    
    # Load curated images
    with open(CURATED_PATH, 'r') as f:
        curated = json.load(f)
    
    # Find new images
    new_items = [item for item in curated if item['id'] not in existing_ids]
    print(f"New images to add: {len(new_items)}")
    
    if not new_items:
        print("No new images to sync.")
        return
    
    # Shuffle pools for variety
    titles = ZEN_TITLES.copy()
    summaries = ZEN_SUMMARIES.copy()
    random.shuffle(titles)
    random.shuffle(summaries)
    
    added = 0
    for i, item in enumerate(new_items):
        category = extract_category(item.get('reason', ''))
        title = titles[i % len(titles)]
        summary = summaries[i % len(summaries)]
        article = random.choice(ARTICLES[category])
        
        feeds[item['id']] = {
            "id": item['id'],
            "url": item['url'],
            "author": item.get('author', 'Unknown'),
            "title": title,
            "summary": summary,
            "score": item.get('score', 85),
            "date": "Feb 2026",
            "category": category,
            "article": article
        }
        added += 1
    
    # Save updated feeds
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(feeds, f, indent=2, ensure_ascii=False)
    
    print(f"Added {added} new images. Total feeds: {len(feeds)}")

if __name__ == "__main__":
    main()
