import os
from dotenv import load_dotenv
import psycopg2

def print_ong_table():
    # Asigură-te că .env e încărcat din root-ul proiectului
    load_dotenv(dotenv_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))
    host = os.environ.get('PGHOST')
    user = os.environ.get('PGUSER')
    password = os.environ.get('PGPASSWORD')
    dbname = os.environ.get('PGDATABASE')
    try:
        conn = psycopg2.connect(host=host, user=user, password=password, dbname=dbname)
        cur = conn.cursor()
        cur.execute("SELECT id, nume, admin_id FROM ong ORDER BY id")
        rows = cur.fetchall()
        print("ID | NUME ONG | ADMIN_ID")
        print("---------------------------------------------")
        for row in rows:
            print(f"{row[0]} | {row[1]} | {row[2]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Eroare la citirea bazei de date: {e}")

if __name__ == "__main__":
    print_ong_table()