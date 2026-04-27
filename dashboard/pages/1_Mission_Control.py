import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import psycopg2
import time
from datetime import datetime

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

st.set_page_config(
    page_title="Mission Control — OrionPulse",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .live-badge {
        background: #e53e3e;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #00d4ff;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)

col_title, col_badge = st.columns([4, 1])
with col_title:
    st.title("Mission Control")
    st.markdown("Artemis II — Simulated Live Orbital Feed")
with col_badge:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<span class='live-badge'>LIVE</span>", unsafe_allow_html=True)

st.divider()

orbital_df = get_data("SELECT * FROM fact_orbital_data ORDER BY timestamp")
orbital_df["timestamp"] = pd.to_datetime(orbital_df["timestamp"])
flares_df = get_data("SELECT * FROM fact_space_weather ORDER BY begin_time")

placeholder = st.empty()

for i in range(1, len(orbital_df) + 1):
    current_df = orbital_df.iloc[:i]
    current_row = orbital_df.iloc[i - 1]

    with placeholder.container():
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("<div class='metric-label'>Mission Day</div>", unsafe_allow_html=True)
            day = (current_row["timestamp"] - orbital_df["timestamp"].min()).days + 1
            st.markdown(f"<div class='metric-value'>Day {day}</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='metric-label'>Distance from Earth</div>", unsafe_allow_html=True)
            dist = current_row["distance_from_earth_km"]
            st.markdown(f"<div class='metric-value'>{dist:,.0f} km</div>", unsafe_allow_html=True)

        with col3:
            st.markdown("<div class='metric-label'>Active Flares</div>", unsafe_allow_html=True)
            active = len(flares_df[flares_df["begin_time"] <= str(current_row["timestamp"])])
            st.markdown(f"<div class='metric-value'>{active}</div>", unsafe_allow_html=True)

        with col4:
            st.markdown("<div class='metric-label'>Last Updated</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-value' style='font-size:1.2rem'>{datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

        st.divider()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=current_df["timestamp"],
            y=current_df["distance_from_earth_km"],
            mode="lines+markers",
            line=dict(color="#00d4ff", width=2),
            marker=dict(size=4),
            name="Distance"
        ))
        fig.add_trace(go.Scatter(
            x=[current_row["timestamp"]],
            y=[current_row["distance_from_earth_km"]],
            mode="markers",
            marker=dict(color="#fc8181", size=14, symbol="circle"),
            name="Orion Now"
        ))
        fig.add_hline(
            y=384400,
            line_dash="dash",
            line_color="#f6e05e",
            annotation_text="Moon Distance",
            annotation_position="bottom right"
        )
        fig.update_layout(
            template="plotly_dark",
            height=380,
            xaxis_title="Mission Time",
            yaxis_title="Distance from Earth (km)",
            showlegend=True,
            plot_bgcolor="#0a0a0f",
            paper_bgcolor="#0a0a0f",
            title="Live Orbital Tracking — Orion Spacecraft"
        )
        st.plotly_chart(fig, use_container_width=True)

        current_flares = flares_df[
            flares_df["begin_time"] <= str(current_row["timestamp"])
        ]
        if not current_flares.empty:
            last_flare = current_flares.iloc[-1]
            severity = "MODERATE" if last_flare["class_type"].startswith("M") else "MINOR"
            color = "#f6ad55" if severity == "MODERATE" else "#68d391"
            st.markdown(f"""
            <div style='background:#1a1a2e; border-left: 4px solid {color}; 
            padding: 12px 20px; border-radius: 4px; margin-top: 10px;'>
                <strong>Latest Solar Event:</strong> {last_flare['class_type']} class flare 
                detected at {str(last_flare['begin_time'])[:16]} — Severity: {severity}
            </div>
            """, unsafe_allow_html=True)

    time.sleep(0.8)

st.success("Mission data stream complete — all 29 orbital snapshots replayed.")