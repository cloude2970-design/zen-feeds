#!/usr/bin/env python3
"""
Sync images from zen-wallpapers with content-relevant titles and summaries.
Extracts search query from Unsplash URL and generates matching descriptions.
"""
import json
import os
import re
import base64
from urllib.parse import unquote

CURATED_PATH = "../zen-wallpapers/s-grade-curated.json"
OUTPUT_PATH = "feeds.json"

# Content-aware descriptions based on common search terms
CONTENT_DESCRIPTIONS = {
    # Nature/Zen
    "misty mountain": [
        ("Veiled Peaks", "Mountains draped in morning mist, where earth meets sky in quiet embrace."),
        ("Cloud Walker", "Through the mist, the mountain reveals its ancient patience."),
        ("Silent Heights", "Where fog and stone converse in whispers."),
    ],
    "zen garden": [
        ("Raked Silence", "Sand patterns trace the rhythm of a still mind."),
        ("Stone Meditation", "Each rock placed with purpose, each space intentional."),
        ("Garden of Peace", "Nature arranged to mirror inner tranquility."),
    ],
    "bamboo": [
        ("Hollow Strength", "The bamboo bends but never breaks."),
        ("Green Whispers", "Leaves rustling secrets of resilience."),
        ("Forest of Patience", "Growing slowly, reaching surely."),
    ],
    "lotus": [
        ("Rising Pure", "From murky depths, beauty emerges unstained."),
        ("Water Bloom", "The lotus needs no instruction to unfold."),
        ("Sacred Blossom", "Rooted in mud, crowned in light."),
    ],
    "waterfall": [
        ("Falling Free", "Water teaches the art of letting go."),
        ("Cascade Song", "The mountain releases what it cannot hold."),
        ("Eternal Flow", "Neither beginning nor end, only motion."),
    ],
    "forest": [
        ("Ancient Canopy", "Trees standing in silent congregation."),
        ("Green Cathedral", "Light filters through nature's stained glass."),
        ("Woodland Breath", "The forest exhales peace."),
    ],
    "sunrise": [
        ("First Light", "Dawn breaks without asking permission."),
        ("Morning Promise", "Each sunrise, the world begins again."),
        ("Golden Awakening", "Light returning to reclaim the horizon."),
    ],
    "sunset": [
        ("Day's Farewell", "The sun departs painting the sky with gratitude."),
        ("Golden Hour", "When light softens and shadows lengthen."),
        ("Evening Glow", "Nature's daily masterpiece."),
    ],
    "ocean": [
        ("Endless Blue", "The sea holds more than it reveals."),
        ("Tidal Wisdom", "Waves teach patience in their rhythm."),
        ("Deep Calm", "Beneath the surface, stillness prevails."),
    ],
    "mountain": [
        ("Standing Firm", "The mountain neither leans nor hurries."),
        ("Peak Solitude", "Where earth touches sky in silent greeting."),
        ("Stone Patience", "Ages pass, the mountain remains."),
    ],
    "lake": [
        ("Mirror Surface", "Still water reflects truth without judgment."),
        ("Quiet Depths", "The lake accepts all rivers equally."),
        ("Reflective Peace", "In stillness, the sky finds its twin."),
    ],
    "river": [
        ("Flowing Path", "The river knows its way without maps."),
        ("Constant Change", "Never the same water, always the same river."),
        ("Journey Home", "All rivers remember the sea."),
    ],
    "rain": [
        ("Falling Grace", "Rain nourishes without choosing where."),
        ("Sky's Gift", "Each drop carries the ocean's memory."),
        ("Cleansing Rhythm", "Nature's gentle reset."),
    ],
    "snow": [
        ("White Silence", "Snow falls on all paths equally."),
        ("Winter's Blanket", "The earth rests under soft white cover."),
        ("Frozen Stillness", "Cold clarity reveals hidden forms."),
    ],
    # Food/Culinary
    "tea": [
        ("Steeped Wisdom", "In each cup, a moment of presence."),
        ("Warm Ritual", "The ceremony is in the attention."),
        ("Liquid Meditation", "Tea teaches patience, cup by cup."),
    ],
    "tea ceremony": [
        ("Sacred Pour", "Each movement a meditation."),
        ("Ritual Calm", "The way of tea is the way of peace."),
        ("Mindful Service", "Presence in every gesture."),
    ],
    "coffee": [
        ("Morning Ritual", "The first cup, a daily awakening."),
        ("Dark Comfort", "Warmth in a humble vessel."),
        ("Aromatic Pause", "Between tasks, a moment to breathe."),
    ],
    "wine": [
        ("Aged Patience", "Time transforms what it touches."),
        ("Vineyard Memory", "Each glass holds a season's story."),
        ("Deep Ruby", "Light captured in liquid form."),
    ],
    "wine glass": [
        ("Crystal Moment", "Light dances through the glass."),
        ("Elegant Pause", "Wine waits for those who appreciate."),
        ("Vineyard Dreams", "In the glass, the earth speaks."),
    ],
    "bread": [
        ("Baked Comfort", "Simple ingredients, profound nourishment."),
        ("Crusty Wisdom", "Patience transforms flour into sustenance."),
        ("Daily Bread", "The staff of life, warm from the oven."),
    ],
    "fruit": [
        ("Nature's Candy", "Sweetness wrapped in simple form."),
        ("Ripe Moment", "The fruit falls when ready."),
        ("Colorful Harvest", "Earth's edible art."),
    ],
    "herbs": [
        ("Green Medicine", "Nature's pharmacy in leaf and stem."),
        ("Aromatic Garden", "Fragrance as flavor."),
        ("Kitchen Wisdom", "Ancient flavors, timeless recipes."),
    ],
    # Travel/Landscape
    "lighthouse": [
        ("Guiding Light", "Standing watch where land meets sea."),
        ("Beacon Hope", "Light piercing the darkness for wanderers."),
        ("Coastal Sentinel", "Steadfast through every storm."),
    ],
    "path": [
        ("Winding Way", "The journey reveals itself step by step."),
        ("Footsteps Forward", "Each path is made by walking."),
        ("Trail Ahead", "The destination is less than the journey."),
    ],
    "bridge": [
        ("Connection", "Spanning the divide with purpose."),
        ("Crossing Over", "The bridge asks nothing of those who pass."),
        ("Structural Grace", "Engineering meets artistry."),
    ],
    "temple": [
        ("Sacred Space", "Walls built to hold silence."),
        ("Ancient Prayers", "Stone remembers centuries of devotion."),
        ("Spiritual Architecture", "Form designed for transcendence."),
    ],
    "village": [
        ("Simple Life", "Community in its purest form."),
        ("Quiet Streets", "Where neighbors are family."),
        ("Timeless Pace", "Life unfolds without hurry."),
    ],
    "architecture": [
        ("Built Beauty", "Human creativity in stone and steel."),
        ("Structural Poetry", "Form following function, beautifully."),
        ("Urban Art", "Buildings as sculptures for living."),
    ],
    "aerial": [
        ("Bird's View", "Perspective changes everything."),
        ("From Above", "Patterns invisible from the ground."),
        ("Sky Perspective", "The earth as tapestry."),
    ],
    "coast": [
        ("Where Worlds Meet", "Land and sea in eternal conversation."),
        ("Shore Line", "The edge of everything."),
        ("Coastal Beauty", "Salt air and endless horizons."),
    ],
}

# Generic fallbacks by category
CATEGORY_FALLBACKS = {
    "food": [
        ("Culinary Moment", "Simple pleasures, artfully presented."),
        ("Kitchen Poetry", "Ingredients arranged with intention."),
        ("Edible Art", "When cooking becomes creation."),
        ("Savory Scene", "Food that feeds more than the body."),
        ("Table Setting", "Gathering around nourishment."),
    ],
    "nature": [
        ("Natural Beauty", "Earth's artistry needs no frame."),
        ("Wild Serenity", "Nature's untouched perfection."),
        ("Organic Form", "Shapes born of time and elements."),
        ("Earth's Canvas", "Colors only nature can blend."),
        ("Living Art", "Beauty that breathes and grows."),
    ],
    "travel": [
        ("Journey's Frame", "Moments captured along the way."),
        ("Distant View", "Horizons calling to explorers."),
        ("Wanderer's Eye", "Seeing the world with fresh wonder."),
        ("Path Taken", "Every road tells a story."),
        ("Scenic Pause", "Worth the journey to witness."),
    ],
}

def extract_search_query(url):
    """Extract the search query from Unsplash URL."""
    # Extract the ixid parameter and decode it
    ixid_match = re.search(r'ixid=([^&]+)', url)
    if ixid_match:
        ixid = ixid_match.group(1)
        try:
            # Add padding if needed for base64
            padded = ixid + '=' * (4 - len(ixid) % 4)
            decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
            # Format: 3|...|search|{num}||{query}|en|...
            parts = decoded.split('|')
            for i, part in enumerate(parts):
                if part == 'search' and i + 3 < len(parts):
                    # Query is after search|num||
                    query = unquote(parts[i + 3])
                    if query and query != 'en':
                        return query.lower()
        except Exception:
            pass
    
    return None

def get_category_from_reason(reason):
    """Extract category from the reason field."""
    reason_lower = reason.lower()
    if 'food' in reason_lower or 'culinary' in reason_lower:
        return 'food'
    elif 'travel' in reason_lower or 'landscape' in reason_lower:
        return 'travel'
    else:
        return 'nature'

def get_description(url, reason, index):
    """Get a content-relevant title and summary."""
    query = extract_search_query(url)
    category = get_category_from_reason(reason)
    
    # Try to find matching content description
    if query:
        for key, descriptions in CONTENT_DESCRIPTIONS.items():
            if key in query or query in key:
                desc = descriptions[index % len(descriptions)]
                return desc[0], desc[1], category
    
    # Fall back to category-based description
    fallbacks = CATEGORY_FALLBACKS.get(category, CATEGORY_FALLBACKS['nature'])
    desc = fallbacks[index % len(fallbacks)]
    return desc[0], desc[1], category

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(os.path.dirname(script_dir))  # Go to zen-feeds root
    
    if not os.path.exists(CURATED_PATH):
        print(f"Source file not found: {CURATED_PATH}")
        return
    
    with open(CURATED_PATH, 'r') as f:
        curated = json.load(f)
    
    # Load existing feeds to preserve any manual edits
    existing_feeds = {}
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, 'r') as f:
            existing_feeds = json.load(f)
    
    feeds = {}
    for i, item in enumerate(curated):
        img_id = item['id']
        reason = item.get('reason', '')
        
        title, summary, category = get_description(item['url'], reason, i)
        
        feeds[img_id] = {
            "id": img_id,
            "url": item['url'],
            "author": item.get('author', 'Unknown'),
            "title": title,
            "summary": summary,
            "score": item.get('score', 85),
            "date": item.get('date', 'Feb 2026'),
            "category": category
        }
    
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(feeds, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Synced {len(feeds)} images with content-relevant descriptions")
    
    # Show sample
    print("\nSample entries:")
    for i, (img_id, data) in enumerate(list(feeds.items())[:5]):
        print(f"  [{data['category']}] {data['title']}: {data['summary'][:50]}...")

if __name__ == "__main__":
    main()
