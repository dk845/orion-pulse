import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "port": "5433",
    "database": "airflow",
    "user": "airflow",
    "password": "airflow"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_tables():
    """Creates all tables in PostgreSQL if they don't exist"""
    print("Creating tables...")
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fact_space_weather (
            flare_id VARCHAR PRIMARY KEY,
            begin_time VARCHAR,
            peak_time VARCHAR,
            end_time VARCHAR,
            class_type VARCHAR,
            location VARCHAR,
            region VARCHAR
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fact_orbital_data (
            timestamp VARCHAR PRIMARY KEY,
            x_km FLOAT,
            y_km FLOAT,
            z_km FLOAT,
            distance_from_earth_km FLOAT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_news (
            nasa_id VARCHAR PRIMARY KEY,
            title VARCHAR,
            date VARCHAR,
            description TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS fact_geomagnetic_storms (
            storm_id VARCHAR,
            start_time VARCHAR,
            observed_time VARCHAR PRIMARY KEY,
            kp_index FLOAT,
            source VARCHAR
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ All tables created")

def load_all():
    """Loads all transformed CSVs into PostgreSQL"""
    create_tables()
    conn = get_connection()

    # Solar flares
    df = pd.read_csv("transformed_data/solar_flares.csv")
    for _, row in df.iterrows():
        conn.cursor().execute("""
            INSERT INTO fact_space_weather VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (flare_id) DO NOTHING
        """, tuple(row))
    conn.commit()
    print(f"✅ {len(df)} solar flares loaded")

    # Orbital data
    df = pd.read_csv("transformed_data/orbital_positions.csv")
    for _, row in df.iterrows():
        conn.cursor().execute("""
            INSERT INTO fact_orbital_data VALUES (%s,%s,%s,%s,%s)
            ON CONFLICT (timestamp) DO NOTHING
        """, tuple(row))
    conn.commit()
    print(f"✅ {len(df)} orbital positions loaded")

    # News
    df = pd.read_csv("transformed_data/nasa_news.csv")
    for _, row in df.iterrows():
        conn.cursor().execute("""
            INSERT INTO dim_news VALUES (%s,%s,%s,%s)
            ON CONFLICT (nasa_id) DO NOTHING
        """, tuple(row[["nasa_id","title","date","description"]]))
    conn.commit()
    print(f"✅ {len(df)} news articles loaded")

    conn.close()
    print("🚀 All data loaded into PostgreSQL!")

if __name__ == "__main__":
    load_all()