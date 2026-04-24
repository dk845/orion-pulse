import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
import requests
import os
from dotenv import load_dotenv

load_dotenv()
NASA_API_KEY = os.getenv("NASA_API_KEY")

DB_CONFIG = {
    "host": "localhost",
    "port": "5433",
    "database": "airflow",
    "user": "airflow",
    "password": "airflow"
}

def get_data(query):
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def fetch_mission_images(query, count=6):
    url = f"https://images-api.nasa.gov/search?q={query}&media_type=image&year_start=2026&year_end=2026"
    r = requests.get(url)
    items = r.json().get("collection", {}).get("items", [])
    images = []
    for item in items[:count]:
        links = item.get("links", [])
        data = item.get("data", [{}])[0]
        if links:
            images.append({
                "url": links[0].get("href"),
                "title": data.get("title", ""),
                "date": data.get("date_created", "")[:10]
            })
    return images

def fetch_artemis1_images(count=6):
    url = "https://images-api.nasa.gov/search?q=Artemis+I&media_type=image"
    r = requests.get(url)
    items = r.json().get("collection", {}).get("items", [])
    images = []
    for item in items[:count]:
        links = item.get("links", [])
        data = item.get("data", [{}])[0]
        if links:
            images.append({
                "url": links[0].get("href"),
                "title": data.get("title", ""),
                "date": data.get("date_created", "")[:10]
            })
    return images

st.set_page_config(
    page_title="OrionPulse — Artemis II",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .health-green { color: #48bb78; font-size: 1.2rem; font-weight: bold; }
    .health-yellow { color: #ecc94b; font-size: 1.2rem; font-weight: bold; }
    .health-red { color: #fc8181; font-size: 1.2rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("OrionPulse")
st.markdown("### Artemis II — Humanity's Return to the Moon")
st.markdown("*April 1–10, 2026 — First crewed lunar mission in 50 years*")
st.divider()

flares_df = get_data("SELECT * FROM fact_space_weather")
orbital_df = get_data("SELECT * FROM fact_orbital_data")
health_df = get_data("SELECT * FROM agg_mission_health ORDER BY mission_date")
correlations_df = get_data("SELECT * FROM agg_event_correlations LIMIT 20")

orbital_df["timestamp"] = pd.to_datetime(orbital_df["timestamp"])

st.subheader("Mission at a Glance")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Days in Space", "10")
col2.metric("Max Distance from Earth", f"{orbital_df['distance_from_earth_km'].max():,.0f} km")
col3.metric("Solar Flares During Mission", len(flares_df))
col4.metric("Ground Station Dishes", "14")
col5.metric("Orbital Snapshots", len(orbital_df))

st.divider()

# Crew
st.subheader("The Crew — Artemis II")
st.markdown("*Reid Wiseman (Commander) · Victor Glover (Pilot) · Christina Koch · Jeremy Hansen (CSA)*")

crew_col1, crew_col2 = st.columns([1, 2])
with crew_col1:
    st.image(
        "https://images-assets.nasa.gov/image/art002e009302/art002e009302~thumb.jpg",
        caption="All four crew members inside Orion during the lunar flyby — April 6, 2026",
        width=450
    )
with crew_col2:
    st.markdown("""
    **Commander:** Reid Wiseman  
    **Pilot:** Victor Glover  
    **Mission Specialist:** Christina Koch  
    **Mission Specialist:** Jeremy Hansen (CSA)

    On April 1, 2026, these four astronauts became the first humans to travel beyond low Earth orbit since Apollo 17 in 1972.
    At their farthest point, they were **252,756 miles from Earth** — a new record for human spaceflight.

    They splashed down on April 10, 2026, off the coast of San Diego after nearly 10 days in deep space.
    """)

st.divider()

# Orbital journey
st.subheader("Orion's Journey — Distance from Earth")
st.markdown("*Watch Orion travel 412,000 km to the Moon and return home*")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=orbital_df["timestamp"],
    y=orbital_df["distance_from_earth_km"],
    mode="lines+markers",
    line=dict(color="#00d4ff", width=3),
    marker=dict(size=5)
))
fig.add_hline(
    y=384400,
    line_dash="dash",
    line_color="#f6e05e",
    annotation_text="Average Moon Distance (384,400 km)",
    annotation_position="bottom right"
)
fig.update_layout(
    template="plotly_dark",
    height=400,
    xaxis_title="Mission Day",
    yaxis_title="Distance from Earth (km)",
    showlegend=False,
    plot_bgcolor="#0a0a0f",
    paper_bgcolor="#0a0a0f"
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Orbital trajectory
st.subheader("Orion's Trajectory — The Path to the Moon and Back")
st.markdown("*The actual route Orion took: Earth → Moon flyby → return*")

trajectory_col1, trajectory_col2 = st.columns([2, 1])
with trajectory_col1:
    fig_traj = px.scatter(
        orbital_df,
        x="x_km",
        y="y_km",
        color="distance_from_earth_km",
        color_continuous_scale="Blues",
        labels={"x_km": "X Position (km)", "y_km": "Y Position (km)", "distance_from_earth_km": "Distance from Earth (km)"},
        title="Orion's Orbital Path (Top View)"
    )
    fig_traj.add_scatter(
        x=[0], y=[0],
        mode="markers+text",
        marker=dict(color="blue", size=20),
        text=["Earth"],
        textposition="top center",
        name="Earth"
    )
    fig_traj.update_layout(
        template="plotly_dark",
        height=400,
        plot_bgcolor="#0a0a0f",
        paper_bgcolor="#0a0a0f"
    )
    st.plotly_chart(fig_traj, use_container_width=True)

with trajectory_col2:
    st.markdown("""
    **Mission Profile:**

    - Launch: Apr 1, 6:35 PM EDT
    - Translunar injection: Apr 3
    - Lunar flyby: Apr 6
    - Max distance: 252,756 miles
    - Splashdown: Apr 10, 8:07 PM EDT

    **Record broken:**  
    Farthest humans have ever traveled in space
    """)

st.divider()

# Mission health
st.subheader("Daily Mission Health")
st.markdown("*Based on solar activity and space weather conditions*")

for _, row in health_df.iterrows():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown(f"**{str(row['mission_date'])[:10]}**")
    with col2:
        score = max(0, min(int(row['health_score']) if row['health_score'] is not None else 100, 100))
        st.progress(score / 100)
    with col3:
        health = row['mission_health']
        if health == 'GREEN':
            st.markdown("<span class='health-green'>Good</span>", unsafe_allow_html=True)
        elif health == 'YELLOW':
            st.markdown("<span class='health-yellow'>Caution</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='health-red'>Alert</span>", unsafe_allow_html=True)

# Real mission photos
st.subheader("Photos Taken During the Mission")
st.markdown("*Actual images captured by the crew from inside Orion*")

mission_photos = [
    {
        "url": "https://images-assets.nasa.gov/image/art002e000193/art002e000193~thumb.jpg",
        "caption": "Apr 3 — Earth backlit, taken by Commander Reid Wiseman"
    },
    {
        "url": "https://images-assets.nasa.gov/image/art002e004462/art002e004462~thumb.jpg",
        "caption": "Apr 4 — Earth illuminated against the blackness of space"
    },
    {
        "url": "https://images-assets.nasa.gov/image/art002e009283/art002e009283~thumb.jpg",
        "caption": "Apr 6 — Lunar surface during flyby, Vavilov Crater region"
    },
    {
        "url": "https://images-assets.nasa.gov/image/art002e009288/art002e009288~thumb.jpg",
        "caption": "Apr 6 — Earthset through Orion spacecraft window"
    },
    {
        "url": "https://images-assets.nasa.gov/image/art002e009301/art002e009301~thumb.jpg",
        "caption": "Apr 6 — Total solar eclipse seen from behind the Moon"
    },
    {
        "url": "https://images-assets.nasa.gov/image/art002e016354/art002e016354~thumb.jpg",
        "caption": "Apr 8 — Thin lunar crescent as crew travels back to Earth"
    },
]

cols = st.columns(3)
for i, photo in enumerate(mission_photos):
    with cols[i % 3]:
        st.image(photo["url"], caption=photo["caption"], width=380)

st.divider()

# Artemis I vs II
st.subheader("Artemis I vs Artemis II")
st.markdown("*From uncrewed test flight to humanity's return to the Moon*")

comp_col1, comp_col2 = st.columns(2)
with comp_col1:
    st.markdown("**Artemis I — November 2022**")
    st.markdown("Uncrewed test flight · 25.5 days · 1.4 million miles")
    art1_images = fetch_artemis1_images(count=2)
    for img in art1_images:
        st.image(img["url"], caption=img["title"][:70], width=380)

with comp_col2:
    st.markdown("**Artemis II — April 2026**")
    st.markdown("First crewed flight · 10 days · 252,756 miles from Earth")
    art2_images = fetch_mission_images("Artemis II crew", count=2)
    for img in art2_images:
        st.image(img["url"], caption=img["title"][:70], width=380)

st.divider()

# Solar weather
st.subheader("Space Weather During the Mission")
st.markdown("*Solar flares that occurred while the crew was in deep space*")

flares_df["date"] = pd.to_datetime(flares_df["begin_time"]).dt.strftime("%b %d")
flares_df["severity"] = flares_df["class_type"].apply(
    lambda x: "Strong" if x.startswith("X") else ("Moderate" if x.startswith("M") else "Minor")
)

fig2 = px.scatter(
    flares_df,
    x="date",
    y="class_type",
    color="severity",
    color_discrete_map={"Strong": "#fc8181", "Moderate": "#f6ad55", "Minor": "#68d391"},
    labels={"date": "Date", "class_type": "Flare Class", "severity": "Severity"}
)
fig2.update_layout(
    template="plotly_dark",
    height=300,
    plot_bgcolor="#0a0a0f",
    paper_bgcolor="#0a0a0f"
)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

if not correlations_df.empty:
    st.subheader("Solar-Orbital Event Correlations")
    st.markdown("*Moments where solar activity coincided with orbital maneuvers*")
    interference = correlations_df[correlations_df["correlation_flag"] == "POSSIBLE_INTERFERENCE"]
    st.markdown(f"**{len(interference)} potential interference events detected** during the mission")
    for _, row in interference.head(5).iterrows():
        st.markdown(f"- **{str(row['flare_time'])[:16]}** — {row['flare_class']} flare, Orion at {row['distance_from_earth_km']:,.0f} km from Earth")

st.divider()
st.caption("Data: NASA DONKI API · JPL Horizons · NASA Image Library · DSN Now | Built with OrionPulse")