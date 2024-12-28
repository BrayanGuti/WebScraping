import os
import psycopg2

DATABASE_URL = "postgresql://brayan:njBtoSEjzXa2JoQaYAEUMw@database-bot-6179.j77.aws-us-west-2.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full"
conn = psycopg2.connect(DATABASE_URL)

with conn.cursor() as cur:
    cur.execute("SELECT now()")
    res = cur.fetchall()
    conn.commit()
    print(res)