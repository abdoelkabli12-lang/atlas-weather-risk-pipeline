import pandas as pd
import numpy as np
from pathlib import Path


class CleanData:
    def __init__(self):
        project_root = Path(__file__).resolve().parent.parent
        self.data = pd.read_json(project_root / "data" / "bronze" / "weather" / "weather.json")
        self.df = pd.DataFrame(self.data)
        self.all_days = []
        
    def cleaning_data(self):
        project_root = Path(__file__).resolve().parent.parent
        for row in self.df.itertuples():
            daily_df = pd.DataFrame(row.daily)
            
            daily_df["city"] = row.city
            daily_df["latitude"] = row.latitude
            daily_df["longitude"] = row.longitude
            
            self.all_days.append(daily_df)

        weather_clean = pd.concat(self.all_days, ignore_index=True)
        weather_clean = weather_clean[
            [
                "city",
                "latitude",
                "longitude",
                "time",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
                "weather_code"
            ]
        ]
        weather_clean = weather_clean.rename(columns={
            "time": "date",
            "temperature_2m_max": "temp_max",
            "temperature_2m_min": "temp_min",
            "precipitation_sum": "precipitation",
            "precipitation_probability_max": "precip_probability",
            "wind_speed_10m_max": "wind_max",
            "wind_gusts_10m_max": "wind_gusts"
        })

        weather_clean["date"] = pd.to_datetime(weather_clean["date"])

        weather_clean.to_csv(
            project_root / "data" / "silver" / "weather_clean.csv",
            index=False
        )