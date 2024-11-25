from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def obtener_dominancia_btc():
    # Configuración del navegador (headless para evitar abrir el navegador visualmente)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service("ruta/a/chromedriver")  # Reemplaza con la ruta a tu chromedriver

    # Inicializar Selenium WebDriver
    driver = webdriver.Chrome()
    
    try:
        # URL de la página
        url = "https://es.tradingview.com/symbols/BTC.D/"
        driver.get(url)
        
        # Esperar explícitamente a que el valor esté visible en el DOM
        value_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "js-symbol-last"))
        )
        
        # Obtener el valor del DOM
        value = value_element.text
        
        return value
    finally:
        driver.quit()

