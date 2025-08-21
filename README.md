# 14MBID_TFM
1. mediciones.py: descarga en fichero mediciones.csv los datos históricos de O₃, NO₂ y CO desde Open AQ, filtrando por estación y fecha utilizando la información obtenida por sensores.py.
2. datos_atmosfericos.py: utiliza la información geográfica obtenida por estaciones.py para realizar consultas a Open-Meteo y extraer los datos meteorológicos correspondientes para cada localización descargando los datos en el fichero datos_atmosfericos.csv.
3. estaciones.py: llama la API de Open AQ para identificar y obtener las coordenadas exactas de las estaciones de medición en las zonas de estudio.
4. sensores.py: obtiene los contaminantes disponibles en cada estación y sus rangos temporales entre otros datos.
5. Análisis_y_pretratamiento_datos.ipynb: lee los ficheros mediciones.csv y datos_atmosféricos.py para realizar las tareas de análisis, limpieza e integración. Crea csv datos_integrados.csv
6. Notebooks con experimentos XGBoost y RandomForest
