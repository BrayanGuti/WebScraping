import psycopg2

# Función para leer y mostrar datos de la tabla
def read_table():
    # Conexión a la base de datos
    DATABASE_URL = "postgresql://brayan:njBtoSEjzXa2JoQaYAEUMw@database-bot-6179.j77.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full"
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cur:
            # Ejecutar una consulta SELECT para obtener los datos
            query = "SELECT * FROM market_data;"
            cur.execute(query)
            
            # Obtener los nombres de las columnas
            col_names = [desc[0] for desc in cur.description]
            
            # Obtener todas las filas
            rows = cur.fetchall()
            
            # Mostrar los datos
            print("Datos de la tabla 'market_data':")
            print("\t".join(col_names))
            for row in rows:
                print("\t".join(map(str, row)))
    except Exception as e:
        print("Error al leer los datos:", e)
    finally:
        conn.close()

# Llamar a la función para leer la tabla
read_table()
