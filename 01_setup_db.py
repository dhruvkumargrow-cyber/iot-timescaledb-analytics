import psycopg2
from config import HOST, PORT, DBNAME, USER, PASSWORD

conn = psycopg2.connect(
    host=HOST, port=PORT, dbname=DBNAME,
    user=USER, password=PASSWORD, sslmode="require"
)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data (
        time        TIMESTAMPTZ NOT NULL,
        sensor_id   TEXT        NOT NULL,
        location    TEXT        NOT NULL,
        temperature DOUBLE PRECISION,
        humidity    DOUBLE PRECISION,
        pressure    DOUBLE PRECISION
    );
""")

cur.execute("""
    SELECT create_hypertable(
        'sensor_data', 'time',
        if_not_exists => TRUE
    );
""")

conn.commit()
cur.close()
conn.close()
print("✅ Table and hypertable created successfully!")