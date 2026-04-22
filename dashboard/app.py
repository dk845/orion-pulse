import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import psycopg2

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

def detect_anomalies(df, column):
    mean = df[column].mean()
    std = df[column].std()
    df["z_score"] = (df[column] - mean) / std
    df["anomaly"] = df["z_score"].abs() > 2
    return df

st.set_page_config(
    page_title="OrionPulse — Artemis II Mission Intelligence",
    layout="wide"
)

st.title("OrionPulse")
st.markdown("Artemis II Mission Intelligence Dashboard — April 1–10, 2026")

flares_df = get_data("SELECT * FROM fact_space_weather")
orbital_df = get_data("SELECT * FROM fact_orbital_data")
news_df = get_data("SELECT * FROM dim_news")

# Clean timestamps
orbital_df["timestamp"] = pd.to_datetime(orbital_df["timestamp"]).dt.strftime("%b %d %H:%M")

# Deduplicate news
news_df = news_df.drop_duplicates(subset=["title"])

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Solar Flares", len(flares_df))
col2.metric("Orbital Snapshots", len(orbital_df))
col3.metric("News Articles", len(news_df))
col4.metric("Max Distance from Earth", f"{get_data('SELECT MAX(distance_from_earth_km) FROM fact_orbital_data').iloc[0,0]:,.0f} km")

st.divider()

# Orbital chart
st.subheader("Orion Distance from Earth Over Time")
orbital_df = detect_anomalies(orbital_df, "distance_from_earth_km")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=orbital_df["timestamp"],
    y=orbital_df["distance_from_earth_km"],
    mode="lines",
    name="Distance",
    line=dict(color="#00d4ff", width=2)
))

anomalies = orbital_df[orbital_df["anomaly"]]
fig.add_trace(go.Scatter(
    x=anomalies["timestamp"],
    y=anomalies["distance_from_earth_km"],
    mode="markers",
    name="Anomaly Detected",
    marker=dict(color="red", size=10, symbol="x")
))

fig.update_layout(
    template="plotly_dark",
    xaxis_title="Date",
    yaxis_title="Distance (km)",
    xaxis=dict(tickangle=-30),
    height=400
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Two column layout for flares and news
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Solar Flares During Mission")
    flares_df["date"] = pd.to_datetime(flares_df["begin_time"]).dt.strftime("%b %d")
    fig2 = px.bar(
        flares_df,
        x="date",
        y="class_type",
        color="class_type",
        labels={"date": "Date", "class_type": "Flare Class"},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig2.update_layout(
        template="plotly_dark",
        height=350,
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_right:
    st.subheader("Mission News Feed")
    for _, row in news_df.head(8).iterrows():
        date = str(row['date'])[:10] if row['date'] else ""
        st.markdown(f"**{date}** — {row['title']}")
        st.divider()

st.caption("Data sources: NASA DONKI API, JPL Horizons, NASA Image Library")