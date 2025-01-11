from imports import *
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk
import easyocr
from concurrent.futures import ThreadPoolExecutor
from process import set_reader, proceseaza_fisier, proceseaza_fisiere_in_paralel

# Inițializăm reader-ul cu o valoare implicită pentru GPU
reader = None

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

# Funcție pentru actualizarea progress bar-ului
def update_progress(current, total):
    progress_bar["value"] = current
    progress_bar["maximum"] = total
    progress_bar.update_idletasks()

# Funcție pentru inițializarea reader-ului OCR
def initialize_reader():
    global reader
    use_gpu = gpu_var.get()  # Obține valoarea de la checkbox
    reader = easyocr.Reader(['en', 'ro'], gpu=use_gpu)
    set_reader(reader)  # Setează reader-ul în process.py

# Funcție care rulează procesul
def run_processing():
    # Inițializează reader-ul OCR
    initialize_reader()

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
        total_files = len(files)
        
        for i, file in enumerate(files):
            # Procesăm fiecare fișier
            proceseaza_fisier(file, folder_output, coordonate)
            print(f"Procesăm fișierul: {file}")

            # Actualizăm progress bar-ul
            update_progress(i + 1, total_files)

        # Afișăm un mesaj de succes
        messagebox.showinfo("Succes", "Procesarea fișierelor a fost finalizată.")
    except Exception as e:
        print(f"Eroare în timpul procesării: {e}")
        messagebox.showerror("Eroare", f"Eroare în timpul procesării: {e}")

def run_processing_threaded():
    threading.Thread(target=run_processing).start()

# Splash screen
splash = tk.Tk()
splash.title("Loading...")

# Dimensiunile splash screen-ului
splash_width = 400
splash_height = 300

# Dimensiunile ecranului (în acest caz 1920x1080)
screen_width = splash.winfo_screenwidth()
screen_height = splash.winfo_screenheight()

# Calculăm poziția centrului pentru splash screen
splash_position_right = int(screen_width/2 - splash_width/2)
splash_position_down = int(screen_height/2 - splash_height/2)

# Setăm dimensiunea și poziția splash screen-ului
splash.geometry(f"{splash_width}x{splash_height}+{splash_position_right}+{splash_position_down}")
splash.overrideredirect(True)

# Setăm imaginea splash
splash_image = Image.open("Assets/cover.png").convert("RGBA")
splash_photo = ImageTk.PhotoImage(splash_image)
splash_label = tk.Label(splash, image=splash_photo)
splash_label.pack()

# Afișăm splash screen-ul pentru câteva secunde
splash.after(3000, splash.destroy)  # Distruge splash screen-ul după 3 secunde
splash.update_idletasks()
splash.mainloop()

# Creăm fereastra principală
root = tk.Tk()
root.title("Procesare Formulare")

# Dimensiunile ferestrei Tkinter
window_width = 800
window_height = 600

# Dimensiunile ecranului (în acest caz 1920x1080)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculăm poziția centrului pentru fereastra Tkinter
position_right = int(screen_width/2 - window_width/2)
position_down = int(screen_height/2 - window_height/2)

# Setăm dimensiunea și poziția ferestrei Tkinter
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

root.iconbitmap('Assets/favicon.ico')

# Setăm background-ul pentru fereastra principală 
bg_image = Image.open("Assets/favicon40transparenta.png").convert("RGBA")
bg_photo = ImageTk.PhotoImage(bg_image)
background_label = tk.Label(root, image=bg_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# Adăugăm widgeturi
label_input = tk.Label(root, text="Selectează folderul de input:", bg='white')
label_input.pack(pady=5)

entry_input = tk.Entry(root, width=40)
entry_input.pack(pady=5)

button_input = tk.Button(root, text="Selectează Input", command=select_folder_input)
button_input.pack(pady=5)

label_output = tk.Label(root, text="Selectează folderul de output:", bg='white')
label_output.pack(pady=5)

entry_output = tk.Entry(root, width=40)
entry_output.pack(pady=5)

button_output = tk.Button(root, text="Selectează Output", command=select_folder_output)
button_output.pack(pady=5)

# Adăugăm un checkbox pentru utilizarea GPU-ului
gpu_var = tk.BooleanVar(value=True)  # Valoarea implicită este True (folosește GPU)
checkbox_gpu = tk.Checkbutton(root, text="Folosește GPU", variable=gpu_var, bg='white')
checkbox_gpu.pack(pady=10)

button_run = tk.Button(root, text="Rulează Procesarea", command=run_processing_threaded)
button_run.pack(pady=20)

# Adăugăm Progressbar
progress_bar = Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

# Funcție pentru a închide aplicația corect
def on_close():
    root.quit()   # Oprim fereastra Tkinter

root.protocol("WM_DELETE_WINDOW", on_close)  # Setează comportamentul la închiderea ferestrei

# Rulăm aplicația Tkinter
root.mainloop()
