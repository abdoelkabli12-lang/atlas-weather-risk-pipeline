import sys
sys.path.insert(0, "C:/Users/ycode/Documents/atlas-weather-risk-pipeline/load")

from postgres import engine
from sqlalchemy import text

with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS weather_risk CASCADE"))
    print("Dropped weather_risk.")

# Verify
with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT tablename FROM pg_tables WHERE tablename = 'weather_risk'"
    ))
    print("Still exists?", result.fetchall())
