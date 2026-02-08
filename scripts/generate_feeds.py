import json
import subprocess
import os

CACHE_FILE = 'feeds.json'
SOURCE_FILE = '../zen-wallpapers/s-grade-curated.json'

def get_gemini_content(reason, author):
    prompt = f"""
    Create a zen-inspired blog article for a high-quality image.
    Image details: {reason} by {author}.
    
    Output in JSON format with exactly these keys:
    - title: A short, poetic title (max 60 chars)
    - summary: A calming summary/teaser (max 150 chars)
    - article: A short, mindful essay (3-4 paragraphs) exploring the theme of the image (Zen, Nature, or Culinary beauty).
    
    Language: English.
    Return ONLY valid JSON.
    """
    try:
        result = subprocess.run(['gemini', prompt], capture_output=True, text=True)
        if result.returncode == 0:
            # Try to parse JSON from output
            content = result.stdout.strip()
            # Clean up potential markdown code blocks
            if content.startswith('```json'):
                content = content[7:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
            return json.loads(content)
    except Exception as e:
        print(f"Error calling gemini: {e}")
    return None

def main():
    if not os.path.exists(SOURCE_FILE):
        print("Source file not found")
        return

    with open(SOURCE_FILE, 'r') as f:
        wallpapers = json.load(f)

    # Load existing cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            feeds = json.load(f)
    else:
        feeds = {}

    # Process latest 15 wallpapers
    latest = wallpapers[:15]
    updated = False

    for wp in latest:
        wp_id = wp['id']
        if wp_id in feeds:
            continue
        
        print(f"Generating content for {wp_id}...")
        content = get_gemini_content(wp['reason'], wp['author'])
        if content:
            feeds[wp_id] = {
                "id": wp_id,
                "url": wp['url'],
                "author": wp['author'],
                "title": content['title'],
                "summary": content['summary'],
                "article": content['article'],
                "date": wp.get('date', 'Feb 9, 2026')
            }
            updated = True
        else:
            print(f"Failed to generate for {wp_id}")

    if updated:
        with open(CACHE_FILE, 'w') as f:
            json.dump(feeds, f, indent=2)
        print("Feeds updated.")
    else:
        print("No new feeds generated.")

if __name__ == "__main__":
    main()
