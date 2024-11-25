from datetime import datetime
import pandas as pd
import os

from Auxiliar.calcular_cambio import calcular_cambio
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
                  [f"Cambio_{k}" for k in ["1min", "5min", "10min", "15min", "20min", "30min", 
                                           "45min", "1hora", "2horas", "5horas", "6horas", 
                                           "12horas", "24horas", "36horas"]]
        return pd.DataFrame(columns=columns)

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

    # Calcular cambios porcentuales en diferentes intervalos
    precios = df["Precio"].dropna().tolist() + [price]
    intervalos = {
        "Cambio_1min": 1,
        "Cambio_5min": 5,
        "Cambio_10min": 10,
        "Cambio_15min": 15,
        "Cambio_20min": 20,
        "Cambio_30min": 30,
        "Cambio_45min": 45,
        "Cambio_1hora": 60,
        "Cambio_2horas": 120,
        "Cambio_5horas": 300,
        "Cambio_6horas": 360,
        "Cambio_12horas": 720,
        "Cambio_24horas": 1440,
        "Cambio_36horas": 2160,
    }
    for key, intervalo in intervalos.items():
        new_data[key] = calcular_cambio(precios, intervalo)

    # Añadir los nuevos datos al DataFrame
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

    # Desplazar los precios y eliminar el primer valor si han pasado 2 días (2880 minutos)
    if len(df) > 2880:
        print("Eliminando el primer valor...")
        df = df.iloc[1:]  # Eliminar la primera fila
        df = df.reset_index(drop=True)  # Reindexar después de eliminar la fila

    # Reorganizar las columnas para mover Dominancia_BTC después de FDV
    columnas = list(df.columns)
    # Quitar "Dominancia_BTC" para reintegrarla en la posición deseada
    columnas.remove("Dominancia_BTC")
    # Obtener el índice de FDV y colocar Dominancia_BTC después
    index_fdv = columnas.index("FDV")
    columnas.insert(index_fdv + 1, "Dominancia_BTC")
    # Reordenar el DataFrame
    df = df[columnas]

    return df

# Función para guardar el DataFrame actualizado
def guardar_csv(df, csv_file):
    df.to_csv(csv_file, index=False)
    print(f"Datos guardados en {csv_file}")

# Función principal que orquesta todo el flujo
def main():
    url = "https://coinmarketcap.com/currencies/worldcoin-org/"
    
    # Obtener el precio y las métricas
    price, market_cap, volume, fdv = obtener_datos(url) 
    
    # Obtener la dominancia de BTC
    dominancia_btc = obtener_dominancia_btc()
    
    if price is not None and market_cap is not None and dominancia_btc is not None:
        # Cargar o crear el DataFrame
        df = cargar_o_crear_csv(csv_file)
        
        # Agregar los datos actuales al DataFrame
        df = agregar_datos(df, price, market_cap, volume, fdv, dominancia_btc)
        
        # Guardar el DataFrame actualizado
        guardar_csv(df, csv_file)
    else:
        print("No se pudieron obtener los datos necesarios.")

if __name__ == "__main__":
    main()
