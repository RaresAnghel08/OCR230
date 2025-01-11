import tkinter as tk
from PIL import Image, ImageTk

class SplashScreen:
    def __init__(self, parent, callback):
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

        # Setăm imaginea splash
        splash_image = Image.open("Assets/cover.png").convert("RGBA")
        self.splash_photo = ImageTk.PhotoImage(splash_image)  # Păstrăm referința la imagine
        splash_label = tk.Label(self.splash, image=self.splash_photo)
        splash_label.pack()

        # Închidem splash screen-ul și apelăm funcția callback după 3 secunde
        self.splash.after(3000, self.close_splash)

    def close_splash(self):
        self.splash.destroy()
        self.callback(self.parent)

def show_splash(root, callback):
    SplashScreen(root, callback)
