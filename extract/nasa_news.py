import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

NASA_API_KEY = os.getenv("NASA_API_KEY")

def fetch_nasa_news():
    """
    Fetches official NASA news articles about Artemis II mission
    """
    print("Fetching NASA Artemis II news...")

    url = "https://images-api.nasa.gov/search?q=Artemis+II&media_type=image&year_start=2026&year_end=2026"
    
    response = requests.get(url)
    data = response.json()

    articles = data.get("collection", {}).get("items", [])

    result = {
        "extracted_at": datetime.now().isoformat(),
        "source": "NASA Image and Video Library",
        "total_items": len(articles),
        "articles": articles
    }

    os.makedirs("raw_data", exist_ok=True)
    with open("raw_data/nasa_news.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"✅ Fetched {len(articles)} NASA Artemis II news items")
    return result

if __name__ == "__main__":
    data = fetch_nasa_news()
    for item in data["articles"][:5]:
        title = item.get("data", [{}])[0].get("title", "No title")
        date = item.get("data", [{}])[0].get("date_created", "")
        print(f"📰 {date[:10]} — {title}")