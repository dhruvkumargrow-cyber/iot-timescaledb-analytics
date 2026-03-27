import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
from config import HOST, PORT, DBNAME, USER, PASSWORD

st.set_page_config(
    page_title="IoT Sensor Dashboard",
    page_icon="🌡️",
    layout="wide"
)

@st.cache_resource
def get_conn():
    return psycopg2.connect(
        host=HOST, port=PORT, dbname=DBNAME,
        user=USER, password=PASSWORD, sslmode="require"
    )

conn = get_conn()

# ── Header ──────────────────────────────────────────
st.title("🌡️ IoT Sensor Analytics — TimescaleDB")
st.caption("Real-time dashboard powered by TimescaleDB "
           "hypertables and continuous aggregates")

# ── Sidebar filters ──────────────────────────────────
st.sidebar.header("Filters")
location = st.sidebar.selectbox(
    "Location",
    ["All", "Delhi", "Mumbai", "Bangalore", "Chennai"]
)
days = st.sidebar.slider("Last N days", 1, 30, 7)
metric = st.sidebar.selectbox(
    "Metric to plot",
    ["avg_temp", "avg_humidity", "avg_pressure"]
)

# ── Query continuous aggregate ────────────────────────
where = f"AND location = '{location}'" \
        if location != "All" else ""

df = pd.read_sql(f"""
    SELECT bucket, sensor_id, location,
           avg_temp, avg_humidity, avg_pressure,
           max_temp, min_temp, reading_count
    FROM sensor_hourly
    WHERE bucket > NOW() - INTERVAL '{days} days'
    {where}
    ORDER BY bucket;
""", conn)

# ── KPI Cards ─────────────────────────────────────────
st.subheader("📊 Key Metrics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg Temperature",
          f"{df['avg_temp'].mean():.1f} °C")
c2.metric("Avg Humidity",
          f"{df['avg_humidity'].mean():.1f} %")
c3.metric("Avg Pressure",
          f"{df['avg_pressure'].mean():.1f} hPa")
c4.metric("Total Readings",
          f"{df['reading_count'].sum():,}")

st.divider()

# ── Trend Chart ───────────────────────────────────────
st.subheader("📈 Sensor Trends Over Time")
fig = px.line(
    df, x="bucket", y=metric, color="sensor_id",
    title=f"{metric.replace('_',' ').title()} "
          f"— Last {days} Days",
    labels={"bucket": "Time", metric: metric}
)
st.plotly_chart(fig, use_container_width=True)

# ── Location Comparison Bar Chart ─────────────────────
st.subheader("🗺️ Average Temperature by Location")
loc_df = df.groupby("location")["avg_temp"] \
           .mean().reset_index()
fig2 = px.bar(
    loc_df, x="location", y="avg_temp",
    color="location",
    title="Average Temperature by City",
    labels={"avg_temp": "Avg Temp (°C)"}
)
st.plotly_chart(fig2, use_container_width=True)

# ── Anomaly Detection ─────────────────────────────────
st.subheader("🔴 Anomaly Detection (Last 24 Hours)")
raw_df = pd.read_sql("""
    SELECT time, sensor_id, location, temperature
    FROM sensor_data
    WHERE time > NOW() - INTERVAL '24 hours'
    ORDER BY time DESC
    LIMIT 1000;
""", conn)

mean = raw_df["temperature"].mean()
std  = raw_df["temperature"].std()
raw_df["status"] = raw_df["temperature"].apply(
    lambda x: "🔴 Anomaly"
    if abs(x - mean) > 2 * std else "🟢 Normal"
)
anomalies = raw_df[raw_df["status"] == "🔴 Anomaly"]
st.write(f"Detected **{len(anomalies)}** anomalies "
         f"out of {len(raw_df)} readings")
st.dataframe(anomalies, use_container_width=True)

# ── Raw Data Explorer ─────────────────────────────────
with st.expander("🔍 Explore Raw Hourly Aggregates"):
    st.dataframe(df, use_container_width=True)