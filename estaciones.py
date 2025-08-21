import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
headers = {'x-api-key': API_KEY}
base_url = "https://api.openaq.org/v3/locations"


results = []

def localizacion(params):
    response = requests.get(base_url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error en la solicitud: {response.status_code}")

    data = response.json()
    results = data.get("results", [])


    df = pd.DataFrame(results)

    localizacion = []

    for i in range(len(df)):
        fila_id = df['id'].iloc[i]
        fila_name = df['name'].iloc[i]
        fila_coord = df['coordinates'].iloc[i]
        fila_sensor = df['sensors'].iloc[i]
        localizacion.append({
            'Localization': fila_id,
            'Name': fila_name,
            'Latitude': fila_coord['latitude'],
            'Longitude': fila_coord['longitude'],
            'Sensor': fila_sensor,
        })

    result = pd.DataFrame(localizacion)

    return result


