from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus

load_dotenv()

password = quote_plus(os.getenv('DB_PASSWORD', ''))

engine = create_engine(f"postgresql+psycopg2://{os.getenv('DB_USER', 'atlas_weather')}:"
    f"{password}@"
    f"{os.getenv('DB_HOST', 'localhost')}:"
    f"{os.getenv('DB_PORT', '5433')}/"
    f"{os.getenv('DB_NAME', 'weather_db')}"
)

