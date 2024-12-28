import psycopg2

# Función para limpiar la tabla eliminando todas las filas
def clear_table():
    # Conexión a la base de datos
    DATABASE_URL = "postgresql://brayan:njBtoSEjzXa2JoQaYAEUMw@database-bot-6179.j77.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full"
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cur:
            # Ejecutar la consulta para vaciar la tabla
            query = "TRUNCATE TABLE market_data;"
            cur.execute(query)
            conn.commit()  # Confirmar los cambios
            print("La tabla 'market_data' ha sido limpiada exitosamente.")
    except Exception as e:
        print("Error al limpiar la tabla:", e)
    finally:
        if conn:
            conn.close()

# Llamar a la función para limpiar la tabla
clear_table()
