import pandas as pd
import streamlit as st

from sqlalchemy import MetaData, Table, select
from load.postgres import engine


# PAGE CONFIG


st.set_page_config(
    page_title="Atlas Weather Risk",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# SIMPLE DARK BACKGROUND


st.markdown(
    """
    <style>
    .stApp {
        background: #050810;
        color: #f8fafc;
    }
    section[data-testid="stSidebar"] {
        background: #0a0f1a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# DB


metadata = MetaData()

cities = Table("cities", metadata, autoload_with=engine)
weather = Table("weather_forecasts", metadata, autoload_with=engine)
risk = Table("weather_risk", metadata, autoload_with=engine)

query = (
    select(
        cities.c.city,
        cities.c.lat,
        cities.c.lng,
        weather.c.forecast_date,
        weather.c.temp_max,
        weather.c.temp_min,
        weather.c.precipitation,
        weather.c.precip_probability,
        weather.c.wind_max,
        weather.c.wind_gusts,
        weather.c.weather_code,
        risk.c.temperature_category,
        risk.c.precipitation_category,
        risk.c.wind_category,
        risk.c.risk_score,
        risk.c.risk_level,
    )
    .join(weather, cities.c.city_id == weather.c.city_id)
    .join(risk, weather.c.weather_id == risk.c.weather_id)
)

df = pd.read_sql(query, engine)
df["forecast_date"] = pd.to_datetime(df["forecast_date"])


# SIDEBAR


st.sidebar.title("Atlas Weather Risk")

city_filter = st.sidebar.multiselect(
    "Cities",
    sorted(df["city"].unique()),
    default=[],
    placeholder="All cities",
)

min_date = df["forecast_date"].min().date()
max_date = df["forecast_date"].max().date()

period = st.sidebar.date_input(
    "Forecast period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

risk_filter = st.sidebar.multiselect(
    "Risk level",
    ["Low", "Moderate", "High", "Extreme"],
    default=["Low", "Moderate", "High", "Extreme"],
)

st.sidebar.caption("Bronze → Silver → Gold → PostgreSQL → Streamlit")


# FILTER


filtered_df = df.copy()

if city_filter:
    filtered_df = filtered_df[filtered_df["city"].isin(city_filter)]

if len(period) == 2:
    start_date, end_date = period
    filtered_df = filtered_df[
        (filtered_df["forecast_date"].dt.date >= start_date)
        & (filtered_df["forecast_date"].dt.date <= end_date)
    ]

if risk_filter:
    filtered_df = filtered_df[
        filtered_df["risk_level"].isin(risk_filter)
    ]


# HEADER


st.title("Atlas Weather Risk")
st.caption(
    "Weather intelligence for Morocco — identifying vulnerable "
    "locations and high-risk forecast periods."
)

if filtered_df.empty:
    st.warning("No forecast data matches the selected filters.")
    st.stop()


# METRICS


c1, c2, c3, c4, c5 = st.columns(5)

n_cities = filtered_df["city"].nunique()
max_temp = filtered_df["temp_max"].max()
max_precip = filtered_df["precipitation"].max()
high_risk_n = filtered_df[
    filtered_df["risk_level"].isin(["High", "Extreme"])
].shape[0]
peak = filtered_df.loc[filtered_df["risk_score"].idxmax()]

c1.metric("Cities", n_cities)
c2.metric("Max temp", f"{max_temp:.1f} °C")
c3.metric("Max precip", f"{max_precip:.1f} mm")
c4.metric("High-risk periods", high_risk_n)
c5.metric(
    "Peak risk",
    f"{peak['risk_score']:.1f}",
    f"{peak['city']} • {peak['forecast_date'].strftime('%d %b %Y')}",
)


# RISK BY CITY — ST.BAR_CHART


st.subheader("Risk by city")

city_risk = (
    filtered_df.groupby("city", as_index=False)
    .agg(average_risk=("risk_score", "mean"))
    .sort_values("average_risk", ascending=True)
)

st.bar_chart(
    city_risk.set_index("city")["average_risk"],
    color="#2dd4bf",
)


# RISK DISTRIBUTION + TIMELINE (side by side)


col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Risk distribution")

    dist = (
        filtered_df["risk_level"]
        .value_counts()
        .reindex(["Low", "Moderate", "High", "Extreme"], fill_value=0)
        .reset_index()
    )
    dist.columns = ["level", "count"]

    st.bar_chart(
        dist.set_index("level")["count"],
        color="#4ade80",
    )

with col_b:
    st.subheader("Risk timeline")

    tl = (
        filtered_df.groupby("forecast_date", as_index=False)
        .agg(avg_risk=("risk_score", "mean"), max_risk=("risk_score", "max"))
        .sort_values("forecast_date")
    )

    st.line_chart(
        tl.set_index("forecast_date")[["avg_risk", "max_risk"]],
        color=["#5eead4", "#818cf8"],
    )


# CRITICAL FORECAST WINDOWS


st.subheader("Critical forecast windows")

top10 = (
    filtered_df[
        [
            "city", "forecast_date", "risk_score", "risk_level",
            "temp_max", "precipitation", "wind_max", "wind_gusts",
        ]
    ]
    .sort_values("risk_score", ascending=False)
    .head(10)
    .copy()
)

top10["forecast_date"] = top10["forecast_date"].dt.strftime("%d %b %Y")
top10 = top10.rename(columns={
    "city": "City",
    "forecast_date": "Date",
    "risk_score": "Risk Score",
    "risk_level": "Risk Level",
    "temp_max": "Max Temp °C",
    "precipitation": "Precip. mm",
    "wind_max": "Wind km/h",
    "wind_gusts": "Gusts km/h",
})

st.dataframe(top10, use_container_width=True, hide_index=True, height=340)


# CITY SUMMARY


st.subheader("City summary")

summary = (
    filtered_df.groupby("city")
    .agg(
        avg_risk=("risk_score", "mean"),
        peak_risk=("risk_score", "max"),
        avg_temp=("temp_max", "mean"),
        total_precip=("precipitation", "sum"),
        max_wind=("wind_max", "max"),
    )
    .reset_index()
    .sort_values("avg_risk", ascending=False)
)

summary = summary.rename(columns={
    "city": "City",
    "avg_risk": "Avg Risk",
    "peak_risk": "Peak Risk",
    "avg_temp": "Avg Temp °C",
    "total_precip": "Total Precip. mm",
    "max_wind": "Max Wind km/h",
})

st.dataframe(summary, use_container_width=True, hide_index=True, height=340)


# FORECAST EXPLORER


st.subheader("Forecast explorer")

explorer = filtered_df[
    [
        "city", "forecast_date", "temp_max", "temp_min",
        "precipitation", "precip_probability",
        "wind_max", "wind_gusts",
        "temperature_category", "precipitation_category",
        "wind_category", "risk_score", "risk_level",
    ]
].copy()

explorer["forecast_date"] = explorer["forecast_date"].dt.strftime("%d %b %Y")
explorer = explorer.rename(columns={
    "city": "City",
    "forecast_date": "Date",
    "temp_max": "Max Temp",
    "temp_min": "Min Temp",
    "precipitation": "Precipitation",
    "precip_probability": "Rain Prob.",
    "wind_max": "Wind",
    "wind_gusts": "Gusts",
    "temperature_category": "Temp Cat.",
    "precipitation_category": "Precip Cat.",
    "wind_category": "Wind Cat.",
    "risk_score": "Risk Score",
    "risk_level": "Risk Level",
})

st.dataframe(explorer, use_container_width=True, hide_index=True, height=420)


# MAP — ST.MAP


st.subheader("Geographic risk")

map_df = (
    filtered_df.groupby(["city", "lat", "lng"], as_index=False)
    .agg(
        risk_score=("risk_score", "mean"),
        max_risk=("risk_score", "max"),
        temp=("temp_max", "mean"),
        precip=("precipitation", "mean"),
    )
)

map_df["color"] = map_df["risk_score"].apply(
    lambda x: "#22c55e" if x < 25 else "#2dd4bf" if x < 50 else "#facc15" if x < 75 else "#fb7185" if x < 90 else "#f43f5e"
)

st.map(
    map_df,
    latitude="lat",
    longitude="lng",
    color="color",
    zoom=4.8,
)
