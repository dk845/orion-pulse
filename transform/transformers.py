import json
import pandas as pd
import os

def transform_space_weather():
    """Cleans raw solar flare and storm JSON into a flat dataframe"""
    print("Transforming space weather data...")

    with open("raw_data/space_weather.json") as f:
        raw = json.load(f)

    flares = []
    for flare in raw["solar_flares"]:
        flares.append({
            "flare_id": flare.get("flrID"),
            "begin_time": flare.get("beginTime"),
            "peak_time": flare.get("peakTime"),
            "end_time": flare.get("endTime"),
            "class_type": flare.get("classType"),
            "location": flare.get("sourceLocation"),
            "region": flare.get("activeRegionNum"),
        })

    storms = []
    for storm in raw["geomagnetic_storms"]:
        for kp in storm.get("allKpIndex", []):
            storms.append({
                "storm_id": storm.get("gstID"),
                "start_time": storm.get("startTime"),
                "observed_time": kp.get("observedTime"),
                "kp_index": kp.get("kpIndex"),
                "source": kp.get("source"),
            })

    df_flares = pd.DataFrame(flares)
    df_storms = pd.DataFrame(storms)

    os.makedirs("transformed_data", exist_ok=True)
    df_flares.to_csv("transformed_data/solar_flares.csv", index=False)
    df_storms.to_csv("transformed_data/geomagnetic_storms.csv", index=False)

    print(f"✅ {len(df_flares)} solar flares transformed")
    print(f"✅ {len(df_storms)} geomagnetic storm readings transformed")
    print(df_flares.head())
    return df_flares, df_storms


def transform_orbital_data():
    """Parses JPL Horizons raw text into structured position data"""
    print("Transforming orbital data...")

    with open("raw_data/orbital_data.json") as f:
        raw = json.load(f)

    raw_text = raw["raw"].get("result", "")

    # Extract data between $$SOE and $$EOE markers
    start = raw_text.find("$$SOE")
    end = raw_text.find("$$EOE")
    data_block = raw_text[start+5:end].strip()

    records = []
    lines = data_block.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "= A.D." in line:
            try:
                date_part = line.split("= A.D.")[1].strip().split(" TDB")[0].strip()
                x_line = lines[i+1].strip()
                rg_line = lines[i+3].strip() if i+3 < len(lines) else ""

                x = float(x_line.split("X =")[1].split("Y =")[0].strip())
                y = float(x_line.split("Y =")[1].split("Z =")[0].strip())
                z = float(x_line.split("Z =")[1].strip())
                rg = float(rg_line.split("RG=")[1].split("RR=")[0].strip()) if "RG=" in rg_line else None

                records.append({
                    "timestamp": date_part,
                    "x_km": x,
                    "y_km": y,
                    "z_km": z,
                    "distance_from_earth_km": rg
                })
            except:
                pass
        i += 1

    df = pd.DataFrame(records)
    df.to_csv("transformed_data/orbital_positions.csv", index=False)
    print(f"✅ {len(df)} orbital position snapshots transformed")
    print(df.head())
    return df


def transform_nasa_news():
    """Flattens NASA news items into clean table"""
    print("Transforming NASA news...")

    with open("raw_data/nasa_news.json") as f:
        raw = json.load(f)

    articles = []
    for item in raw["articles"]:
        data = item.get("data", [{}])[0]
        articles.append({
            "title": data.get("title"),
            "date": data.get("date_created", "")[:10],
            "description": data.get("description"),
            "nasa_id": data.get("nasa_id"),
        })

    df = pd.DataFrame(articles)
    df.to_csv("transformed_data/nasa_news.csv", index=False)
    print(f"✅ {len(df)} news articles transformed")
    print(df.head())
    return df


if __name__ == "__main__":
    transform_space_weather()
    transform_orbital_data()
    transform_nasa_news()