# Función para calcular cambios porcentuales
def calcular_cambio(data, intervalo):
    intervalo += 1  # Ajustar el intervalo para calcular el cambio correctamente
    if len(data) >= intervalo:
        return ((data[-1] - data[-intervalo]) / data[-intervalo]) * 100
    return None