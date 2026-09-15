import requests as rq

class Cities:
  def __init__(self):
    self.url = "https://simplemaps.com/static/data/country-cities/ma/ma.csv"
    self.output = 'data/bronze/cities/morocco_cities.csv'
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
