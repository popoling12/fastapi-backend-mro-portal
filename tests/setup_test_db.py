import os
import psycopg2

try:
    from app.core.config import settings
    POSTGRES_SERVER = settings.POSTGRES_SERVER
    POSTGRES_PORT = getattr(settings, 'POSTGRES_PORT', 5432)
    POSTGRES_USER = settings.POSTGRES_USER
    POSTGRES_PASSWORD = settings.POSTGRES_PASSWORD
    POSTGRES_DB = settings.POSTGRES_DB
except Exception as e:
    print(f"[WARN] Could not import settings from app.core.config: {e}")
    POSTGRES_SERVER = os.environ.get("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT", 5432)
    POSTGRES_USER = os.environ.get("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "admin123")
    POSTGRES_DB = os.environ.get("POSTGRES_DB", "mydb")

def create_test_database():
    try:
        print(f"Connecting to Postgres server {POSTGRES_SERVER}:{POSTGRES_PORT} as {POSTGRES_USER}")
        conn = psycopg2.connect(
            host=POSTGRES_SERVER,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        test_db_name = f"{POSTGRES_DB}_test"
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{test_db_name}'")
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(f"CREATE DATABASE {test_db_name}")
            print(f"Created test database: {test_db_name}")
        else:
            print(f"Test database {test_db_name} already exists")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Failed to create test database: {e}")
        raise

if __name__ == "__main__":
    create_test_database() 