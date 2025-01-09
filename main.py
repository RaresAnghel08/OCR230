from imports import *
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import PhotoImage
from PIL import Image
import pystray
from pystray import MenuItem as item

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
    files = [os.path.join(folder_input, f) for f in os.listdir(folder_input) if f.lower().endswith(('jpg', 'jpeg', 'png'))]

    # Verificăm dacă sunt fișiere de procesat
    if not files:
        messagebox.showinfo("Info", "Nu au fost găsite fișiere de procesat în folderul de intrare.")
        return

    try:
        # Procesăm fișierele în paralel folosind funcția dedicată
        print("Se procesează fișierele în paralel...")
        proceseaza_fisiere_in_paralel(files, folder_output, coordonate)

        # Afișăm un mesaj de succes
        messagebox.showinfo("Succes", "Procesarea fișierelor a fost finalizată.")
    except Exception as e:
        print(f"Eroare în timpul procesării: {e}")
        messagebox.showerror("Eroare", f"Eroare în timpul procesării: {e}")

# Splash screen
splash = tk.Tk()
splash.title("Loading...")
splash.geometry("400x300+760+390")  # Centrat pentru un ecran 1920x1080
splash.overrideredirect(True)

from PIL import ImageTk

# Setăm imaginea splash
splash_image = Image.open("images/cover.png").convert("RGBA")
splash_photo = ImageTk.PhotoImage(splash_image)
splash_label = tk.Label(splash, image=splash_photo)  # Sau bg=None pentru transparență completă
splash_label.pack()

# Afișăm splash screen-ul pentru câteva secunde
splash.after(3000, splash.destroy)  # Distruge splash screen-ul după 3 secunde
splash.update_idletasks()
splash.mainloop()

# Creăm fereastra principală
root = tk.Tk()
root.title("Procesare Formulare")
root.geometry("400x300+760+390")

# Setează calea corectă pentru icoane
icon_path = 'images/favicon.ico'
icon_image = Image.open(icon_path)  # Folosim PIL pentru a deschide icoana

# Setăm imaginea favicon pentru Tkinter
favicon = PhotoImage(file='images/favicon.png')
root.iconphoto(False, favicon)

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

# Funcție pentru a închide aplicația corect
def on_close():
    root.quit()   # Oprim fereastra Tkinter

root.protocol("WM_DELETE_WINDOW", on_close)  # Setează comportamentul la închiderea ferestrei

# Rulăm aplicația Tkinter
root.mainloop()
