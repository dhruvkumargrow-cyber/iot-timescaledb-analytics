import psycopg2
import random
from datetime import datetime, timedelta
from config import HOST, PORT, DBNAME, USER, PASSWORD

conn = psycopg2.connect(
    host=HOST, port=PORT, dbname=DBNAME,
    user=USER, password=PASSWORD, sslmode="require"
)
cur = conn.cursor()

sensors = [
    ("sensor_1", "Delhi"),
    ("sensor_2", "Mumbai"),
    ("sensor_3", "Bangalore"),
    ("sensor_4", "Chennai"),
]

print("Inserting 10,000 sensor readings...")
now = datetime.utcnow()

base_temp = {
    "Delhi": 38,
    "Mumbai": 32,
    "Bangalore": 26,
    "Chennai": 34
}

for i in range(10000):
    sensor_id, location = random.choice(sensors)

    cur.execute("""
        INSERT INTO sensor_data 
        (time, sensor_id, location, temperature, humidity, pressure)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        now - timedelta(minutes=random.randint(0, 43200)),
        sensor_id,
        location,
        round(base_temp[location] + random.uniform(-5, 5), 2),
        round(random.uniform(30.0, 90.0), 2),
        round(random.uniform(980.0, 1050.0), 2)
    ))

    if (i + 1) % 1000 == 0:
        conn.commit()
        print(f"  Inserted {i+1} rows...")

conn.commit()
cur.close()
conn.close()
print("✅ 10,000 sensor readings inserted!")