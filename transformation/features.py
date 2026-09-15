import pandas as pd
import numpy as np

class FeatureEngineering:
  def __init__(self):
    self.data = pd.read_csv("data/silver/weather_clean.csv")
    self.df = pd.DataFrame(self.data)
    
  def temp_category(self):
    bins = [10,20,30,40,50, 55]
    labels = ["cold","Mild","Normal","Hot","Extreme"]
    temp_cat = pd.cut(self.df["temp_max"], bins=bins, labels = labels, include_lowest=True, right = True)
    self.df["temp_category"] = temp_cat
    return self.df
  
  
  
  def prec_category(self):
    bins = [0, 0.1, 0.3, 0.5, 1]
    labels = ["None", "Low", "Moderate", "Heavy"]
    prec_cat = pd.cut(self.df["precipitation"], bins = bins, labels=labels, include_lowest=True)
    self.df["prec_category"] = prec_cat
    
  def prec_probability_category(self):

    bins = [0, 20, 40, 60, 80, 100]

    labels = ["Very Low", "Low", "Moderate", "High", "Very High"]
    prec_prob_cat = pd.cut(self.df["precip_probability"], bins=bins, labels=labels, include_lowest=True)
    self.df["prec_probability_category"] = prec_prob_cat
  
dat =FeatureEngineering()
uuh = dat.temp_category()
print(uuh)