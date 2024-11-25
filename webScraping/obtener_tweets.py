from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def obtener_tweets_por_hashtag(hashtag, correo, telefono, contrasena):
    """
    Función para obtener los tweets de un hashtag específico en X (anteriormente Twitter).
    
    :param hashtag: El hashtag a buscar (sin el símbolo #).
    :param correo: El correo electrónico para iniciar sesión.
    :param telefono: El número de teléfono o nombre de usuario para iniciar sesión.
    :param contrasena: La contraseña de la cuenta de X.
    """
    driver = webdriver.Chrome()  # Cambia esto al driver de tu navegador si no usas Chrome
    driver.get(f"https://x.com/search?q=%23{hashtag}&src=recent_search_click&f=live")

    try:
        # Esperar a que el input de correo esté presente
        login_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="text" and @type="text"]'))
        )
        print("Se encontró el input de correo.")
        
        # Introducir el correo electrónico en el input
        login_input.send_keys(correo)

        # Esperar a que el contenedor de botones esté presente
        buttons_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "r-nllxps"))
        )
        
        # Encontrar todos los botones dentro del contenedor y seleccionar el botón "Siguiente"
        buttons = buttons_container.find_elements(By.CLASS_NAME, "r-rs99b7")
        next_button = buttons[2]
        next_button.click()

        # Esperar a que el mensaje de texto de "Introduce tu número de teléfono..." esté presente
        elemento = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='Introduce tu número de teléfono o nombre de usuario']"))
        )
        print("Se encontró el mensaje de texto.")

        input_element = driver.find_element(By.XPATH, "//input[@name='text']")
        input_element.send_keys(telefono)

        print("Usuario ingresado y clic en 'Siguiente' realizado.")
        
        # Clic en el botón "Siguiente" nuevamente
        next_button = driver.find_element(By.XPATH, '//button[@data-testid="ocfEnterTextNextButton"]')
        next_button.click()
        print("Botón 'Siguiente' presionado después de introducir el usuario.")

        # Esperar a que el campo de contraseña esté presente
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="password" and @type="password"]'))
        )
        print("Se encontró el campo de contraseña.")

        # Introducir la contraseña
        password_input.send_keys(contrasena)
        print("Contraseña ingresada.")

        # Clic en el botón después de introducir la contraseña
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@data-testid="LoginForm_Login_Button"]'))
        )

        login_button.click()
        print("Botón de login presionado.")

        # Esperar a que la página cargue y cargar tweets
        time.sleep(10)  # Ajusta el tiempo de espera si es necesario

        # Aquí puedes agregar la lógica para extraer los tweets
        

    except Exception as e:
        print("Error encontrado:", e)  # Si no estamos en la página de inicio de sesión
        return []

    finally:
        # Cerrar el navegador después de la prueba
        driver.quit()

# Uso de la función
tweets = obtener_tweets_por_hashtag("pepe", "Brag.8631@gmail.com", "Pepe2913269666", "MUjJj#tqLUNWo2*0Jto9nY%@pEEwREN#Z2TzkyIfqa1KR3mfuZ2&WMM@")
for tweet in tweets:
    print(tweet)
