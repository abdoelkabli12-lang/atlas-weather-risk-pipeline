from dotenv import load_dotenv
import psycopg2 as ps
import os
from sqlalchemy import Table, Column, MetaData, Integer, Computed


print(os.getenv("DB_PORT"))
conn = ps.connect(
    dbname=os.getenv("DB_NAME", "weather_db"),
    user=os.getenv("DB_USER", "atlas_weather"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
)