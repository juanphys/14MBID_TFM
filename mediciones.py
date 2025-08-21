import requests
import pandas as pd
import sensores
import time
from dotenv import load_dotenv
import os

BahiaCadiz_params= {
    "limit": 100,           # Máximo por página (puedes ajustar hasta 10000 en algunos casos)
    "page": 1,
    "coordinates": "36.4606,-6.2031",
    "radius": 1000,
}

Jerez_params = {
    "limit": 100,           # Máximo por página (puedes ajustar hasta 10000 en algunos casos)
    "page": 1,
    "coordinates": "36.6885,-6.1172",
    "radius": 1000,
}


Algeciras_params = {
    "limit": 100,           # Máximo por página (puedes ajustar hasta 10000 en algunos casos)
    "page": 1,
    "coordinates": "36.13623,-5.4534",
    "radius": 1000,
}


# Parámetros para mediciones horarias
params = {
    "limit": 1000,
    "page": 1,
    "datetime_from": "2021-12-31T22:00:00Z",
    "datetime_to": "2025-05-31T21:00:00Z",
}

# Obtener sensores
Bahia_Cadiz = sensores.sensor(BahiaCadiz_params)
Jerez = sensores.sensor(Jerez_params)
Algeciras = sensores.sensor(Algeciras_params)

sensor = pd.concat([Bahia_Cadiz, Jerez, Algeciras], axis=0, ignore_index=True)
contaminante = ['o3', 'no2', 'co']
sensor = sensor[sensor['Parameter'].isin(contaminante)]

# Lista para acumular resultados
registros = []

load_dotenv()
API_KEY = os.getenv("API_KEY")
headers = {'x-api-key': API_KEY}

# Iterar por cada sensor
for id in range(len(sensor)):

    sensor_id = sensor['SensorID'].iloc[id]
    location_id = sensor['LocationID'].iloc[id]
    location_name = sensor['LocationName'].iloc[id]

    print("procesando", id, sensor_id, location_id, location_name)

    base_url = f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements/hourly"

    all_results = []
    local_params = params.copy()
    local_params["page"] = 1

    MAX_PAGES = 100

    while True:

        max_retries = 3
        retries = 0
        success = False

        while retries < max_retries and not success:
            try:
                response = requests.get(base_url, headers=headers, params=local_params, timeout=30)

                if response.status_code == 429:
                    print("Rate limit alcanzado. Esperando 10 segundos...")
                    time.sleep(10)
                    continue

                if response.status_code != 200:
                    print(f"Error {response.status_code} en sensor {sensor_id}.")
                    break

                success = True  # solicitud completada correctamente

            except requests.exceptions.Timeout:
                retries += 1
                print(f"Timeout en sensor {sensor_id}, reintentando...")
                time.sleep(10)
                continue

            except requests.exceptions.RequestException as e:
                print(f"Error de red en sensor {sensor_id}: {e}")
                break

        if not success:
            print(f" Fallo persistente al acceder a sensor {sensor_id}. Saltando...")
            break

        data = response.json()
        results = data.get("results", [])

        if not results:
            print(f"Sin resultados en la página {local_params['page']}. Saliendo del bucle.")
            break

        all_results.extend(results)

        meta = data.get("meta", {})
        found = meta.get("found", 0)
        limit = meta.get("limit", 1000)
        page = meta.get("page", 1)

        # Protección por número máximo de páginas
        if page >= MAX_PAGES:
            print(f"Límite de {MAX_PAGES} páginas alcanzado. Saliendo por seguridad.")
            break

        if page * limit >= found:
            break
        else:
            local_params["page"] += 1

    # Convertir a DataFrame si hay datos
    df = pd.DataFrame(all_results)

    if not df.empty:
        for _, row in df.iterrows():
            parametro = row['parameter']['name']
            valor = row['value']
            fecha = row['coverage'].get('datetimeTo', {}).get('local')
            registros.append({
                'datetime': fecha,
                'estacion': location_id,
                'nombre': location_name,
                'parametro': parametro,
                'valor': valor
            })

# Crear DataFrame largo y pivotar
df_largo = pd.DataFrame(registros)

df_pivot = df_largo.pivot_table(
    index=['datetime', 'estacion', 'nombre'],
    columns='parametro',
    values='valor'
).reset_index()

df_filtrado = df_pivot[['datetime', 'estacion', 'nombre', 'o3', 'no2', 'co']]


df_filtrado.to_csv("mediciones.csv", index=False)


