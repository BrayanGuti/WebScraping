from datetime import datetime
import pandas as pd
import os
from selenium import webdriver
from webScraping.obtener_dominancia_btc import obtener_dominancia_btc
from webScraping.obtener_datos_criptomoneda import obtener_datos

# Nombre del archivo CSV
csv_file = "WorldCoin_metrics_extended.csv"

# Función para cargar o crear el DataFrame
def cargar_o_crear_csv(csv_file):
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)
    else:
        columns = ["Fecha", "Precio", "Dominancia_BTC"] + \
                  [f"Precio_hace_{i}min" for i in range(1, 2881)] + \
                  ["MarketCap", "Volumen", "FDV"] + \
                  [f"SMA_{k}" for k in ["1min", "5min", "10min", "15min", "20min", "30min", 
                                           "45min", "1hora", "2horas", "5horas", "6horas", 
                                           "12horas", "24horas", "36horas"]] + \
                  [f"EMA_{k}" for k in ["1min", "5min", "10min", "15min", "20min", "30min", 
                                           "45min", "1hora", "2horas", "5horas", "6horas", 
                                           "12horas", "24horas", "36horas"]] + \
                  [f"Porcentaje_Cambio_{i}min" for i in [1, 5, 10, 15, 20, 30, 45, 60, 120, 300, 360, 720, 1440, 2160]] + \
                  ["MACD", "MACD_Signal"]
        return pd.DataFrame(columns=columns)

# Función para calcular EMA
def calcular_ema(data, periodo):
    if len(data) < periodo:
        return None
    ema = pd.Series(data).ewm(span=periodo, adjust=False).mean().iloc[-1]
    return ema

# Función para calcular el MACD y su línea de señal
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

# Función para calcular el porcentaje de cambio
def calcular_porcentaje_cambio(precio_actual, precio_hace_n_minutos):
    if precio_hace_n_minutos is None or precio_hace_n_minutos == 0:
        return None
    return ((precio_actual - precio_hace_n_minutos) / precio_hace_n_minutos) * 100

# Función para guardar el DataFrame actualizado
def guardar_csv(df, csv_file):
    df.to_csv(csv_file, index=False)
    print(f"Datos guardados en {csv_file}")

# Función para agregar los nuevos datos al DataFrame
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

    # Agregar precios históricos por minuto
    for i in range(1, 2881):
        column = f"Precio_hace_{i}min"
        if len(df) >= i:
            new_data[column] = df.iloc[-i]["Precio"]
        else:
            new_data[column] = None

    # Calcular SMA, EMA, MACD, MACD Signal y porcentaje de cambio en diferentes intervalos
    precios = df["Precio"].dropna().tolist() + [price]
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
        precio_hace_n_minutos = df.iloc[-intervalo]["Precio"] if len(df) >= intervalo else None
        new_data[f"Porcentaje_Cambio_{key}min"] = calcular_porcentaje_cambio(price, precio_hace_n_minutos)

    # Calcular MACD y MACD Signal
    macd, macd_signal = calcular_macd(precios)
    new_data["MACD"] = macd
    new_data["MACD_Signal"] = macd_signal

    # Añadir los nuevos datos al DataFrame
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

    # Desplazar los precios y eliminar el primer valor si han pasado 2 días (2880 minutos)
    if len(df) > 2880:
        print("Eliminando el primer valor...")
        df = df.iloc[1:]  # Eliminar la primera fila
        df = df.reset_index(drop=True)  # Reindexar después de eliminar la fila

    # Reorganizar las columnas para mover Dominancia_BTC después de FDV
    columnas = list(df.columns)
    columnas.remove("Dominancia_BTC")
    index_fdv = columnas.index("FDV")
    columnas.insert(index_fdv + 1, "Dominancia_BTC")
    df = df[columnas]

    return df

# Main loop para ejecutar el scraping
def main():
    driver = webdriver.Chrome()
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

if __name__ == "__main__":
    main()
