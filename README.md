# Pipeline de Datos Meteorológicos en GCP

Pipeline end-to-end para ingesta y procesamiento de datos del clima usando servicios serverless de Google Cloud Platform.

## 🏗️ Arquitectura Actual

### Streaming Ingestion (Implementado)
```
Cloud Scheduler (cada X min/hs/dia)
    ↓
Publisher Cloud Function (HTTP trigger)
    ↓
Pub/Sub Topic (topic_clima)
    ↓
Push Subscription (sub_clima_push)
    ↓
Subscriber Cloud Function (HTTP trigger)
    ↓
Cloud Storage (clima_raw_data_pj)
```

### Próximas Capas (Planificado)
- **Batch Processing:** Apache Airflow / Cloud Composer
- **Transformación:** Apache DataFusion
- **Data Warehouse:** BigQuery
- **Visualización:** Looker Studio
- **Orquestación:** Airflow con branching para validación de datos

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

## 🔧 Tecnologías

- **Cloud Platform:** Google Cloud Platform (GCP)
- **Compute:** Cloud Functions (Gen2)
- **Messaging:** Cloud Pub/Sub
- **Storage:** Cloud Storage (GCS)
- **Scheduler:** Cloud Scheduler
- **Language:** Python 3.11
- **API:** OpenWeatherMap API
- **Orchestration:** Apache Airflow / Cloud Composer

## 📊 Datos Capturados

Cada X tiempo se captura:
- Ciudad
- Temperatura
- Humedad
- Presión atmosférica
- Descripción del clima
- Velocidad del viento
- Timestamp de última actualización

## 🎯 Roadmap

- [x] Streaming ingestion con Cloud Functions
- [x] Pub/Sub messaging
- [x] Almacenamiento raw en GCS
- [ ] Procesamiento batch con Airflow
- [ ] Transformación con DataFusion
- [ ] Carga a BigQuery
- [ ] Dashboards en Looker Studio
- [ ] Data quality checks

## 📝 Notas

Este proyecto es parte de mi aprendizaje en Data Engineering brindado por [Dicsys Academy], enfocado en arquitecturas de datos en la nube y procesamiento en tiempo real.

---

**Fuente de datos:** [OpenWeatherMap API](https://openweathermap.org/api)