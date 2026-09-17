from dotenv import load_dotenv
import os
from sqlalchemy import Table, MetaData, select, text
from postgres import engine
import pandas as pd
from collections import defaultdict

metadata = MetaData()


cities = pd.read_csv("C:/Users/ycode/Documents/atlas-weather-risk-pipeline/data/bronze/cities/morocco_cities.csv")
df_cities = pd.DataFrame(cities)
weather_clean = pd.read_csv("C:/Users/ycode/Documents/atlas-weather-risk-pipeline/data/silver/weather_clean.csv")
df_weather1 = pd.DataFrame(weather_clean)
weather_risk = pd.read_csv("C:/Users/ycode/Documents/atlas-weather-risk-pipeline/data/gold/weather_risk.csv")
df_risk = pd.DataFrame(weather_risk)


with engine.begin() as conn:
    conn.execute(text("TRUNCATE weather_forecasts, cities RESTART IDENTITY CASCADE"))
    conn.execute(text("DROP TABLE IF EXISTS weather_risk CASCADE;"))

df_cities.to_sql("cities",
                engine,
                if_exists="append",
                index=False
                )


cities = Table('cities',
              metadata, 
            autoload_with=engine
              )

stmt = select(cities.c.city_id, cities.c.city)


rows = defaultdict(list)

with engine.connect() as conn:
  
    for row in conn.execute(stmt):
      
      rows["city_id"].append(row.city_id)
      
      rows["city"].append(row.city)

df_weather_temp = pd.DataFrame({
  "city_id": rows["city_id"],
  "city": rows["city"]
})  
    

df_weather = pd.merge(df_weather_temp, df_weather1, how="inner", on = "city")

df_weather = df_weather.drop(["city", "latitude", "longitude"], axis=1)

df_weather.rename(columns={"date": "forecast_date"}, inplace=True)

df_weather.to_sql("weather_forecasts", engine, if_exists="append", index=False)



weather = Table('weather_forecasts',
              metadata, 
            autoload_with=engine
              )

weather_table = select(weather.c.weather_id)


r = defaultdict(list)
with engine.connect() as conn:
  
    for row in conn.execute(weather_table):
      r["weather_id"].append(row.weather_id)
      
df_weather_risk_temp = pd.DataFrame({
  "weather_id":r["weather_id"], 
})

df_weather_risk = pd.merge(df_weather_risk_temp, df_risk, how="inner", on="weather_id")

# Select + rename to match the table schema
df_weather_risk = df_weather_risk[[
    "weather_id",
    "temp_category",
    "prec_category",
    "wind_category",
    "risk_score",
    "risk_level"
]].rename(columns={
    "temp_category": "temperature_category",
    "prec_category": "precipitation_category"
})

df_weather_risk.to_sql("weather_risk", engine, if_exists="append", index=False)
