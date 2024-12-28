import os
import psycopg2

# URL de tu base de datos
DATABASE_URL = "postgresql://brayan:njBtoSEjzXa2JoQaYAEUMw@database-bot-6179.j77.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full"

# Conexión a la base de datos
conn = psycopg2.connect(DATABASE_URL)

# Crear la tabla
try:
    with conn.cursor() as cur:
        # Generar las columnas dinámicamente para los precios históricos
        historical_prices = ",\n".join([f"precio_hace_{i}min NUMERIC" for i in range(1, 2881)])

        # Definir el esquema SQL de la tabla
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS market_data (
            id SERIAL PRIMARY KEY,
            fecha TIMESTAMP NOT NULL, -- Fecha y hora del registro
            precio NUMERIC, -- Precio actual
            {historical_prices}, -- Precios históricos
            marketcap NUMERIC, -- Market Cap
            volumen NUMERIC, -- Volumen
            fdv NUMERIC, -- FDV (Fully Diluted Valuation)
            dominancia_btc NUMERIC, -- Dominancia de BTC

            -- SMA (Simple Moving Averages) para diferentes periodos
            sma_1min NUMERIC,
            sma_5min NUMERIC,
            sma_10min NUMERIC,
            sma_15min NUMERIC,
            sma_20min NUMERIC,
            sma_30min NUMERIC,
            sma_45min NUMERIC,
            sma_1hora NUMERIC,
            sma_2horas NUMERIC,
            sma_5horas NUMERIC,
            sma_6horas NUMERIC,
            sma_12horas NUMERIC,
            sma_24horas NUMERIC,
            sma_36horas NUMERIC,

            -- EMA (Exponential Moving Averages) para diferentes periodos
            ema_1min NUMERIC,
            ema_5min NUMERIC,
            ema_10min NUMERIC,
            ema_15min NUMERIC,
            ema_20min NUMERIC,
            ema_30min NUMERIC,
            ema_45min NUMERIC,
            ema_1hora NUMERIC,
            ema_2horas NUMERIC,
            ema_5horas NUMERIC,
            ema_6horas NUMERIC,
            ema_12horas NUMERIC,
            ema_24horas NUMERIC,
            ema_36horas NUMERIC,

            -- MACD y su señal
            macd NUMERIC,
            macd_signal NUMERIC,

            -- Porcentajes de cambio en diferentes periodos
            porcentaje_cambio_1minmin NUMERIC,
            porcentaje_cambio_5minmin NUMERIC,
            porcentaje_cambio_10minmin NUMERIC,
            porcentaje_cambio_15minmin NUMERIC,
            porcentaje_cambio_20minmin NUMERIC,
            porcentaje_cambio_30minmin NUMERIC,
            porcentaje_cambio_45minmin NUMERIC,
            porcentaje_cambio_1horamin NUMERIC,
            porcentaje_cambio_2horasmin NUMERIC,
            porcentaje_cambio_5horasmin NUMERIC,
            porcentaje_cambio_6horasmin NUMERIC,
            porcentaje_cambio_12horasmin NUMERIC,
            porcentaje_cambio_24horasmin NUMERIC,
            porcentaje_cambio_36horasmin NUMERIC
        );
        """

        # Ejecutar la consulta para crear la tabla
        cur.execute(create_table_query)
        conn.commit()
        print("Tabla 'market_data' creada con éxito.")

except Exception as e:
    print("Error al crear la tabla:", e)

finally:
    # Cerrar la conexión
    conn.close()
