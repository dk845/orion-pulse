import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

NASA_API_KEY = os.getenv("NASA_API_KEY")

def fetch_space_weather(start_date="2026-04-01", end_date="2026-04-10"):
    """
    Fetches solar flare and geomagnetic storm data from NASA DONKI API
    during the Artemis II mission window (April 1-10, 2026)
    """
    print(f"Fetching space weather data from {start_date} to {end_date}...")

    # Solar Flares
    flare_url = f"https://api.nasa.gov/DONKI/FLR?startDate={start_date}&endDate={end_date}&api_key={NASA_API_KEY}"
    flare_response = requests.get(flare_url)
    flares = flare_response.json()

    # Geomagnetic Storms
    storm_url = f"https://api.nasa.gov/DONKI/GST?startDate={start_date}&endDate={end_date}&api_key={NASA_API_KEY}"
    storm_response = requests.get(storm_url)
    storms = storm_response.json()

    result = {
        "extracted_at": datetime.utcnow().isoformat(),
        "solar_flares": flares,
        "geomagnetic_storms": storms
    }

    # Save raw JSON locally for now (S3 comes in Week 3)
    os.makedirs("raw_data", exist_ok=True)
    with open("raw_data/space_weather.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"✅ Fetched {len(flares)} solar flares and {len(storms)} geomagnetic storms")
    return result

if __name__ == "__main__":
    data = fetch_space_weather()
    print(json.dumps(data, indent=2))