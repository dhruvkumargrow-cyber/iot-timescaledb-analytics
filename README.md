# 🌡️ IoT Sensor Analytics — TimescaleDB

Real-time IoT sensor analytics platform built on TimescaleDB and Streamlit.

## 🚀 Features
- **Hypertable** — time-series data auto-partitioned by time chunks
- **Continuous Aggregates** — pre-computed hourly rollups for fast queries
- **Compression Policies** — auto-compress data older than 7 days
- **Anomaly Detection** — flags readings 2+ std deviations from mean
- **Live Dashboard** — interactive Streamlit + Plotly visualizations

## 🛠️ Tech Stack
TimescaleDB · PostgreSQL · Python · Streamlit · Plotly · Pandas · psycopg2

## ⚙️ Setup
1. Clone the repo
2. Copy `config.example.py` to `config.py` and fill in your TimescaleDB credentials
3. Install dependencies:
   pip install psycopg2-binary pandas streamlit plotly
4. Run in order:
   - python 01_setup_db.py
   - python 02_generate_data.py
   - python 03_setup_policies.py
   - streamlit run 04_dashboard.py

## 📊 Dashboard
- KPI cards: Avg Temperature, Humidity, Pressure, Total Readings
- Sensor trend lines across 4 Indian cities over time
- Location-wise temperature comparison bar chart
- Real-time anomaly detection on last 24 hours of data