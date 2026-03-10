from google.cloud import storage
import json
from datetime import datetime

def guardar_en_gcs(payload, bucket_name):
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)

        fecha = datetime.now().strftime('%Y-%m-%d')
        hora = datetime.now().strftime('%H-%M-%S')
        nombre_archivo = f"dt={fecha}/clima_{fecha}_{hora}.json"
        
        blob = bucket.blob(nombre_archivo)
        blob.upload_from_string(json.dumps(payload), content_type="application/json")
        
        print(f"Archivo guardado en GCS: {nombre_archivo}")
        
    except json.JSONEncodeError as e:
        print(f"Error al serializar datos a JSON: {str(e)}")
        raise
        
    except Exception as e:
        print(f"Error al guardar en GCS: {str(e)}")
        raise