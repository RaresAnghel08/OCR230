import os
from dotenv import load_dotenv
import psycopg2

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
host = os.environ.get('DATABASE_HOST')
user = os.environ.get('DATABASE_USER')
password = os.environ.get('DATABASE_PASSWORD')
dbname = os.environ.get('DATABASE_NAME')

try:
    conn = psycopg2.connect(host=host, user=user, password=password, dbname=dbname)
    cur = conn.cursor()
    # Șterge tabela veche dacă există
    cur.execute("DROP TABLE IF EXISTS ong;")
    conn.commit()
    # Creează tabela nouă cu admin_id
    cur.execute("""
        CREATE TABLE ong (
            id SERIAL PRIMARY KEY,
            nume VARCHAR(255) UNIQUE NOT NULL,
            admin_id VARCHAR(64) UNIQUE NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tabela 'ong' a fost recreată cu succes.")
except Exception as e:
    print(f"❌ Eroare la recrearea tabelei: {e}")