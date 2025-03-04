from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    'simple_test',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
) as dag:
    t = BashOperator(
        task_id='print_hello',
        bash_command='echo "Hello, Airflow!"',
    )
