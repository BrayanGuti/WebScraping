from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def obtener_datos(url, driver):
    driver.get(url)
    
    try:
        # Esperar a que la página cargue completamente
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "WXGwg")))  # Esperar por el precio
        time.sleep(12)  # Espera adicional para asegurar la carga completa de la página

        # Obtener el contenido de la página después de esperar
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Obtener el precio
        price_raw = soup.find("span", class_="WXGwg").text
        price = float(price_raw.replace("$", "").replace(",", ""))

        # Obtener las métricas
        metrics = soup.find_all("div", class_="CoinMetrics_overflow-content__tlFu7")
        market_cap = float(metrics[0].text.replace("$", "").replace("M", "").replace(",", "").replace("B", ""))
        volume = float(metrics[1].text.replace("$", "").replace("M", "").replace(",", "").replace("B", ""))
        fdv = float(metrics[2].text.replace("$", "").replace("M", "").replace(",", "").replace("B", ""))
        
        return price, market_cap, volume, fdv
        
    except Exception as e:
        print(f"Error al obtener los datos: {e}")
        return None, None, None, None
