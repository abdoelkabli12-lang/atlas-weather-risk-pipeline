import sys

sys.path.insert(0, "/opt/airflow/project")

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator

from datetime import datetime, timedelta

from extraction.cities import Cities
from extraction.weather import get_weather
from transformation.cleaning import CleanData
from transformation.features import Category, Risk
from load.load_weather import load_to_postgres


with DAG(
    dag_id="atlas_weather_pipeline",
    start_date=datetime(2026, 9, 20),
    schedule="@daily",
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
) as dag:

    extract_cities = PythonOperator(
        task_id="extract_cities",
        python_callable=Cities().get_cities,
    )

    extract_weather_task = PythonOperator(
        task_id="extract_weather",
        python_callable=get_weather,
    )

    clean = PythonOperator(
        task_id="clean",
        python_callable=CleanData().cleaning_data,
    )

    categorize = PythonOperator(
        task_id="categorize",
        python_callable=Category().save_category,
    )

    calculate_risk = PythonOperator(
        task_id="calculate_risk",
        python_callable=Risk().save_risk,
    )

    load_postgres = PythonOperator(
        task_id="load_postgres",
        python_callable=load_to_postgres,
    )

    extract_cities >> extract_weather_task >> clean >> categorize >> calculate_risk >> load_postgres