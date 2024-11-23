from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
import time

# Nombre del archivo CSV
csv_file = "banana_gun_metrics_extended.csv"

# Función para calcular cambios porcentuales
def calcular_cambio(data, intervalo):
    if len(data) >= intervalo:
        return ((data[-1] - data[-intervalo]) / data[-intervalo]) * 100
    return None

# Función para obtener el precio de Banana Gun usando Selenium
def obtener_precio(url):
    driver = webdriver.Chrome()  # Asegúrate de tener el driver adecuado instalado
    driver.get(url)
    
    try:
        # Esperar a que el precio se cargue (ajusta el tiempo y el selector si es necesario)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "WXGwg")))
        
        # Espera adicional para asegurarte de que la página esté completamente cargada
        time.sleep(10)
        
        # Obtener el contenido de la página después de esperar
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        price_raw = soup.find("span", class_="WXGwg").text
        driver.quit()
        return float(price_raw.replace("$", "").replace(",", ""))
    except Exception as e:
        print(f"Error al obtener el precio: {e}")
        driver.quit()
        return None

# Función para obtener las métricas principales usando Selenium
def obtener_metricas(url):
    driver = webdriver.Chrome()  # Asegúrate de tener el driver adecuado instalado
    driver.get(url)
    
    try:
        # Esperar a que las métricas se carguen
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "CoinMetrics_overflow-content__tlFu7")))
        
        # Espera adicional para asegurarte de que la página esté completamente cargada
        time.sleep(10)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        metrics = soup.find_all("div", class_="CoinMetrics_overflow-content__tlFu7")
        market_cap = float(metrics[0].text.replace("$", "").replace("M", "").replace(",", ""))
        volume = float(metrics[1].text.replace("$", "").replace("M", "").replace(",", ""))
        fdv = float(metrics[2].text.replace("$", "").replace("M", "").replace(",", ""))
        driver.quit()
        return market_cap, volume, fdv
    except Exception as e:
        print(f"Error al obtener las métricas: {e}")
        driver.quit()
        return None, None, None

# Función para cargar o crear el DataFrame
def cargar_o_crear_csv(csv_file):
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)
    else:
        columns = ["Fecha", "Precio"] + [f"Precio_hace_{i}min" for i in range(1, 2881)] + \
                  ["MarketCap", "Volumen", "FDV", 
                   "Cambio_5min", "Cambio_15min", "Cambio_30min", 
                   "Cambio_1hora", "Cambio_2horas", "Cambio_5horas", 
                   "Cambio_12horas", "Cambio_24horas", "Cambio_36horas"]
        return pd.DataFrame(columns=columns)

# Función para agregar los nuevos datos al DataFrame
def agregar_datos(df, price, market_cap, volume, fdv):
    now = datetime.now()
    new_data = {"Fecha": now.strftime("%Y-%m-%d %H:%M:%S"), "Precio": price, "MarketCap": market_cap, 
                "Volumen": volume, "FDV": fdv}
    
    # Agregar precios históricos por minuto
    for i in range(1, 2881):
        column = f"Precio_hace_{i}min"
        if len(df) >= i:
            new_data[column] = df.iloc[-i]["Precio"]
        else:
            new_data[column] = None
    
    # Calcular cambios porcentuales en diferentes intervalos
    precios = df["Precio"].dropna().tolist() + [price]
    new_data["Cambio_5min"] = calcular_cambio(precios, 5)
    new_data["Cambio_15min"] = calcular_cambio(precios, 15)
    new_data["Cambio_30min"] = calcular_cambio(precios, 30)
    new_data["Cambio_1hora"] = calcular_cambio(precios, 60)
    new_data["Cambio_2horas"] = calcular_cambio(precios, 120)
    new_data["Cambio_5horas"] = calcular_cambio(precios, 300)
    new_data["Cambio_12horas"] = calcular_cambio(precios, 720)
    new_data["Cambio_24horas"] = calcular_cambio(precios, 1440)
    new_data["Cambio_36horas"] = calcular_cambio(precios, 2160)  # Cambio de 36 horas
    
    # Añadir los nuevos datos al DataFrame
    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

    # Desplazar los precios y eliminar el primer valor si han pasado 2 días (2880 minutos)
    if len(df) > 2880:
        print("Eliminando el primer valor...")
        df = df.iloc[1:]  # Eliminar la primera fila
        df = df.reset_index(drop=True)  # Reindexar después de eliminar la fila
    return df

# Función para guardar el DataFrame actualizado
def guardar_csv(df, csv_file):
    df.to_csv(csv_file, index=False)
    print(f"Datos guardados en {csv_file}")

# Función principal que orquesta todo el flujo
def main():
    url = "https://coinmarketcap.com/currencies/banana-gun/"
    
    # Obtener el precio y las métricas
    price = obtener_precio(url)
    market_cap, volume, fdv = obtener_metricas(url)
    
    if price is not None and market_cap is not None:
        # Cargar o crear el DataFrame
        df = cargar_o_crear_csv(csv_file)
        
        # Agregar los datos actuales al DataFrame
        df = agregar_datos(df, price, market_cap, volume, fdv)
        
        # Guardar el DataFrame actualizado
        guardar_csv(df, csv_file)
    else:
        print("No se pudieron obtener los datos necesarios.")

if __name__ == "__main__":
    main()
