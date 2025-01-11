import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk
from src.utils.utils import select_folder_input, select_folder_output, update_progress
from src.ocr.ocr import initialize_reader, run_processing, run_processing_threaded
from src.ui.splash import show_splash
import easyocr

def create_main_window(root):
    root.deiconify()  # Afișăm fereastra principală
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
    background_label.image = bg_photo  # Păstrăm referința la imagine
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Adăugăm widgeturi
    label_input = tk.Label(root, text="Selectează folderul de input:", bg='white')
    label_input.pack(pady=5)

    entry_input = tk.Entry(root, width=40)
    entry_input.pack(pady=5)

    button_input = tk.Button(root, text="Selectează Input", command=lambda: select_folder_input(entry_input))
    button_input.pack(pady=5)

    label_output = tk.Label(root, text="Selectează folderul de output:", bg='white')
    label_output.pack(pady=5)

    entry_output = tk.Entry(root, width=40)
    entry_output.pack(pady=5)

    button_output = tk.Button(root, text="Selectează Output", command=lambda: select_folder_output(entry_output))
    button_output.pack(pady=5)

    # Adăugăm un checkbox pentru utilizarea GPU-ului
    gpu_var = tk.BooleanVar(value=True)  # Valoarea implicită este True (folosește GPU)
    checkbox_gpu = tk.Checkbutton(root, text="Folosește GPU", variable=gpu_var, bg='white')
    checkbox_gpu.pack(pady=10)

    button_run = tk.Button(root, text="Rulează Procesarea", command=lambda: run_processing_threaded(gpu_var, progress_bar))
    button_run.pack(pady=20)

    # Adăugăm Progressbar
    progress_bar = Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)

    # Funcție pentru a închide aplicația corect
    def on_close():
        root.quit()   # Oprim fereastra Tkinter

    root.protocol("WM_DELETE_WINDOW", on_close)  # Setează comportamentul la închiderea ferestrei

# Creăm fereastra principală și o ascundem inițial
root = tk.Tk()
root.withdraw()  # Ascundem fereastra principală inițial
show_splash(root, create_main_window)
root.mainloop()  # Pornim bucla principală
