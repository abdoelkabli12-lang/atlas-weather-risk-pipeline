-- Active: 1789539689022@@127.0.0.1@5432
SELECT c.city, MAX(f.temp_max) FROM cities c JOIN weather_forecasts f ON c.city_id = f.city_id GROUP BY c.city ORDER BY MAX(f.temp_max) DESC;


SELECT c.city, MAX(f.precipitation) FROM cities c JOIN weather_forecasts f ON c.city_id = f.city_id GROUP BY c.city ORDER BY MAX(f.precipitation) DESC;

SELECT c.city, AVG(r.risk_score) FROM cities c JOIN weather_forecasts f  ON c.city_id = f.city_id JOIN weather_risk r ON f.weather_id = r.weather_id GROUP BY c.city ORDER BY AVG(r.risk_score) DESC LIMIT 10;

SELECT c.city, f.forecast_date, r.risk_score AS risk FROM cities c JOIN weather_forecasts f ON c.city_id = f.city_id JOIN weather_risk r ON f.weather_id = r.weather_id ORDER BY risk DESC limit 10;

SELECT city, forecast_date, risk_score
FROM (
    SELECT
        c.city,
        f.forecast_date,
        r.risk_score,
        ROW_NUMBER() OVER (
            PARTITION BY c.city
            ORDER BY r.risk_score DESC
        ) AS rn
    FROM cities c
    JOIN weather_forecasts f
        ON c.city_id = f.city_id
    JOIN weather_risk r
        ON f.weather_id = r.weather_id
) x
WHERE rn = 1 LIMIT 10;