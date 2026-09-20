import requests as rq
import pandas as pd
import json
from pathlib import Path

def get_weather():
  project_root = Path(__file__).resolve().parent.parent
  url = "https://api.open-meteo.com/v1/forecast"
  output = project_root / "data" / "bronze" / "weather" / "weather.json"


  res = pd.read_csv(project_root / "data" / "bronze" / "cities" / "morocco_cities.csv")
  df  = pd.DataFrame(res)
  cols = [0,1,2]

  df = df[df.columns[cols]]

  lat = []
  lng = []

  for i in df.itertuples():
    lat.append(i.lat)
    lng.append(i.lng)


  params = {
      "latitude": ",".join(df["lat"].astype(str)),
      "longitude": ",".join(df["lng"].astype(str)),
      "daily": ",".join([
          "temperature_2m_max",
          "temperature_2m_min",
          "precipitation_sum",
          "precipitation_probability_max",
          "wind_speed_10m_max",
          "wind_gusts_10m_max",
          "weather_code"
      ]),
      "timezone": "Africa/Casablanca"
  }


  try :

    response = rq.get(url, params=params, timeout=30)
    
    response.raise_for_status()
    data = response.json()

    for i, city in enumerate(df["city"]):
        data[i]["city"] = city
      
    with open(output, "w") as f:
      json.dump(data, f, indent=4, ensure_ascii=False)
      
      print(f"the file downloaded to {output}")
      
  except rq.exceptions.Timeout:
    print("The data took too long to load")
    
  except rq.exceptions.RequestException as e:
    print(f"Request failed: {e}")


