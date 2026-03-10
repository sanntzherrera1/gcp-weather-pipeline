import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("API_KEY")

url = 'http://api.openweathermap.org/data/2.5/weather'
params = {
    "q": "Buenos Aires",
    "appid": API_KEY,
    "lang": "es",
}

def response_data():
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        message = {
            "ciudad": data["name"],
            "temperatura": data["main"]["temp"],
            "humedad": data["main"]["humidity"],
            "presion": data["main"]["pressure"],
            "descripcion": data["weather"][0]["description"],
            "viento_velocidad": data["wind"]["speed"],
            "fecha_ultima_act": datetime.fromtimestamp(data["dt"]).strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        print(f"Datos obtenidos correctamente de la API para {data['name']}")
        return message
        
    except requests.exceptions.Timeout:
        print("Error: Timeout al conectar con la API de OpenWeatherMap")
        raise
        
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP de la API: {response.status_code} - {str(e)}")
        raise
        
    except KeyError as e:
        print(f"Error: Campo faltante en respuesta de API: {str(e)}")
        raise
        
    except Exception as e:
        print(f"Error inesperado al obtener datos del clima: {str(e)}")
        raise




    