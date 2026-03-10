from google.cloud import pubsub_v1
from Api.clima import response_data
import json

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("project-72f0fa15-7cc5-41b4-902", "topic_clima")

def run_cf(request):
    try:
        message = response_data()
        
        if not message:
            return {"error": "No hay data en la API"}, 500
        
        data_json = json.dumps(message)
        future = publisher.publish(topic_path, data_json.encode("utf-8"))
        message_id = future.result()
        
        print(f"Mensaje exitoso con ID: {message_id}")
        return {"status": "success", "message_id": message_id}, 200
        
    except json.JSONEncodeError as e:
        print(f"Error al codificar mensaje a JSON: {str(e)}")
        return {"error": "Formato de datos inválido"}, 400
        
    except Exception as e:
        print(f"Error al publicar mensaje: {str(e)}")
        return {"error": f"Fallo al publicar: {str(e)}"}, 500