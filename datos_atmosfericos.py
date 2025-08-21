import requests
import pandas as pd
import estaciones
import time


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

dfs = []

Bahia_Cadiz = estaciones.localizacion(BahiaCadiz_params)
Jerez = estaciones.localizacion(Jerez_params)
Algeciras = estaciones.localizacion(Algeciras_params)



estat = pd.concat([Bahia_Cadiz, Jerez, Algeciras], axis=0, ignore_index=True)

for i in range(0,len(estat)):

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": float(estat['Latitude'][i]),
        "longitude": float(estat['Longitude'][i]),
        "start_date": "2022-01-01",
        "end_date": "2025-05-31",
        "hourly": ["temperature_2m", "direct_radiation", "wind_direction_10m", "wind_speed_10m", "relative_humidity_2m"],
        "timezone": "Europe/Berlin"
    }

    # Evitar sobrepasar el límite de llamadas por minuto
    if (i + 1) % 10 == 0:
        print("Esperando 60 segundos para respetar el rate limit...")
        time.sleep(60)

    success = False
    attempts = 0

    while not success and attempts < 3:
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                df_temp = pd.DataFrame.from_dict(data['hourly'])

                # Añadir información geográfica
                df_temp['Localizacion'] = estat['Localization'][i]
                df_temp['Name'] = estat['Name'][i]
                df_temp['Latitude'] = estat['Latitude'][i]
                df_temp['Longitude'] = estat['Longitude'][i]

                dfs.append(df_temp)
                success = True
            else:
                print(f"Error {response.status_code} en la estación {i}, reintentando...")
                attempts += 1
                time.sleep(10)

        except Exception as e:
            print(f"Excepción en la estación {i}: {e}")
            attempts += 1
            time.sleep(10)

# Combinar todos los DataFrames
df_final = pd.concat(dfs, ignore_index=True)
df_final.to_csv("datos_atmosfericos.csv", index=False)

