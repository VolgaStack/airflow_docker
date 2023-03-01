import pandas as pd
import sqlite3
import pendulum
from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.models.param import Param
from airflow.operators.python_operator import PythonOperator
from airflow.operators.sqlite_operator import SqliteOperator


CON = sqlite3.connect('////content/simple_EL.db')


def extract_load_data(date, table_name, conn, **context):
    """ Extract and load CSV to database
    """
    url = f'https://raw.githubusercontent.com/dm-novikov/stepik_airflow_course/main/data_new/{date}.csv'
    pd.read_csv(url).to_sql(table_name, conn, if_exists='append', index=False)

def extract_currency(date, **context):
    """ Extract CSV and puts daily rate into xcom
    """
    url = f'https://api.exchangerate.host/timeseries?start_date={date}&end_date={date}&base=EUR&symbols=USD&format=csv'

    df = pd.read_csv(url)
    rate_list = df["rate"].to_list()

    if rate_list:
        rate = rate_list.pop().replace(',','.')
        context["ti"].xcom_push(key='currency_rate', value=rate)
   

# Создадим объект класса DAG
with DAG(dag_id='simple_el',
         default_args={'owner': 'airflow'},
         schedule_interval='@daily', # Интервал запусков
         start_date=pendulum.datetime(2021, 1, 1, tz='UTC'), # Начальная точка запуска
         end_date=pendulum.datetime(2021, 1, 4, tz='UTC'), # Крайняя точка запуска
         tags=["stepic"] # тэги для фильтрации дагов в вебинтерфейсе
    ) as dag:

    extract_load_data_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_load_data,
        op_kwargs={
            'date': '{{ds}}',
            'table_name': 'data',
            'conn' : CON
            }
    )

    extract_currency_task = PythonOperator(
        task_id='extract_currency',
        python_callable=extract_currency,
        op_kwargs={
            'date': '{{ds}}'
            }
    )

    create_table_join = SqliteOperator(
        task_id='create_table_join',
        sql="""CREATE TABLE IF NOT EXISTS join_data(
        currency TEXT, 
        value INTEGER, 
        date DATE, 
        rate FLOAT
        )
        """,
        sqlite_conn_id='sqlite_simple_el'
    )

    create_table_data = SqliteOperator(
        task_id='create_table_data',
        sql="""CREATE TABLE IF NOT EXISTS data(
        currency TEXT, 
        value INTEGER, 
        date DATE
        )
        """,
        sqlite_conn_id='sqlite_simple_el'
    )    

    clear_table_data = SqliteOperator(
        task_id='clear_table_data',
        sql="delete from data where date = '{{ds}}'",
        sqlite_conn_id='sqlite_simple_el'
    )

    join_data = SqliteOperator(
        task_id='join_data',
        sql="insert into join_data(currency, value, date, rate) " +
        "select currency, value, date, " + 
        "{{ ti.xcom_pull(key='currency_rate',task_ids='extract_currency') }}" + 
        " as rate from data where date = '{{ds}}'",
        sqlite_conn_id='sqlite_simple_el'
    )

    create_table_data >> clear_table_data >> extract_load_data_task >> join_data
    extract_currency_task >> join_data
    create_table_join >> join_data
