import psycopg2
from datetime import datetime
import csv

def read_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        # Devuelve la única fila en el archivo CSV como un diccionario
        return next(csv_reader, None)

def convert_to_numeric(value):
    """
    Convierte un valor a tipo float si es posible, de lo contrario devuelve None.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def agregar_datos_db(csv_file_path: str) -> None:
    # Ruta del archivo CSV
    csv_data = read_csv(csv_file_path)

    if not csv_data:
        print("El archivo CSV está vacío o no tiene datos.")
        exit()

    # Construir los datos a insertar en la base de datos
    data = {
        "fecha": datetime.now(),  # Fecha y hora actuales
        "precio": convert_to_numeric(csv_data.get("Precio", None)),
    }

    # Agregar los precios históricos al diccionario `data`
    for i in range(1, 2881):
        key = f"Precio_hace_{i}min"
        if key in csv_data:
            data[key] = convert_to_numeric(csv_data[key])

    # Agregar indicadores técnicos al diccionario `data`
    indicators = [
        "SMA_1min", "SMA_5min", "SMA_10min", "SMA_15min", "SMA_20min", 
        "SMA_30min", "SMA_45min", "SMA_1hora", "SMA_2horas", "SMA_5horas", 
        "SMA_6horas", "SMA_12horas", "SMA_24horas", "SMA_36horas",
        "EMA_1min", "EMA_5min", "EMA_10min", "EMA_15min", "EMA_20min", 
        "EMA_30min", "EMA_45min", "EMA_1hora", "EMA_2horas", "EMA_5horas", 
        "EMA_6horas", "EMA_12horas", "EMA_24horas", "EMA_36horas",
        "MACD", "MACD_Signal",
        "Porcentaje_Cambio_1minmin", "Porcentaje_Cambio_5minmin", "Porcentaje_Cambio_10minmin", 
        "Porcentaje_Cambio_15minmin", "Porcentaje_Cambio_20minmin", "Porcentaje_Cambio_30minmin", 
        "Porcentaje_Cambio_45minmin", "Porcentaje_Cambio_1horamin", "Porcentaje_Cambio_2horasmin", 
        "Porcentaje_Cambio_5horasmin", "Porcentaje_Cambio_6horasmin", "Porcentaje_Cambio_12horasmin", 
        "Porcentaje_Cambio_24horasmin", "Porcentaje_Cambio_36horasmin"
    ]

    # Agregar columnas adicionales al diccionario `data`
    data.update({
        "marketcap": convert_to_numeric(csv_data.get("MarketCap", None)),
        "volumen": convert_to_numeric(csv_data.get("Volumen", None)),
        "fdv": convert_to_numeric(csv_data.get("FDV", None)),
        "dominancia_btc": convert_to_numeric(csv_data.get("Dominancia_BTC", None)),
    })

    for indicator in indicators:
        if indicator in csv_data:
            data[indicator] = convert_to_numeric(csv_data[indicator])

    # Construir la consulta SQL
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))

    insert_query = f"""
    INSERT INTO market_data ({columns})
    VALUES ({placeholders})
    """

    # Imprimir la consulta SQL que se va a ejecutar

    # Conectar a la base de datos e insertar los datos
    DATABASE_URL = "postgresql://brayan:njBtoSEjzXa2JoQaYAEUMw@database-bot-6179.j77.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full"

    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cur:
            # Ejecutar la consulta
            cur.execute(insert_query, tuple(data.values()))
            conn.commit()
            print("Datos insertados con éxito en la tabla 'market_data'.")
    except Exception as e:
        print("Error al insertar los datos:", e)
    finally:
        conn.close()
