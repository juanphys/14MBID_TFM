import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
headers = {'x-api-key': API_KEY}

base_url = "https://api.openaq.org/v3/locations"


results = []


def sensor(params):
    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Error en la solicitud: {response.status_code}")

    data = response.json()
    results = data.get("results", [])

    df = pd.DataFrame(results)

    sensor_ind = []

    for i in range(len(df)):
        location_id = df['id'].iloc[i]
        location_name = df['name'].iloc[i]
        for sensors in df['sensors'].iloc[i]:
            sensor_ind.append({
                'LocationID': location_id,
                'LocationName': location_name,
                'SensorID': sensors['id'],
                'SensorName': sensors['name'],
                'Parameter': sensors['parameter']['name'],
                'ParameterDisplay': sensors['parameter']['displayName'],
                'Units': sensors['parameter']['units']
            })
# Convertir a DataFrame
    df_sensores = pd.DataFrame(sensor_ind)

    return df_sensores


