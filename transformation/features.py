import pandas as pd
import numpy as np
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
class Category:
  def __init__(self):
    self.data = pd.read_csv(project_root / "data" / "silver" / "weather_clean.csv")
    self.df = pd.DataFrame(self.data)
    
  def temp_category(self):
    bins = [10,20,30,40,50, 55]
    labels = ["cold","Mild","Normal","Hot","Extreme"]
    temp_cat = pd.cut(self.df["temp_max"], bins=bins, labels = labels, include_lowest=True, right = True)
    self.df["temp_category"] = temp_cat
    return self.df
  
  
  
  def prec_category(self):
      bins = [-float("inf"), 0, 0.1, 0.5, 1, float("inf")]
      labels = ["zero", "Low", "Moderate", "Heavy", "Very Heavy"]

      prec_cat = pd.cut(self.df["precipitation"], bins=bins, labels=labels, include_lowest=True)

      self.df["prec_category"] = prec_cat
    
  def prec_probability_category(self):
    bins = [0, 20, 40, 60, 80, 100]
    labels = ["Very Low", "Low", "Moderate", "High", "Very High"]
    prec_prob_cat = pd.cut(self.df["precip_probability"], bins=bins, labels=labels, include_lowest=True)
    self.df["prec_probability_category"] = prec_prob_cat
  
  
  def wind_category(self):
    bins = [5,10,20,30,40,float("inf")]
    labels = ["weak", "normal","stong", "very strong", "extreme"]
    wind_cat = pd.cut(self.df["wind_max"], bins= bins, labels=labels, include_lowest=True)
    self.df["wind_category"] = wind_cat
    
    
  def gust_category(self):

    bins = [0, 30, 50, 70, 90, float("inf")]

    labels = ["weak", "normal", "strong", "very strong", "extreme"]

    gust_cat = pd.cut(
        self.df["wind_gusts"],
        bins=bins,
        labels=labels,
        include_lowest=True
    )

    self.df["gust_category"] = gust_cat
    
    
  
  def weather_code_category(self):

    risk_values = {
        0: "Clear",
        1: "Low",
        2: "Low",
        3: "Moderate",
        45: "Moderate",
        48: "Moderate",
        51: "Moderate",
        53: "Moderate",
        55: "High",
        56: "High",
        57: "High",
        61: "High",
        63: "High",
        65: "Very High",
        66: "Very High",
        67: "Very High",
        71: "High",
        73: "High",
        75: "Very High",
        77: "Very High",
        80: "High",
        81: "High",
        82: "Very High",
        85: "Very High",
        86: "Very High",
        95: "Extreme",
        96: "Extreme",
        99: "Extreme"
    }

    self.df["weather_category"] = self.df["weather_code"].map(risk_values)
    
  def save_category(self):
    self.temp_category()
    self.prec_category()
    self.prec_probability_category()
    self.wind_category()
    self.gust_category()
    self.weather_code_category()
    self.df.to_csv(project_root / "data" / "gold" / "weather_categories.csv", index=False)
    
    
class Risk:
  def __init__(self):
    self.data = pd.read_csv(project_root / "data" / "gold" / "weather_categories.csv")
    self.df = pd.DataFrame(self.data)
    print(self.df["temp_category"].unique())
    print(self.df["prec_category"].unique())
    
  def temp_risk(self):
    risk_values = {
      "cold": 20,
      "Mild": 0,
      "Normal": 0,
      "Hot": 50,
      "Extreme": 100
    }
    
    self.df["temp_risk"] = self.df["temp_category"].map(risk_values)
  def prec_risk(self):
    risk_values = {
      "zero" : 0,
      "Low" : 25,
      "Moderate": 60,
      "Heavy": 80,
      "Very Heavy": 100 
    } 
    
    self.df["prec_risk"] = self.df["prec_category"].map(risk_values)
    
  def prec_probability_risk(self):
    risk_values = {
      "Very Low" : 0,
      "Low" : 25,
      "Moderate": 50,
      "High" : 75,
      "Very High" : 100
      }
    
    self.df["prec_probability_risk"] = self.df["prec_probability_category"].map(risk_values)
  
  
  def wind_risk(self):
    risk_values = {
        "weak": 0,
        "normal": 25,
        "stong": 50,
        "very strong": 75,
        "extreme": 100
    }

    self.df["wind_risk"] = self.df["wind_category"].map(risk_values)
    
    
  def gust_risk(self):

    risk_values = {
        "weak": 0,
        "normal": 25,
        "strong": 50,
        "very strong": 75,
        "extreme": 100
    }

    self.df["gust_risk"] = self.df["gust_category"].map(risk_values)
    
    
    
  def weather_code_risk(self):

    risk_values = {
        "Clear": 0,
        "Low": 25,
        "Moderate": 50,
        "High": 75,
        "Very High": 90,
        "Extreme": 100
    }

    self.df["weather_code_risk"] = self.df["weather_category"].map(risk_values)
    
    
  def risk_score(self):
    self.df["risk_score"] =  (
    self.df["temp_risk"] * 0.20 +
    self.df["prec_risk"] * 0.15 +
    self.df["prec_probability_risk"] * 0.15 +
    self.df["wind_risk"] * 0.20 +
    self.df["gust_risk"] * 0.20 +
    self.df["weather_code_risk"] * 0.10
    )
    
    
  def risk_level(self):
    bins = [-1, 24, 49, 74, 100]
    labels = ["Low", "Moderate", "High", "Extreme"]
    self.df["risk_level"] = pd.cut(self.df["risk_score"], bins=bins, labels=labels)
    
  def save_risk(self):
    self.temp_risk()
    self.prec_risk()
    self.prec_probability_risk()
    self.wind_risk()
    self.gust_risk()
    self.weather_code_risk()
    self.risk_score()
    self.risk_level()
    
    print(self.df[
    [
        "temp_risk",
        "prec_risk",
        "prec_probability_risk",
        "wind_risk",
        "gust_risk",
        "weather_code_risk"
    ]
].isna().sum())
    
    print(self.df.head())
    print(self.df.shape)
    self.df.reset_index(drop=True)
    self.df.insert(0, "weather_id", range(1, len(self.df) + 1))
    self.df.to_csv(project_root / "data" / "gold" / "weather_risk.csv", index=False)
    
    
    
if __name__ == "__main__":
  dat =Category()
  dat.save_category()

  dat2 = Risk()
  dat2.save_risk()