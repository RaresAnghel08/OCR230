import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import scipy
class SplashScreen:
    def __init__(self, parent, callback, splash_image_path):
        self.parent = parent
        self.callback = callback
        self.splash = tk.Toplevel(parent)
        self.splash.title("Loading...")

        # Dimensiunile splash screen-ului
        splash_width = 400
        splash_height = 300

        # Dimensiunile ecranului (în acest caz 1920x1080)
        screen_width = self.splash.winfo_screenwidth()
        screen_height = self.splash.winfo_screenheight()

        # Calculăm poziția centrului pentru splash screen
        splash_position_right = int(screen_width/2 - splash_width/2)
        splash_position_down = int(screen_height/2 - splash_height/2)

        # Setăm dimensiunea și poziția splash screen-ului
        self.splash.geometry(f"{splash_width}x{splash_height}+{splash_position_right}+{splash_position_down}")
        self.splash.overrideredirect(True)

        # Creează canvas-ul și bara de progres imediat, imaginea după idle
        self.canvas = tk.Canvas(self.splash, width=400, height=300, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.progress = ttk.Progressbar(self.splash, mode='determinate', length=300, maximum=100)
        self.progress.place(in_=self.canvas, relx=0.5, rely=0.88, anchor="center")
        self.progress['value'] = 0
        self.progress_step = 100 / 30
        self.update_progress(0)

        # Încarcă imaginea după ce UI-ul a apărut (asigură afișare rapidă splash)
        self.splash.after_idle(self.load_image, splash_image_path)

        # Închidem splash screen-ul și apelăm funcția callback după 3 secunde
        self.splash.after(3000, self.close_splash)

    def load_image(self, splash_image_path):
        try:
            # Încarcă imaginea și o convertește într-un obiect PhotoImage
            splash_image = Image.open(splash_image_path)
            self.splash_photo = ImageTk.PhotoImage(splash_image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.splash_photo)
        except Exception as e:
            pass  # Dacă nu se poate încărca imaginea, continuă fără ea

    def update_progress(self, count):
        if count <= 30:
            self.progress['value'] = count * self.progress_step
            self.splash.after(100, self.update_progress, count + 1)

    def close_splash(self):
        self.splash.destroy()
        self.callback(self.parent)

def show_splash(root, callback):
    try:
        # Obținem directorul principal al proiectului
        project_dir = os.path.dirname(os.path.abspath(__file__))  # Obține directorul în care se află scriptul curent (src/ui)

        # Construim calea completă către fișierul cover.png
        assets_dir = os.path.join(project_dir, '..', '..', 'Assets')  # Mergem două nivele înapoi pentru a ajunge în directorul principal
        splash_image_path = os.path.join(assets_dir, 'cover.png')

        # Verificăm dacă fișierul există
        if os.path.exists(splash_image_path):
            SplashScreen(root, callback, splash_image_path)
        else:
            callback(root)
    except Exception as e:
        print(f"Error loading splash screen: {e}")
        callback(root)