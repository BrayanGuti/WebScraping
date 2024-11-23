import subprocess
import os
import time
import sys

# Obtener la ruta del directorio raíz (donde está el script)
raiz = os.path.dirname(os.path.abspath(__file__))

# Ruta al archivo que se va a ejecutar
archivo = os.path.join(raiz, "webScraping.py")

# Ruta al entorno virtual (usando la carpeta 'venv')
venv_path = os.path.join(raiz, "venv", "Scripts" if sys.platform == "win32" else "bin", "activate")

if sys.platform == "win32":
    comando = f"cmd /c {venv_path} && python {archivo}"
elif sys.platform == "darwin" or sys.platform == "linux":
    comando = f"source {venv_path} && python {archivo}"

# Ejecutar el archivo infinitamente con espera de 40 segundos
while True:
    print("Ejecutando el script...")
    subprocess.run(comando, shell=True, executable="/bin/bash" if sys.platform != "win32" else None)
    print("Esperando 40 segundos antes de la siguiente ejecución...")
    time.sleep(40)  # Espera 40 segundos antes de ejecutar nuevamente
