from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys

sys.path.insert(0, '/opt/airflow')

from extract.space_weather import fetch_space_weather
from extract.orbital_data import fetch_orbital_data
from extract.nasa_news import fetch_nasa_news
from extract.dsn_tracker import fetch_dsn_data

default_args = {
    'owner': 'orionpulse',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='orion_pipeline',
    default_args=default_args,
    description='Artemis II Mission Data Pipeline',
    schedule_interval='@daily',
    start_date=datetime(2026, 4, 1),
    catchup=False,
    tags=['nasa', 'artemis', 'orionpulse'],
) as dag:

    task_space_weather = PythonOperator(
        task_id='extract_space_weather',
        python_callable=fetch_space_weather,
    )

    task_orbital = PythonOperator(
        task_id='extract_orbital_data',
        python_callable=fetch_orbital_data,
    )

    task_news = PythonOperator(
        task_id='extract_nasa_news',
        python_callable=fetch_nasa_news,
    )

    task_dsn = PythonOperator(
        task_id='extract_dsn_data',
        python_callable=fetch_dsn_data,
    )

    # All extractors run in parallel
    [task_space_weather, task_orbital, task_news, task_dsn]