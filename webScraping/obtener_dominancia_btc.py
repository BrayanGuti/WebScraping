from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def obtener_dominancia_btc(driver):
    try:
        # URL de la página
        url = "https://es.tradingview.com/symbols/BTC.D/"
        driver.get(url)
        
        time.sleep(3)
        # Esperar explícitamente a que el valor esté visible en el DOM
        value_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "js-symbol-last"))
        )
        
        # Obtener el valor del DOM
        value = value_element.text
        value = float(value.replace(",", "."))

        return value
    except Exception as e:
        print("Error al obtener la dominancia de BTC:", e)
        return None
