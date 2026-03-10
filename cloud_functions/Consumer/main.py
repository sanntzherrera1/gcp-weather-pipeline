import base64
import json
from storage.gcs import guardar_en_gcs

def run_cf(request):
    try:
        envelope = request.get_json()
        
        if not envelope or "message" not in envelope:
            return {"error": "Formato de mensaje inválido"}, 400
        
        message = envelope["message"]
        data = base64.b64decode(message["data"]).decode("utf-8")
        payload = json.loads(data)

        print("Mensaje recibido:", payload)
        
        guardar_en_gcs(payload, "clima_raw_data_pj")
        
        print(f"Datos guardados en GCS")
        return {"status": "success"}, 200
        
    except KeyError as e:
        print(f"Campo faltante en el mensaje: {str(e)}")
        return {"error": f"Campo faltante: {str(e)}"}, 400
        
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON: {str(e)}")
        return {"error": "Datos JSON inválidos"}, 400
        
    except Exception as e:
        print(f"Error al procesar mensaje: {str(e)}")
        raise