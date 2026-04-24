# OrionPulse

An automated data engineering pipeline that unifies four separate NASA data sources from the Artemis II mission into a single queryable intelligence database. Artemis II was NASA's first crewed lunar mission in over 50 years, launching April 1, 2026. During the 10-day mission, data was generated across completely separate NASA systems with no unified record of what happened. OrionPulse solves that.

---

## The Problem

During the Artemis II mission, four independent NASA systems were generating data simultaneously:

- Solar flares and radiation events that could endanger the crew (NASA DONKI)
- Ground stations across three continents communicating with Orion (NASA DSN Now)
- The spacecraft traveling 412,784 km from Earth (JPL Horizons)
- Official mission updates being published every few hours (NASA Image Library)

None of this data talked to each other. There was no unified, queryable historical record of what happened during the mission. OrionPulse builds that record.

---

## Architecture
NASA DONKI API ──────────────┐
JPL Horizons API ────────────┤
NASA DSN Now (XML) ──────────┼──► Python Extractors ──► Raw JSON/XML(local)
NASA Image Library API ──────┘                                              │
│
Pandas Transform
│
PostgreSQL
│
dbt Models
│
┌─────────────────┼─────────────────┐
Anomaly            Correlation        Mission
Detection            Engine          Health Score
│
Streamlit Dashboard
All orchestrated by Apache Airflow, containerized with Docker.

---

## Tech Stack

| Layer | Technology | Purpose |
| Orchestration | Apache Airflow 2.8.1 | Schedules pipeline daily, monitors every task, auto-retries on failure |
| Extraction | Python + Requests | Hits all 4 NASA APIs and pulls raw data |
| Raw Storage | Local filesystem | Raw API responses stored as JSON files before transformation |
| Transformation | Python + Pandas | Cleans and structures raw data into CSVs |
| Analytics Layer | dbt | SQL models that aggregate and join clean data |
| Database | PostgreSQL 15 | Final structured storage across 6 tables |
| Intelligence | scikit-learn | Isolation Forest ML model for multi-feature anomaly detection |
| Dashboard | Streamlit + Plotly | Interactive web app with real NASA mission imagery |
| Containerization | Docker Compose | Runs Airflow and PostgreSQL together with one command |



## Data Sources

| Source | What it provides | Format |
| NASA DONKI API | Solar flares and geomagnetic storms during the mission | REST/JSON |
| JPL Horizons API | Orion spacecraft position, velocity, and distance from Earth every 6 hours | Batch/Text |
| NASA DSN Now | Ground station dish contacts and signal data | XML |
| NASA Image Library | Official mission news and imagery | REST/JSON |

The JPL Horizons extractor uses spacecraft ID -1024, which is the official identifier for the Artemis II Orion spacecraft.

---

## Project Structure
orion_pulse/
├── dags/
│   └── orion_pipeline.py            Airflow DAG orchestrating all tasks on a daily schedule
├── dashboard/
│   └── app.py                       Streamlit dashboard with real NASA imagery and Plotly charts
├── extract/
│   ├── space_weather.py             NASA DONKI API — solar flares and geomagnetic storms
│   ├── dsn_tracker.py               NASA DSN Now XML — ground station dish contacts
│   ├── orbital_data.py              JPL Horizons batch API — Orion position every 6 hours
│   ├── nasa_news.py                 NASA Image Library — official mission news and imagery
│   └── isolation_forest.py          Isolation Forest ML model for multi-feature anomaly detection
├── load/
│   └── loader.py                    PostgreSQL loader with idempotent ON CONFLICT DO NOTHING inserts
├── orionpulse/                      dbt project
│   └── models/
│       ├── agg_mission_summary.sql      Daily rollup of distance and flare count per mission day
│       ├── agg_mission_health.sql       Composite health score — GREEN, YELLOW, RED per day
│       ├── agg_event_correlations.sql   Solar flare vs orbital event correlation engine
│       ├── agg_anomalies.sql            Z-score anomaly detection on orbital metrics in SQL
│       └── agg_mission_comparison.sql   Multi-mission comparison framework
├── raw_data/                        Raw JSON and XML responses from NASA APIs
├── tests/
│   └── test_extractors.py           Basic extractor tests
├── transform/
│   └── transformers.py              Pandas cleaning pipeline for all 4 data sources
├── transformed_data/                Cleaned CSVs ready for PostgreSQL loading
├── docker-compose.yml               Spins up Airflow and PostgreSQL in one command
├── requirements.txt                 All Python dependencies
└── .env                             NASA API key — not committed to Git

---
---

## Database Schema

### Fact Tables

**fact_space_weather** — Every solar flare during the mission with class type, timing, source location, and active region number

**fact_orbital_data** — Orion's position in 3D space (X, Y, Z coordinates in km) and distance from Earth, captured every 6 hours from April 3 to April 10

**fact_geomagnetic_storms** — Geomagnetic storm events with Kp index readings from NOAA

### Dimension Tables

**dim_news** — Official NASA Artemis II news articles and imagery metadata from the NASA Image Library

### dbt Aggregation Models

**agg_mission_summary** — Daily rollup joining orbital distance with solar flare counts per mission day

**agg_mission_health** — Composite mission health score per day. X-class flares score 3, M-class score 2, C-class score 1. Score above 4 is RED, above 2 is YELLOW, below 2 is GREEN.

**agg_event_correlations** — Cross-joins solar flare timestamps with orbital snapshots and flags any pair within 6 hours as a possible interference event

**agg_anomalies** — Z-score detection directly in SQL, flagging orbital metrics deviating more than 2 standard deviations from the mission mean

**agg_mission_comparison** — Structured for multi-mission analysis, ready to ingest Artemis I data for side-by-side comparison

---

## Intelligence Layer

### Anomaly Detection

Two approaches are implemented. The SQL-based Z-score model in `agg_anomalies.sql` flags deviations directly in PostgreSQL. The Python-based Isolation Forest in `isolation_forest.py` uses scikit-learn to detect anomalies across all orbital features simultaneously — X, Y, Z position and distance. It detected 3 anomalies during the early mission phase corresponding to Orion's rapid acceleration after translunar injection.

### Event Correlation Engine

`agg_event_correlations.sql` cross-joins solar flare timestamps with orbital snapshots and flags any pair of events within 6 hours of each other as a possible interference event. This allows analysts to investigate whether communication or navigation anomalies coincided with solar activity.

### Mission Health Score

Daily health scoring based on solar severity. Produces a GREEN, YELLOW, or RED status per mission day with a numeric score from 0 to 100.

---

## What the Data Shows

- 11 solar flares occurred while the crew was in deep space, including an M7.5 class flare on April 4 while Orion was 206,000 km from Earth
- 2 geomagnetic storms hit Earth during the mission, with the strongest reaching Kp 6.67 on April 3
- Orion reached a maximum distance of 412,784 km from Earth, peaking around April 6 during the lunar flyby
- 14 NASA Deep Space Network dishes tracked Orion across ground stations on three continents
- The Isolation Forest model flagged the first 3 orbital snapshots as anomalous, corresponding to the rapid acceleration phase after translunar injection

---

## Running Locally

Prerequisites: Docker Desktop, Python 3.12, Git

```bash
git clone https://github.com/dk845/orion-pulse.git
cd orion_pulse

# Add your NASA API key
echo "NASA_API_KEY=your_key_here" > .env

# Start Airflow and PostgreSQL
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Run the full pipeline
python extract/space_weather.py
python extract/orbital_data.py
python extract/nasa_news.py
python extract/dsn_tracker.py
python transform/transformers.py
python load/loader.py

# Run dbt models
cd orionpulse
dbt run

# Launch dashboard
cd ..
python -m streamlit run dashboard/app.py
```

Airflow UI is available at http://localhost:8080

---

## Mission Context

Artemis II launched on April 1, 2026, carrying NASA astronauts Reid Wiseman (Commander), Victor Glover (Pilot), Christina Koch (Mission Specialist), and CSA astronaut Jeremy Hansen (Mission Specialist). It was the first crewed lunar mission since Apollo 17 in December 1972. The crew splashed down on April 10, 2026, off the coast of San Diego, having traveled a record 252,756 miles from Earth — the farthest any humans have ever been from our planet.

---

## Data Sources and Attribution

All data is sourced from publicly available NASA APIs. No authentication beyond a free NASA API key is required. Keys are available at api.nasa.gov