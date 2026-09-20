import requests as rq
from pathlib import Path

class Cities:
  def __init__(self):
    project_root = Path(__file__).resolve().parent.parent
    self.output = project_root / "data" / "bronze" / "cities" / "morocco_cities.csv"
    self.url = "https://simplemaps.com/static/data/country-cities/ma/ma.csv"
  def get_cities(self):
    try :

      response = rq.get(self.url, timeout=30)
      
      response.raise_for_status()
      
      with open(self.output, "wb") as f:
        f.write(response.content)
        
        print(f"the file downloaded to {self.output}")
        
    except rq.exceptions.Timeout:
      print("The data took too long to load")
      
    except rq.exceptions.RequestException:
      print("the request didn't go through")
