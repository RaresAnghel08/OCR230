import os
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, messagebox
from dotenv import load_dotenv
import psycopg2

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def add_ong_to_db(ong_name, admin_id):
	load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
	host = os.environ.get('PGHOST')
	user = os.environ.get('PGUSER')
	password = os.environ.get('PGPASSWORD')
	dbname = os.environ.get('PGDATABASE')
	try:
		conn = psycopg2.connect(host=host, user=user, password=password, dbname=dbname)
		cur = conn.cursor()
		cur.execute("INSERT INTO ong (nume, admin_id) VALUES (%s, %s)", (ong_name, admin_id))
		conn.commit()
		cur.close()
		conn.close()
		return True
	except Exception as e:
		print(f"Eroare la adăugare ONG: {e}")
		return False

def delete_ong_from_db(ong_name, admin_id):
	load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
	host = os.environ.get('PGHOST')
	user = os.environ.get('PGUSER')
	password = os.environ.get('PGPASSWORD')
	dbname = os.environ.get('PGDATABASE')
	try:
		conn = psycopg2.connect(host=host, user=user, password=password, dbname=dbname)
		cur = conn.cursor()
		cur.execute("DELETE FROM ong WHERE nume = %s AND admin_id = %s", (ong_name, admin_id))
		deleted = cur.rowcount
		conn.commit()
		cur.close()
		conn.close()
		return deleted > 0
	except Exception as e:
		print(f"Eroare la ștergerea ONG: {e}")
		return False

def show_add_ong_window():
	window = Tk()
	window.title("Adaugă ONG în Database")
	window.geometry("400x200")
	window.configure(bg="#D9D9D9")
	window.resizable(False, False)

	canvas = Canvas(window, bg="#D9D9D9", height=200, width=400, bd=0, highlightthickness=0, relief="ridge")
	canvas.place(x=0, y=0)

	canvas.create_text(200, 30, anchor="center", text="Adaugă ONG nou", fill="#000", font=("Inter", 18, "bold"))
	canvas.create_text(50, 80, anchor="nw", text="Nume ONG:", fill="#000", font=("Inter", 12))
	canvas.create_text(50, 120, anchor="nw", text="ID Unic (admin):", fill="#000", font=("Inter", 12))

	ong_entry = Entry(window, font=("Inter", 12), bg="white", relief="solid", bd=1)
	ong_entry.place(x=170, y=75, width=170, height=30)
	admin_id_entry = Entry(window, font=("Inter", 12), bg="white", relief="solid", bd=1)
	admin_id_entry.place(x=170, y=115, width=170, height=30)

	status_label = canvas.create_text(200, 53, anchor="center", text="", fill="#FF0000", font=("Inter", 10))

	def on_add():
		ong_name = ong_entry.get().strip()
		admin_id = admin_id_entry.get().strip()
		if not ong_name or not admin_id:
			canvas.itemconfig(status_label, text="❌ Completează numele ONG-ului și ID-ul unic!")
			return
		if add_ong_to_db(ong_name, admin_id):
			canvas.itemconfig(status_label, text="✅ ONG adăugat cu succes!", fill="#00AA00")
			ong_entry.delete(0, 'end')
			admin_id_entry.delete(0, 'end')
		else:
			canvas.itemconfig(status_label, text="❌ Eroare la adăugare ONG!", fill="#FF0000")

	def on_delete():
		ong_name = ong_entry.get().strip()
		admin_id = admin_id_entry.get().strip()
		if not ong_name or not admin_id:
			canvas.itemconfig(status_label, text="❌ Completează numele ONG-ului și ID-ul unic pentru ștergere!")
			return
		if delete_ong_from_db(ong_name, admin_id):
			canvas.itemconfig(status_label, text="✅ ONG șters cu succes!", fill="#00AA00")
			ong_entry.delete(0, 'end')
			admin_id_entry.delete(0, 'end')
		else:
			canvas.itemconfig(status_label, text="❌ ONG-ul nu a fost găsit sau eroare la ștergere!", fill="#FF0000")

	add_button = Button(window, text="Adaugă ONG", command=on_add, font=("Inter", 12, "bold"), bg="#4CAF50", fg="white", relief="raised", bd=2)
	add_button.place(x=70, y=155, width=120, height=35)

	delete_button = Button(window, text="Șterge ONG", command=on_delete, font=("Inter", 12, "bold"), bg="#CC4444", fg="white", relief="raised", bd=2)
	delete_button.place(x=210, y=155, width=120, height=35)
    
	# Set window icon
	icon_path = Path(__file__).parent / "Assets" / "favicon.ico"
	try:
		window.iconbitmap(str(icon_path))
	except Exception:
		pass

	window.mainloop()

if __name__ == "__main__":
	show_add_ong_window()