import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from sqlalchemy import Table, MetaData, select, text, join
from load.postgres import engine
from altair.datasets import data
from streamlit_searchbox import st_searchbox
"""
# My first app
Here's our first attempt at using data to create a table:
"""

# Number of cities ✅
# Maximum temperature ✅
# Maximum precipitation ✅
# Number of high-risk periods ✅
# City with the highest risk ✅


with engine.connect() as conn:
    num_city = conn.execute(text("SELECT COUNT(*) FROM cities")).scalar()
    max_temp = conn.execute(text("SELECT c.city, MAX(f.temp_max) AS mx FROM cities c JOIN weather_forecasts f ON c.city_id = f.city_id GROUP BY c.city ORDER BY mx DESC LIMIT 1;")).fetchone()
    max_precip = conn.execute(text("SELECT MAX(precipitation) FROM weather_forecasts")).scalar()
    num_risk = conn.execute(text("SELECT COUNT(*) FILTER (WHERE r.risk_score > (SELECT AVG(risk_score) FROM weather_risk)) AS high_risk_periods FROM weather_forecasts f JOIN weather_risk r ON f.weather_id = r.weather_id;")).scalar()
    highest_risk = conn.execute(text("SELECT c.city, r.risk_score FROM weather_risk r JOIN weather_forecasts f ON r.weather_id = f.weather_id  JOIN cities c ON f.city_id = c.city_id ORDER BY r.risk_score DESC LIMIT 1")).fetchone()

metadata = MetaData()
cities = Table("cities", metadata, autoload_with=engine)
w = Table("weather_forecasts", metadata, autoload_with=engine)
r = Table("weather_risk", metadata, autoload_with=engine)

df_city = pd.read_sql(select(cities.c.city_id, cities.c.city, cities.c.lat, cities.c.lng), engine)
df_date = pd.read_sql(select(w.c.forecast_date, cities.c.city, r).join(cities, w.c.city_id == cities.c.city_id).join(r, w.c.weather_id == r.c.weather_id), engine)

st.metric("Number of cities", num_city)

st.metric(
    label=f"Max temperature ({max_temp.city})",
    value=f"{max_temp.mx} °C"
)

st.metric("Maximum precipitation", f"{max_precip} mm")

st.metric("High-risk periods", num_risk)

st.metric(f"Highest-risk city ({highest_risk.city})", value=f"{highest_risk.risk_score:.1f}")

city_filter = st.multiselect(label="choose a city:", key="name", options=df_city['city'])


if city_filter:
    st.write(df_city[df_city['city'].isin(city_filter)])
else:
    st.write("no filters ar applied")

date_filter = st.multiselect(label="choose a date", key="date", options=df_date['forecast_date'])

if date_filter:
    st.write(df_date[df_date['forecast_date'].isin(date_filter)])
else:
    st.write("no filters ar applied")