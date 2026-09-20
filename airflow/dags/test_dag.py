from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime


def hello():
    print("Atlas Weather Pipeline is alive 🗿")


with DAG(
    dag_id="atlas_weather_test",
    start_date=datetime(2026, 9, 20),
    schedule=None,
    catchup=False,
) as dag:

    test = PythonOperator(
        task_id="test_airflow",
        python_callable=hello,
    )