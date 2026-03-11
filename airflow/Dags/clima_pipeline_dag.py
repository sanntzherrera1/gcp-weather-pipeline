from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryInsertJobOperator,
    BigQueryCheckOperator
)
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timezone

import os
#Config inicial
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "your-project-id")
DATASET_ID = os.environ.get("BQ_DATASET_ID", "dataset_clima")
GCS_BUCKET = os.environ.get("GCS_BUCKET", "your-bucket-name")


default_args = {
    'owner': 'luis_herrera',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'clima_batch_pipeline',
    default_args=default_args,
    description='Pipeline clima batch con Airflow y BigQuery',
    schedule_interval=None,  #config del time del schedule
    start_date=datetime(2026, 3, 10),
    catchup=False,
    tags=['clima', 'batch', 'bigquery'],
)

# Task 1: Cargar datos de GCS a BigQuery (raw)

BigQueryInsertJobOperator.template_fields = ["job_id"]

execution_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
source_uri = f"gs://{GCS_BUCKET}/dt={execution_date}/clima_*.json"

load_gcs_to_bigquery_raw = BigQueryInsertJobOperator(
    task_id="load_gcs_to_bigquery_raw",
    configuration={
        "load": {
            "sourceUris": [source_uri],
            "destinationTable": {
                "projectId": PROJECT_ID,
                "datasetId": DATASET_ID,
                "tableId": "clima_raw"
            },
            "sourceFormat": "NEWLINE_DELIMITED_JSON",
            "writeDisposition": "WRITE_APPEND",
            "autodetect": True,
            "timePartitioning": {"type": "DAY", "field": "fecha_ultima_act"}
        }
    },
    gcp_conn_id="google_cloud_default",
    project_id=PROJECT_ID,
)

# Task 2: Verificar que hay datos nuevos
check_data = BigQueryCheckOperator(
    task_id='check_new_data',
    sql=f"""
        SELECT COUNT(*) > 0
        FROM `{PROJECT_ID}.{DATASET_ID}.clima_raw`
    """,
    location='us-central1',
    use_legacy_sql=False,
    dag=dag,
)

# Task 3: Branching - decidir si transformar
def decide_branch(**context):
    """Decide si hay datos válidos para transformar"""
    return 'transform_clima_data'

branch_task = BranchPythonOperator(
    task_id='branch_decision',
    python_callable=decide_branch,
    dag=dag,
)

# Task 4a: Transformación (rama de camino feliz)
transform_data = BigQueryInsertJobOperator(
    task_id='transform_clima_data',
    configuration={
        "query": {
            "query": f"""
                CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.clima_analytics` 
                PARTITION BY DATE(fecha_ultima_act) AS
                SELECT 
                  ciudad,
                  ROUND(temperatura - 273.15, 2) AS temperatura_celsius,
                  humedad,
                  presion,
                  descripcion,
                  viento_velocidad,
                  TIMESTAMP(fecha_ultima_act) AS fecha_ultima_act
                FROM `{PROJECT_ID}.{DATASET_ID}.clima_raw`
            """,
            "useLegacySql": False
        }
    },
    location='us-central1',
    dag=dag,
)

# Task 4b: Log si no hay datos - bifurcacion
def log_no_data(**context):
    print("No se encontraron datos para procesar")

no_data_task = PythonOperator(
    task_id='log_no_data',
    python_callable=log_no_data,
    dag=dag,
)

# Task 5: Data quality check
quality_check = BigQueryCheckOperator(
    task_id='quality_check',
    sql=f"""
        SELECT COUNT(*) > 0
        FROM `{PROJECT_ID}.{DATASET_ID}.clima_analytics`
        WHERE temperatura_celsius BETWEEN -50 AND 60
          AND humedad BETWEEN 0 AND 100
          AND presion > 0
    """,
    location='us-central1',
    use_legacy_sql=False,
    dag=dag,
)

# Task 6: Success/End tasks
success_task = EmptyOperator(task_id='pipeline_success', dag=dag)
end_task = EmptyOperator(
    task_id='end', 
    dag=dag, 
    trigger_rule='none_failed_min_one_success'
)

# Definir flujo con bifurcacion
load_gcs_to_bigquery_raw >> check_data >> branch_task
branch_task >> transform_data >> quality_check >> success_task >> end_task
branch_task >> no_data_task >> end_task