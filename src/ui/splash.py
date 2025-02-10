import tkinter as tk
from PIL import Image, ImageTk
import os

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

        # Încarcă imaginea și o convertește într-un obiect PhotoImage
        splash_image = Image.open(splash_image_path)
        self.splash_photo = ImageTk.PhotoImage(splash_image)

        # Afișăm imaginea în splash screen
        splash_label = tk.Label(self.splash, image=self.splash_photo)
        splash_label.pack()

        # Închidem splash screen-ul și apelăm funcția callback după 3 secunde
        self.splash.after(3000, self.close_splash)

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