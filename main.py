from imports import *
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
# from generare_adresa import corecteaza_adresa

# Creează un obiect EasyOCR Reader cu GPU activat
reader = easyocr.Reader(['en', 'ro'], gpu=False)

folder_input = ""
folder_output = ""

# Funcție pentru selectarea folderului de input
def select_folder_input():
    global folder_input
    folder_input = filedialog.askdirectory(title="Selectează folderul de input")
    if folder_input:
        entry_input.delete(0, tk.END)  # Șterge textul existent
        entry_input.insert(0, folder_input)  # Introduce calea selectată în entry

# Funcție pentru selectarea folderului de output
def select_folder_output():
    global folder_output
    folder_output = filedialog.askdirectory(title="Selectează folderul de output")
    if folder_output:
        entry_output.delete(0, tk.END)  # Șterge textul existent
        entry_output.insert(0, folder_output)  # Introduce calea selectată în entry

# Funcție care rulează procesul
def run_processing():
    # Verificăm dacă folderul de intrare există
    if not os.path.exists(folder_input):
        messagebox.showerror("Eroare", f"Folderul de intrare '{folder_input}' nu există!")
        return

    # Verificăm dacă folderul de ieșire există, dacă nu, îl creăm
    if not os.path.exists(folder_output):
        os.makedirs(folder_output)

    # Obținem lista de fișiere din folderul de intrare
    files = [f for f in os.listdir(folder_input) if f.lower().endswith(('jpg', 'jpeg', 'png'))]

    # Verificăm dacă sunt fișiere de procesat
    if not files:
        messagebox.showinfo("Info", "Nu au fost găsite fișiere de procesat în folderul de intrare.")
        return

    # Procesăm fiecare fișier din folder
    for file_name in files:
        # Construim calea completă a fișierului
        file_path = os.path.join(folder_input, file_name)
        
        # Apelăm funcția proceseaza_fisier pentru fiecare imagine
        print(f"Se procesează fișierul: {file_name}")
        try:
            proceseaza_fisier(file_path, folder_output)
        except Exception as e:
            print(f"Eroare la procesarea fișierului {file_name}: {e}")
            messagebox.showerror("Eroare", f"Eroare la procesarea fișierului {file_name}: {e}")
    
    # Afișăm un mesaj de succes
    messagebox.showinfo("Succes", "Procesarea fișierelor a fost finalizată.")

# Creăm fereastra principală
root = tk.Tk()
root.title("Procesare Formulare")
root.geometry("400x400")

# Adăugăm widgeturi
label_input = tk.Label(root, text="Selectează folderul de input:")
label_input.pack(pady=5)

entry_input = tk.Entry(root, width=40)
entry_input.pack(pady=5)

button_input = tk.Button(root, text="Selectează Input", command=select_folder_input)
button_input.pack(pady=5)

label_output = tk.Label(root, text="Selectează folderul de output:")
label_output.pack(pady=5)

entry_output = tk.Entry(root, width=40)
entry_output.pack(pady=5)

button_output = tk.Button(root, text="Selectează Output", command=select_folder_output)
button_output.pack(pady=5)

button_run = tk.Button(root, text="Rulează Procesarea", command=run_processing)
button_run.pack(pady=20)

# Rulăm aplicația Tkinter
root.mainloop()
