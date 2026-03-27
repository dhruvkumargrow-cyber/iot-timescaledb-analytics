import psycopg2
from config import HOST, PORT, DBNAME, USER, PASSWORD

conn = psycopg2.connect(
    host=HOST, port=PORT, dbname=DBNAME,
    user=USER, password=PASSWORD, sslmode="require"
)

print("Creating continuous aggregate (hourly rollups)...")
cur = conn.cursor()
cur.execute("""
    CREATE MATERIALIZED VIEW sensor_hourly
    WITH (timescaledb.continuous) AS
    SELECT
        time_bucket('1 hour', time)  AS bucket,
        sensor_id,
        location,
        AVG(temperature)             AS avg_temp,
        AVG(humidity)                AS avg_humidity,
        AVG(pressure)                AS avg_pressure,
        MAX(temperature)             AS max_temp,
        MIN(temperature)             AS min_temp,
        COUNT(*)                     AS reading_count
    FROM sensor_data
    GROUP BY bucket, sensor_id, location
    WITH NO DATA;
""")
conn.commit()
cur.close()

print("Refreshing aggregate data...")
conn.autocommit = True
cur = conn.cursor()
cur.execute("""
    CALL refresh_continuous_aggregate(
        'sensor_hourly', NULL, NULL
    );
""")
cur.close()

print("Enabling compression...")
conn.autocommit = False
cur = conn.cursor()
cur.execute("""
    ALTER TABLE sensor_data SET (
        timescaledb.compress,
        timescaledb.compress_segmentby = 'sensor_id'
    );
""")
cur.execute("""
    SELECT add_compression_policy(
        'sensor_data', INTERVAL '7 days'
    );
""")
conn.commit()
cur.close()
conn.close()
print("✅ Continuous aggregates and compression policies set up!")