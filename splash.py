import tkinter as tk
from PIL import Image, ImageTk

def show_splash(root, callback):
    # Splash screen
    splash = tk.Toplevel(root)
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

    def on_close_splash():
        splash.destroy()
        callback(root)

    # Închidem splash screen-ul și apelăm funcția callback după 3 secunde
    root.after(3000, on_close_splash)
    root.mainloop()
