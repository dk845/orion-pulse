import requests
import json
import os
from datetime import datetime
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
load_dotenv()

def fetch_dsn_data():
    """
    Fetches NASA Deep Space Network ground station data
    Shows which dishes were communicating with Orion during Artemis II
    """
    print("Fetching DSN ground station data...")

    url = "https://eyes.nasa.gov/dsn/data/dsn.xml"
    
    response = requests.get(url, params={"r": "2026"})
    
    # DSN returns XML so we parse it differently
    root = ET.fromstring(response.content)
    
    stations = []
    for dish in root.iter("dish"):
        station = {
            "name": dish.get("name"),
            "azimuth": dish.get("azimuth"),
            "elevation": dish.get("elevation"),
            "wind_speed": dish.get("windSpeed"),
            "targets": []
        }
        for target in dish.iter("target"):
            station["targets"].append({
                "name": target.get("name"),
                "id": target.get("id"),
                "upleg_range": target.get("uplegRange"),
                "downleg_range": target.get("downlegRange"),
                "rtlt": target.get("rtlt")
            })
        stations.append(station)

    result = {
        "extracted_at": datetime.now().isoformat(),
        "source": "NASA DSN Now",
        "total_dishes": len(stations),
        "stations": stations
    }

    os.makedirs("raw_data", exist_ok=True)
    with open("raw_data/dsn_data.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"✅ Fetched data for {len(stations)} DSN dishes")
    return result

if __name__ == "__main__":
    data = fetch_dsn_data()
    for station in data["stations"]:
        print(f"📡 {station['name']} — targets: {[t['name'] for t in station['targets']]}")