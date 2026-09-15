import pandas as pd
import json
import random
from datetime import date, timedelta

INPUT = "data/bronze/cities/morocco_cities.csv"
OUTPUT = "data/bronze/weather/weather_mock.json"

df = pd.read_csv(INPUT)

cities = df[["city", "lat", "lng"]]

weather_data = []

start_date = date(2026, 9, 15)

for _, city in cities.iterrows():

    daily = {
        "time": [],
        "temperature_2m_max": [],
        "temperature_2m_min": [],
        "precipitation_sum": [],
        "precipitation_probability_max": [],
        "wind_speed_10m_max": [],
        "wind_gusts_10m_max": [],
        "weather_code": []
    }

    # Give each city a slightly different baseline
    temperature_base = random.uniform(24, 36)

    for day in range(7):

        current_date = start_date + timedelta(days=day)

        temp_max = round(
            temperature_base + random.uniform(-4, 4), 1
        )

        temp_min = round(
            temp_max - random.uniform(7, 15), 1
        )

        precipitation = round(
            random.uniform(0, 20), 1
        )

        precipitation_probability = random.randint(0, 100)

        wind_speed = round(
            random.uniform(10, 40), 1
        )

        wind_gusts = round(
            wind_speed * random.uniform(1.3, 1.8), 1
        )

        # Generate a weather code based roughly on precipitation
        if precipitation_probability < 20:
            weather_code = random.choice([0, 1, 2])
        elif precipitation_probability < 60:
            weather_code = random.choice([2, 3, 61])
        else:
            weather_code = random.choice([61, 63, 65, 80, 81])

        daily["time"].append(str(current_date))
        daily["temperature_2m_max"].append(temp_max)
        daily["temperature_2m_min"].append(temp_min)
        daily["precipitation_sum"].append(precipitation)
        daily["precipitation_probability_max"].append(
            precipitation_probability
        )
        daily["wind_speed_10m_max"].append(wind_speed)
        daily["wind_gusts_10m_max"].append(wind_gusts)
        daily["weather_code"].append(weather_code)

    weather_data.append({
        "city": city["city"],
        "latitude": city["lat"],
        "longitude": city["lng"],
        "timezone": "Africa/Casablanca",
        "daily": daily
    })


with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(weather_data, f, indent=2, ensure_ascii=False)

print(f"Generated {len(weather_data)} cities")
print(f"Saved to {OUTPUT}")