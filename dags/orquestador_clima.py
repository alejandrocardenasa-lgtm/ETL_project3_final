from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import sys


sys.path.append('/opt/airflow')

from src.extract import extract_original_dataset, extract_meteostat
from src.clean import clean_meteostat
from src.transform import transform_datasets
from src.validate import validate_fact_climate_daily
from src.load import load_to_warehouse

default_args = {
    'owner': 'ingenieria_datos',
    'start_date': datetime(2026, 5, 27),
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

with DAG(
    'pipeline_clima_batch', 
    default_args=default_args, 
    schedule_interval='@daily', 
    catchup=False
) as dag:

    # 1. Extracción 
    def extraer_ideam():
        extract_original_dataset()

    def extraer_api():
        extract_meteostat()

    # 2. Limpieza
    def limpiar_api():
        clean_meteostat()

    # 3. Transformación 
    def transformar_integrar():
        transform_datasets()

    # 4. Validación
    def validar_calidad():
        validate_fact_climate_daily()

    # 5. Carga 
    def cargar_datos():
        print("Leyendo archivos procesados del disco duro...")
        d_city = pd.read_csv("data/processed/dim_city.csv")
        d_date = pd.read_csv("data/processed/dim_date.csv")
        d_source = pd.read_csv("data/processed/dim_source.csv")
        f_climate = pd.read_csv("data/processed/fact_climate_daily.csv")
        
        load_to_warehouse(d_city, d_date, d_source, f_climate)

    # Definición de las tareas de Airflow
    t1_ideam = PythonOperator(task_id='extraer_ideam', python_callable=extraer_ideam)
    t1_api = PythonOperator(task_id='extraer_api', python_callable=extraer_api)
    t2_clean = PythonOperator(task_id='limpiar_api', python_callable=limpiar_api)
    t3_transform = PythonOperator(task_id='transformar_datos', python_callable=transformar_integrar)
    t4_validate = PythonOperator(task_id='validar_calidad', python_callable=validar_calidad)
    t5_load = PythonOperator(task_id='cargar_dw', python_callable=cargar_datos)

    
    t1_api >> t2_clean
    [t1_ideam, t2_clean] >> t3_transform >> t4_validate >> t5_load