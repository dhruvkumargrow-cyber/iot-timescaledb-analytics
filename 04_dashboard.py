
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os

HOST     = st.secrets.get("DB_HOST", os.environ.get("DB_HOST", ""))
PORT     = int(st.secrets.get("DB_PORT", os.environ.get("DB_PORT", "39045")))
DBNAME   = st.secrets.get("DB_NAME", os.environ.get("DB_NAME", "tsdb"))
USER     = st.secrets.get("DB_USER", os.environ.get("DB_USER", "tsdbadmin"))
PASSWORD = st.secrets.get("DB_PASSWORD", os.environ.get("DB_PASSWORD", ""))

# ── Page config ───────────────────────────────────────
st.set_page_config(
    page_title="IoT Sensor Analytics",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #1C2333;
        border: 1px solid #2D3748;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Metric label */
    [data-testid="metric-container"] label {
        color: #A0AEC0 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    
    /* Metric value */
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #63B3ED !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1A202C;
        border-right: 1px solid #2D3748;
    }

    /* Headers */
    h1, h2, h3 {
        color: #E2E8F0 !important;
    }

    /* Divider */
    hr {
        border-color: #2D3748;
    }

    /* Anomaly table */
    .anomaly-card {
        background-color: #2D1B1B;
        border: 1px solid #FC8181;
        border-radius: 8px;
        padding: 12px;
        margin: 4px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Database connection ───────────────────────────────
@st.cache_resource
def get_conn():
    return psycopg2.connect(
        host=HOST, port=PORT, dbname=DBNAME,
        user=USER, password=PASSWORD, sslmode="require"
    )

conn = get_conn()

# ── Header ────────────────────────────────────────────
st.markdown("""
<div style='text-align: center; padding: 20px 0 10px 0;'>
    <h1 style='font-size: 2.5rem; font-weight: 800; 
    background: linear-gradient(90deg, #63B3ED, #76E4F7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;'>
    🌡️ IoT Sensor Analytics Platform
    </h1>
    <p style='color: #718096; font-size: 1rem; margin-top: 0;'>
    Real-time monitoring · TimescaleDB · AWS Cloud
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Sidebar ───────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    st.divider()

    location = st.selectbox(
        "📍 Location",
        ["All", "Delhi", "Mumbai", "Bangalore", "Chennai"],
        help="Filter by sensor location"
    )

    days = st.slider(
        "📅 Time Range (days)",
        min_value=1, max_value=30, value=7
    )

    metric = st.selectbox(
        "📊 Primary Metric",
        ["avg_temp", "avg_humidity", "avg_pressure"],
        format_func=lambda x: {
            "avg_temp": "🌡️ Temperature (°C)",
            "avg_humidity": "💧 Humidity (%)",
            "avg_pressure": "🔵 Pressure (hPa)"
        }[x]
    )

    st.divider()
    st.markdown("""
    <div style='color: #718096; font-size: 12px;'>
    <b style='color: #A0AEC0;'>About</b><br>
    Built with TimescaleDB hypertables,
    continuous aggregates & compression
    policies on AWS Cloud.<br><br>
    <a href='https://github.com/dhruvkumargrow-cyber/iot-timescaledb-analytics'
    style='color: #63B3ED;'>📦 View on GitHub</a>
    </div>
    """, unsafe_allow_html=True)

# ── Query data ────────────────────────────────────────
where = f"AND location = '{location}'" if location != "All" else ""

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

# ── Empty state check ─────────────────────────────────
if df.empty:
    st.warning(f"⚠️ No sensor data available for the last {days} day(s). Try increasing the time range to 7+ days.")
    st.stop()

st.markdown("### 📊 Live Metrics")
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "🌡️ Avg Temperature",
    f"{df['avg_temp'].mean():.1f} °C",
    f"Max: {df['max_temp'].max():.1f}°C"
)
c2.metric(
    "💧 Avg Humidity",
    f"{df['avg_humidity'].mean():.1f} %"
)
c3.metric(
    "🔵 Avg Pressure",
    f"{df['avg_pressure'].mean():.1f} hPa"
)
c4.metric(
    "📡 Total Readings",
    f"{df['reading_count'].sum():,}"
)
c5.metric(
    "🏙️ Cities Monitored",
    df['location'].nunique()
)

st.divider()

# ── Charts row 1 ──────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📈 Sensor Trends Over Time")
    fig = px.line(
        df, x="bucket", y=metric, color="sensor_id",
        title=None,
        labels={"bucket": "Time", metric: metric.replace("_", " ").title()},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(
        plot_bgcolor="#1C2333",
        paper_bgcolor="#1C2333",
        font_color="#E2E8F0",
        legend_title="Sensor",
        xaxis=dict(gridcolor="#2D3748"),
        yaxis=dict(gridcolor="#2D3748"),
        hovermode="x unified",
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 🗺️ Avg Temp by City")
    loc_df = df.groupby("location")["avg_temp"].mean().reset_index()
    fig2 = px.bar(
        loc_df, x="avg_temp", y="location",
        orientation='h',
        title=None,
        labels={"avg_temp": "Avg Temp (°C)", "location": ""},
        color="avg_temp",
        color_continuous_scale="Blues"
    )
    fig2.update_layout(
        plot_bgcolor="#1C2333",
        paper_bgcolor="#1C2333",
        font_color="#E2E8F0",
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Charts row 2 ──────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown("### 🌡️ Temperature Range by City")
    fig3 = px.box(
        df, x="location", y="avg_temp",
        color="location",
        title=None,
        labels={"avg_temp": "Temperature (°C)", "location": "City"},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig3.update_layout(
        plot_bgcolor="#1C2333",
        paper_bgcolor="#1C2333",
        font_color="#E2E8F0",
        showlegend=False,
        xaxis=dict(gridcolor="#2D3748"),
        yaxis=dict(gridcolor="#2D3748"),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("### 💧 Humidity vs Temperature")
    fig4 = px.scatter(
        df, x="avg_temp", y="avg_humidity",
        color="location", size="reading_count",
        title=None,
        labels={
            "avg_temp": "Temperature (°C)",
            "avg_humidity": "Humidity (%)"
        },
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig4.update_layout(
        plot_bgcolor="#1C2333",
        paper_bgcolor="#1C2333",
        font_color="#E2E8F0",
        xaxis=dict(gridcolor="#2D3748"),
        yaxis=dict(gridcolor="#2D3748"),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Anomaly Detection ─────────────────────────────────
st.markdown("### 🔴 Anomaly Detection — Last 24 Hours")

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
    lambda x: "🔴 Anomaly" if abs(x - mean) > 2 * std else "🟢 Normal"
)
anomalies = raw_df[raw_df["status"] == "🔴 Anomaly"]

a1, a2, a3 = st.columns(3)
a1.metric("Total Readings (24h)", f"{len(raw_df):,}")
a2.metric("🔴 Anomalies", f"{len(anomalies)}", 
          delta=f"{len(anomalies)/len(raw_df)*100:.1f}% of total" if len(raw_df) > 0 else "No data",
          delta_color="inverse")
a3.metric("🟢 Normal", f"{len(raw_df) - len(anomalies):,}")

if len(anomalies) > 0:
    st.dataframe(
        anomalies[["time", "sensor_id", "location", "temperature", "status"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.success("✅ No anomalies detected in the last 24 hours!")

st.divider()

# ── Raw Data ──────────────────────────────────────────
with st.expander("🔍 Explore Raw Hourly Aggregates"):
    st.dataframe(df, use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────
st.markdown("""
<div style='text-align: center; color: #4A5568; 
font-size: 12px; padding: 20px 0;'>
Built by Dhruv Kumar · 
<a href='https://github.com/dhruvkumargrow-cyber' 
style='color: #63B3ED;'>GitHub</a> · 
Powered by TimescaleDB on AWS
</div>
""", unsafe_allow_html=True)