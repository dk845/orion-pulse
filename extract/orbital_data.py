import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

def fetch_orbital_data():
    """
    Fetches Orion spacecraft position, distance from Earth/Moon, 
    and speed during Artemis II mission using JPL Horizons API
    """
    print("Fetching Orion orbital data from JPL Horizons...")

    # Orion Artemis II NAIF ID = -98
    # JPL Horizons batch query
    params = {
        "format": "json",
        "COMMAND": "'-1024'",       # Orion spacecraft ID
        "OBJ_DATA": "NO",
        "MAKE_EPHEM": "YES",
        "EPHEM_TYPE": "VECTORS",
        "CENTER": "'500@399'",        # Earth center
        "START_TIME": "'2026-04-03'",
        "STOP_TIME": "'2026-04-10'",
        "STEP_SIZE": "'6h'",          # Every 6 hours = 36 snapshots
        "QUANTITIES": "'1,9,20'"      # Position, range, speed
    }

    response = requests.get("https://ssd.jpl.nasa.gov/api/horizons.api", params=params)
    data = response.json()

    result = {
        "extracted_at": datetime.now().isoformat(),
        "source": "JPL Horizons",
        "spacecraft": "Orion Artemis II",
        "raw": data
    }

    os.makedirs("raw_data", exist_ok=True)
    with open("raw_data/orbital_data.json", "w") as f:
        json.dump(result, f, indent=2)

    print("✅ Orbital data fetched and saved to raw_data/orbital_data.json")
    return result

if __name__ == "__main__":
    data = fetch_orbital_data()
    # Print just a snippet so it's readable
    raw_text = data["raw"].get("result", "")
    print(raw_text[:2000])  # First 2000 chars only