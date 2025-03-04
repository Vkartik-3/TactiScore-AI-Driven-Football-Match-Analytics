from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

def scrape_match_data():
    print("Scraping match data...")
    return "Scraped match data successfully"

def fetch_odds_data():
    print("Fetching odds data...")
    return "Fetched odds data successfully"

def process_data():
    print("Processing data...")
    return "Processed data successfully"

def generate_features():
    print("Generating features...")
    return "Generated features successfully"

def create_tables():
    print("This would create database tables in a real setup")
    return "Tables created successfully"

default_args = {
    'owner': 'football_prediction',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'football_pipeline_simple',
    default_args=default_args,
    description='Simplified Football data pipeline',
    schedule_interval='0 2 * * *',
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    # Create tables task
    create_tables_task = PythonOperator(
        task_id='create_tables',
        python_callable=create_tables,
    )
    
    # Scrape task
    scrape = PythonOperator(
        task_id='scrape_data',
        python_callable=scrape_match_data,
    )
    
    # Fetch odds task
    fetch_odds = PythonOperator(
        task_id='fetch_odds',
        python_callable=fetch_odds_data,
    )
    
    # Process task
    process = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
    )
    
    # Generate features task
    generate = PythonOperator(
        task_id='generate_features',
        python_callable=generate_features,
    )
    
    # Define task sequence
    create_tables_task >> [scrape, fetch_odds] >> process >> generate