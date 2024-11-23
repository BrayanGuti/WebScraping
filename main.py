import subprocess
import os
import time
import sys

def find_chromedriver():
    try:
        # Ejecutar el comando y capturar la salida
        result = subprocess.run(['find', '/', '-name', 'chromedriver'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        
        # Obtener las rutas de la salida
        paths = result.stdout.strip().split('\n')
        
        # Filtrar y devolver la primera ruta válida
        for path in paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
        
        # Si no se encuentra una ruta válida, devolver None
        return None
    except Exception as e:
        print(f"Error al ejecutar el comando: {e}")
        return None
    
# Obtener la ruta de chromedriver
path_chromedriver = find_chromedriver()

# Obtener la ruta del directorio raíz (donde está el script)
raiz = os.path.dirname(os.path.abspath(__file__))

# Ruta al archivo que se va a ejecutar
archivo = os.path.join(raiz, "webScraping.py")

# Ruta al entorno virtual (usando la carpeta 'venv')
venv_path = os.path.join(raiz, "venv", "Scripts" if sys.platform == "win32" else "bin", "activate")

if sys.platform == "win32":
    comando = f"cmd /c {venv_path} && python {archivo}"
elif sys.platform == "darwin" or sys.platform == "linux":
    comando = f"source {venv_path} && python {archivo} {path_chromedriver}"

# Ejecutar el archivo infinitamente con espera de 40 segundos
while True:
    print("Ejecutando el script...")
    subprocess.run(comando, shell=True, executable="/bin/bash" if sys.platform != "win32" else None)
    print("Esperando 40 segundos antes de la siguiente ejecución...")
    time.sleep(40)  # Espera 40 segundos antes de ejecutar nuevamente
