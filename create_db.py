import pyodbc
from app.config import settings

def create_db():
    server = settings.DB_HOST
    database = 'master'
    username = settings.DB_USER
    password = settings.DB_PASS
    driver = settings.DB_DRIVER

    conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;TrustServerCertificate=yes;"
    try:
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        cursor.execute(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'{settings.DB_NAME}') CREATE DATABASE {settings.DB_NAME}")
        print("Database created or already exists.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_db()
