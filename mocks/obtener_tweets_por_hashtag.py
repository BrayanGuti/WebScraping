import os
import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

COOKIE_FILE = "cookies.pkl"

def guardar_cookies(driver, path):
    with open(path, "wb") as file:
        pickle.dump(driver.get_cookies(), file)

def cargar_cookies(driver, path):
    if os.path.exists(path):
        try:
            with open(path, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    driver.add_cookie(cookie)
        except (EOFError, pickle.UnpicklingError) as e:
            print("Error al cargar cookies:", e)

def verificar_sesion_activa(driver):
    """
    Verifica si la sesión del usuario está activa basándose en la presencia de elementos clave
    visibles solo cuando el usuario ha iniciado sesión correctamente.

    Args:
        driver (webdriver): Instancia del navegador Selenium.

    Returns:
        bool: True si la sesión está activa, False en caso contrario.
    """
    try:
        # Navegar a la página principal de X (Twitter)
        driver.get("https://x.com/home")

        # Esperar un elemento único de la página de usuario autenticado
        WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.XPATH, '//div[@data-testid="tweetTextarea_0RichTextInputContainer"]'))
        )

        return True  # El elemento está presente, sesión activa
    except Exception as e:
        print("Sesión no activa o error al verificar:")
        return False  # No se pudo encontrar el elemento, sesión no activa



def iniciar_sesion(driver, correo, usuario, contrasena):
    driver.get("https://x.com/login")

    try:
        # Introducir correo
        login_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="text" and @type="text"]'))
        )
        login_input.send_keys(correo)
        login_input.send_keys(u'\ue007')  # Presionar Enter

        # Intentar verificar si es necesario introducir usuario o teléfono
        try:
            user_prompt = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//span[text()='Introduce tu número de teléfono o nombre de usuario']"))
            )
            if user_prompt:
                user_input = driver.find_element(By.XPATH, "//input[@name='text']")
                user_input.send_keys(usuario)
                user_input.send_keys(u'\ue007')  # Presionar Enter
        except Exception:
            # No se requiere introducir usuario o teléfono, continuar con la contraseña
            pass

        # Introducir contraseña
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="password" and @type="password"]'))
        )
        password_input.send_keys(contrasena)
        password_input.send_keys(u'\ue007')  # Presionar Enter

        # Esperar a que la página principal cargue
        WebDriverWait(driver, 10).until(
            EC.url_contains("home")
        )
        print("Inicio de sesión exitoso.")

    except Exception as e:
        print("Error durante el inicio de sesión:", e)

def obtener_tweets_por_hashtag(hashtag, correo, usuario, contrasena, ultimo_tweet, driver):
    if ultimo_tweet is not None:
        print(f"Buscando tweets más recientes que '{ultimo_tweet}'...")
    
    try:
        # Cargar cookies si existen
        if os.path.exists(COOKIE_FILE):
            cargar_cookies(driver, COOKIE_FILE)

        # Verificar si ya estamos autenticados
        if not verificar_sesion_activa(driver):
            print("Sesión no activa. Procediendo a iniciar sesión...")
            iniciar_sesion(driver, correo, usuario, contrasena)
        else:
            print("Sesión activa. Saltando inicio de sesión.")


        nuevos_tweets = 0
        ultimo_tweet_actual = None

        # Navegar a la página del hashtag
        driver.get(f"https://x.com/search?q=%23{hashtag}&src=recent_search_click&f=live")

        # Esperar a que la sección de tweets cargue
        while True:
            section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//section[@aria-labelledby="accessible-list-0"]'))
            )
            div = section.find_element(By.XPATH, './div/div')
            lista_de_tweets = div.find_elements(By.XPATH, './div')

            for tweet_element in lista_de_tweets:
                tweet_text = tweet_element.text.strip()

                if not ultimo_tweet_actual:
                    ultimo_tweet_actual = tweet_text  # Capturar el primer tweet encontrado

                if ultimo_tweet is None:
                    nuevos_tweets = 1  # Establecer en 1 si ultimo_tweet es None
                    guardar_cookies(driver, COOKIE_FILE)
                    return ultimo_tweet_actual, nuevos_tweets

                if tweet_text == ultimo_tweet:
                    guardar_cookies(driver, COOKIE_FILE)
                    return ultimo_tweet_actual, nuevos_tweets  # Encontrado el último conocido

                nuevos_tweets += 1

            # Si no encontramos el último tweet conocido, seguimos bajando
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Pausa para cargar más tweets

    except Exception as e:
        print("Error al obtener nuevos tweets:", e)
        return None, 0


driver = webdriver.Chrome()

try:
    # Uso de la función
    last_tweet,  cantidad_tweets = obtener_tweets_por_hashtag("neiro", "Brag.8631@gmail.com", "Pepe2913269666", "MUjJj#tqLUNWo2*0Jto9nY%@pEEwREN#Z2TzkyIfqa1KR3mfuZ2&WMM@", None, driver)
    
    print(last_tweet)
    print(cantidad_tweets)
    print("types")
    print(type(last_tweet))
    print(type(cantidad_tweets))
    
    time.sleep(2)
    last_tweet2, cantidad_tweets2 = obtener_tweets_por_hashtag("neiro", "Brag.8631@gmail.com", "Pepe2913269666", "MUjJj#tqLUNWo2*0Jto9nY%@pEEwREN#Z2TzkyIfqa1KR3mfuZ2&WMM@", last_tweet, driver)
    print(f"Último tweet conocido: {last_tweet2}")
    print(f"Se encontraron {cantidad_tweets2} nuevos tweets.")
    # time.sleep(2)   
    # last_tweet3, cantidad_tweets3 = obtener_tweets_por_hashtag("neiro", "Brag.8631@gmail.com", "Pepe2913269666", "MUjJj#tqLUNWo2*0Jto9nY%@pEEwREN#Z2TzkyIfqa1KR3mfuZ2&WMM@", last_tweet2, driver)



    # print(f"Último tweet conocido: {last_tweet3}")
    # print(f"Se encontraron {cantidad_tweets3} nuevos tweets.")

finally:
    driver.quit()