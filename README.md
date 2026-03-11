# Pipeline de Datos Meteorológicos en GCP

Pipeline end-to-end para ingesta y procesamiento de datos del clima usando servicios serverless de Google Cloud Platform.

## 🏗️ Arquitectura

![Diagrama de Arquitectura](./docs/diagrama_arquitectura.png)

## 📈  Monitoreo 

![Monitorio de Airflow](./docs/clima_task_pipeline.png)

## 📁 Estructura del Proyecto
```
project_clima/
├── cloud_functions/
│   ├── publisher/          # Obtiene datos de OpenWeatherMap API
│   │   ├── Api/
│   │   │   └── clima.py    # Llamada a la API
│   │   ├── main.py         # Cloud Function publisher
│   │   └── requirements.txt
│   └── subscriber/         # Procesa mensajes y guarda en GCS
│       ├── storage/
│       │   └── gcs.py      # Operaciones de Cloud Storage
│       ├── main.py         # Cloud Function subscriber
│       └── requirements.txt
├── airflow/
│   └── dags/
│       └── clima_pipeline_dag.py  # DAG de Airflow para batch processing
├── .env.example            # Template de variables de entorno
├── .gitignore
└── README.md
```

## 🚀 Deployment

### Prerequisitos
- Cuenta de GCP activa
- `gcloud` CLI configurado
- API Key de OpenWeatherMap

### Variables de Entorno
Crear archivo `.env` basado en `.env.example`:
```bash
API_KEY=tu_api_key_de_openweathermap
GCP_PROJECT_ID=tu_project_id
BQ_DATASET_ID=dataset_clima
GCS_BUCKET=tu_bucket_name
```

### Deploy Cloud Functions

**Publisher:**
```bash
gcloud functions deploy publisher_clima \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=./cloud_functions/publisher \
  --entry-point=run_cf \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars=API_KEY=tu_api_key
```

**Subscriber:**
```bash
gcloud functions deploy subscriber_clima \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=./cloud_functions/subscriber \
  --entry-point=run_cf \
  --trigger-http \
  --allow-unauthenticated
```

### Configurar Cloud Scheduler
```bash
gcloud scheduler jobs create http scheduler_clima \
  --location=us-central1 \
  --schedule="* * * * *" \
  --uri="https://us-central1-YOUR_PROJECT.cloudfunctions.net/publisher_clima" \
  --http-method=GET
```

### Deploy DAG en Cloud Composer
```bash
gsutil cp airflow/dags/clima_pipeline_dag.py gs://YOUR_COMPOSER_BUCKET/dags/
```

## 🔧 Tecnologías

- **Cloud Platform:** Google Cloud Platform (GCP)
- **Compute:** Cloud Functions (Gen2)
- **Messaging:** Cloud Pub/Sub
- **Storage:** Cloud Storage (GCS)
- **Scheduler:** Cloud Scheduler
- **Orchestration:** Apache Airflow / Cloud Composer
- **Data Warehouse:** BigQuery
- **Visualización:** Looker Studio
- **Language:** Python 3.11
- **API:** OpenWeatherMap API

## 📊 Datos Capturados

Cada X tiempo se captura:
- Ciudad
- Temperatura (Kelvin → Celsius en analytics)
- Humedad
- Presión atmosférica
- Descripción del clima
- Velocidad del viento
- Timestamp de última actualización

## 🎯 Roadmap

- [x] Streaming ingestion con Cloud Functions
- [x] Cloud Scheduler para automatización
- [x] Pub/Sub messaging
- [x] Almacenamiento raw en GCS
- [x] Procesamiento batch con Airflow
- [x] Carga a dataset en BigQuery
- [x] Data quality checks
- [x] Transformación con SQL en DAGs
- [x] Dashboards en Looker Studio

## 📝 Notas

Este proyecto es parte de mi aprendizaje en Data Engineering brindado por [Dicsys Academy], enfocado en arquitecturas de datos en la nube y procesamiento en tiempo real.

---

**Fuente de datos:** [OpenWeatherMap API](https://openweathermap.org/api)