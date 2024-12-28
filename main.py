from datetime import datetime
import pandas as pd
import time
import os
from selenium import webdriver
from webScraping.obtener_dominancia_btc import obtener_dominancia_btc
from webScraping.obtener_datos_criptomoneda import obtener_datos
from dbManage.agregar_datos_db import agregar_datos_db
from selenium.webdriver.chrome.options import Options

# Nombre del archivo CSV
csv_file = "WorldCoin_metrics_extended.csv"

def cargar_o_crear_csv(csv_file):
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)
    else:
        columns = ["Fecha", "Precio"] + \
                  [f"Precio_hace_{i}min" for i in range(1, 2881)] + \
                  ["MarketCap", "Volumen", "FDV", "Dominancia_BTC"] + \
                  [f"SMA_{k}" for k in ["1min", "5min", "10min", "15min", "20min", "30min", 
                                           "45min", "1hora", "2horas", "5horas", "6horas", 
                                           "12horas", "24horas", "36horas"]] + \
                  [f"EMA_{k}" for k in ["1min", "5min", "10min", "15min", "20min", "30min", 
                                           "45min", "1hora", "2horas", "5horas", "6horas", 
                                           "12horas", "24horas", "36horas"]] + \
                  ["MACD", "MACD_Signal"]
        return pd.DataFrame(columns=columns)

def calcular_ema(data, periodo):
    if len(data) < periodo:
        return None
    ema = pd.Series(data).ewm(span=periodo, adjust=False).mean().iloc[-1]
    return ema

def calcular_macd(data):
    if len(data) < 26:
        return None, None
    ema_12 = calcular_ema(data, 12)
    ema_26 = calcular_ema(data, 26)
    if ema_12 is None or ema_26 is None:
        return None, None
    macd = ema_12 - ema_26
    macd_signal = calcular_ema([macd] * 9, 9)  # Calculando EMA de 9 períodos sobre el MACD
    return macd, macd_signal

def calcular_sma(data, intervalo):
    if len(data) >= intervalo:
        return sum(data[-intervalo:]) / intervalo
    return None

def calcular_porcentaje_cambio(precio_actual, precio_hace_n_minutos):
    if precio_hace_n_minutos is None or precio_hace_n_minutos == 0:
        return None
    return ((precio_actual - precio_hace_n_minutos) / precio_hace_n_minutos) * 100

def guardar_csv(df, csv_file):
    df.to_csv(csv_file, index=False)
    print(f"Datos guardados en {csv_file}")

def agregar_datos(df, price, market_cap, volume, fdv, dominancia_btc):
    now = datetime.now()
    new_data = {
        "Fecha": now.strftime("%Y-%m-%d %H:%M:%S"),
        "Precio": price,
        "Dominancia_BTC": dominancia_btc,
        "MarketCap": market_cap,
        "Volumen": volume,
        "FDV": fdv
    }

    for i in range(1, 2881):
        column = f"Precio_hace_{i}min"
        if len(df) > 0:
            # Si la columna anterior existe y tiene datos, úsala.
            prev_column = f"Precio_hace_{i-1}min"
            if prev_column in df.columns and not pd.isna(df.iloc[0][prev_column]):
                new_data[column] = df.iloc[0][prev_column]
            else:
                # Si no hay datos en la columna anterior, llena con None.
                new_data[column] = None
        else:
            # Si no hay datos en el DataFrame, llena con None.
            new_data[column] = None
    
        new_data[f"Precio_hace_1min"] = df.iloc[0]["Precio"] if not df.empty else None

    # Calcular SMA, EMA, MACD, MACD Signal y porcentaje de cambio en diferentes intervalos
    precios = (
        [new_data[f"Precio_hace_{i}min"] for i in range(2880, 0, -1) if f"Precio_hace_{i}min" in new_data]
        + [price]
    )
    precios = [p for p in precios if p is not None]

    intervalos = {
        "1min": 1,
        "5min": 5,
        "10min": 10,
        "15min": 15,
        "20min": 20,
        "30min": 30,
        "45min": 45,
        "1hora": 60,
        "2horas": 120,
        "5horas": 300,
        "6horas": 360,
        "12horas": 720,
        "24horas": 1440,
        "36horas": 2160,
    }
    for key, intervalo in intervalos.items():
        # SMA
        new_data[f"SMA_{key}"] = calcular_sma(precios, intervalo)
        # EMA
        new_data[f"EMA_{key}"] = calcular_ema(precios, intervalo)
        # Porcentaje de cambio
        precio_hace_n_minutos = precios[-intervalo] if len(precios) >= intervalo else None
        new_data[f"Porcentaje_Cambio_{key}min"] = calcular_porcentaje_cambio(price, precio_hace_n_minutos)

    # Calcular MACD y MACD Signal
    macd, macd_signal = calcular_macd(precios)
    new_data["MACD"] = macd
    new_data["MACD_Signal"] = macd_signal

    # Crear el nuevo DataFrame con una sola fila
    df_nuevo = pd.DataFrame([new_data])

    if(len(precios) == 2881):
        agregar_datos_db(csv_file)
    return df_nuevo

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar en modo headless (sin UI)
    chrome_options.add_argument("--no-sandbox")  # Requerido en algunas configuraciones de VM
    chrome_options.add_argument("--disable-dev-shm-usage")  # Para evitar problemas de memoria
    chrome_options.add_argument("--disable-gpu")  # Desactivar uso de GPU (opcional en headless)

    driver = webdriver.Chrome(options=chrome_options)
    url = "https://coinmarketcap.com/currencies/worldcoin-org/"

    while True:
        price, market_cap, volume, fdv = obtener_datos(url, driver) 

        dominancia_btc = obtener_dominancia_btc(driver)
  
        if price is not None and market_cap is not None and dominancia_btc is not None:
            df = cargar_o_crear_csv(csv_file)

            df = agregar_datos(df, price, market_cap, volume, fdv, dominancia_btc)

            guardar_csv(df, csv_file)
        else:
            print("No se pudieron obtener los datos necesarios.")

        # Esperar 1 minuto antes de volver a obtener los datos
        time.sleep(60)

if __name__ == "__main__":
    main()
