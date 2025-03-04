from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'football_prediction',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def scrape_data():
    print("Scraping football data...")
    return "Data scraped successfully"

def process_data():
    print("Processing football data...")
    return "Data processed successfully"

with DAG(
    'football_data_pipeline',
    default_args=default_args,
    description='Football data ETL pipeline',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    t1 = BashOperator(
        task_id='print_working_dir',
        bash_command='pwd && ls -la',
    )
    
    t2 = PythonOperator(
        task_id='scrape_data',
        python_callable=scrape_data,
    )
    
    t3 = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
    )
    
    t1 >> t2 >> t3