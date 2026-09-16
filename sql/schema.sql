CREATE TABLE cities (
    city_id SERIAL PRIMARY KEY,
    city VARCHAR(150) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    country VARCHAR(100),
    iso2 CHAR(2),
    admin_name VARCHAR(150),
    capital VARCHAR(50),
    population BIGINT,
    population_proper BIGINT
);

CREATE TABLE weather (
  weather_id SERIAL PRIMARY KEY,
  city_id INTEGER NOT NULL,
  forecast_date DATE NOT NULL,

  temperature_max DOUBLE PRECISION,
  temperature_min DOUBLE PRECISION,
  precipitation_sum DOUBLE PRECISION,
  precipitation_probability_max DOUBLE PRECISION,
  wind_speed_max DOUBLE PRECISION,
  wind_gusts_max DOUBLE PRECISION,
  weather_code INTEGER,
  FOREIGN KEY (city_id) REFERENCES cities(city_id),
  UNIQUE (city_id, forecast_date)
);
