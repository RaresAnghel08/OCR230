from pathlib import Path
import webbrowser
from tkinter import Tk, Canvas, Button, PhotoImage
from tkinter import filedialog
import os
from src.utils.utils import select_folder_input, select_folder_output, update_progress
from src.ocr.ocr import initialize_reader, run_processing_threaded
from src.ui.splash import show_splash
from src.processing.coordonate import coordonate
from tkinter.ttk import Progressbar
from tkinter import messagebox

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "src/ui/assets"
PDF_PATH = OUTPUT_PATH / "src/ui/assets"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

folder_input = ""
folder_output = ""

root = Tk()
def reset_progress():
    """Reset the progress bar to 0%."""
    progress_bar['value'] = 0

root.geometry("800x600")
root.configure(bg="#FFFFFF")

canvas = Canvas(
    root,
    bg="#FFFFFF",
    height=600,
    width=800,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)

canvas.place(x=0, y=0)
canvas.create_rectangle(
    0.0,
    0.0,
    800.0,
    600.0,
    fill="#D9D9D9",
    outline="")

# Imagine pentru butonul Ajutor
button_image_ajutor = PhotoImage(file=relative_to_assets("button_ajutor.png"))

# Funcția de ajutor
def open_guide():
    guide_path = PDF_PATH / "guide.pdf"
    webbrowser.open(guide_path.as_uri())

Button_ajutor = Button(
    image=button_image_ajutor,
    borderwidth=0,
    highlightthickness=0,
    command=open_guide,
    relief="flat",
    activebackground="#D9D9D9",
    background="#D9D9D9"
)
Button_ajutor.place(
    x=723.0,
    y=567.0,
    width=61.0,
    height=26.012451171875
)

canvas.create_rectangle(
    -4.0,
    558.0,
    800.0,
    562.0,
    fill="#C4C4C4",
    outline="")

canvas.create_rectangle(
    28.0,
    535.0,
    772.0,
    547.0,
    fill="#000000",
    outline="")

canvas.create_text(
    323.0,
    571.0,
    anchor="nw",
    text="™ F230-OCR",
    fill="#000000",
    font=("Inter", 14 * -1)
)

canvas.create_text(
    14.0,
    571.0,
    anchor="nw",
    text="©2025 Rareș Anghel",
    fill="#000000",
    font=("Inter", 14 * -1)
)

canvas.create_text(
    320.0,
    18.0,
    anchor="nw",
    text="F230-OCR",
    fill="#000000",
    font=("Inter", 32 * -1)
)

image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    55.0,
    108.0,
    image=image_image_1
)

canvas.create_rectangle(
    23.0,
    215.0,
    778.0,
    271.0,
    fill="#D9D9D9",
    outline="")

image_image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    400.0,
    300.0,
    image=image_image_2
)

# Păstrăm imaginile 3 și 4
image_image_3 = PhotoImage(file=relative_to_assets("image_3.png"))
image_3 = canvas.create_image(
    397.0,
    290.0,
    image=image_image_3
)

image_image_4 = PhotoImage(file=relative_to_assets("image_4.png"))
image_4 = canvas.create_image(
    397.0,
    159.0,
    image=image_image_4
)

# Text pentru mesajul că nu s-a selectat folderul de intrare
entry_folder_text = canvas.create_text(
    297.0,
    150.0,
    anchor="nw",
    text="Nu ai selectat niciun folder",
    fill="#000000",
    font=("Inter", 16 * -1)
)

# Text pentru mesajul că nu s-a selectat folderul de ieșire
output_folder_text = canvas.create_text(
    298.0,
    281.0,
    anchor="nw",
    text="Nu ai selectat niciun folder",
    fill="#000000",
    font=("Inter", 16 * -1)
)

# Funcție pentru selectarea folderului de intrare
def select_input_folder():
    input_folder = filedialog.askdirectory()  # Deschide dialogul de selectare a folderului
    if input_folder:
        folder_name_input = os.path.basename(input_folder)  # Extrage doar numele folderului
        canvas.itemconfig(entry_folder_text, text=folder_name_input)  # Modifică textul
        canvas.coords(entry_folder_text, canvas.winfo_width() / 2, canvas.coords(entry_folder_text)[1])  # Centrează pe X
        global folder_input  # Asigură-te că folosești variabila globală
        folder_input = input_folder  # Actualizează folder_input cu calea completă a folderului
    else:
        canvas.itemconfig(entry_folder_text, text="Nu ai selectat niciun folder")
        #canvas.coords(entry_folder_text, canvas.winfo_width() / 2, canvas.coords(entry_folder_text)[1])  # Centrează pe X

# Funcție pentru selectarea folderului de ieșire
def select_output_folder():
    output_folder = filedialog.askdirectory()  # Deschide dialogul de selectare a folderului
    if output_folder:
        folder_name_output = os.path.basename(output_folder)  # Extrage doar numele folderului
        canvas.itemconfig(output_folder_text, text=folder_name_output)  # Modifică textul
        canvas.coords(output_folder_text, canvas.winfo_width() / 2, canvas.coords(output_folder_text)[1])  # Centrează pe X
        global folder_output  # Asigură-te că folosești variabila globală
        folder_output = output_folder  # Actualizează folder_output cu calea completă a folderului
    else:
        canvas.itemconfig(output_folder_text, text="Nu ai selectat niciun folder")
        #canvas.coords(output_folder_text, canvas.winfo_width() / 2, canvas.coords(output_folder_text)[1])  # Centrează pe X

# Imagine pentru butonul de ieșire (Button_output)
button_image_output = PhotoImage(file=relative_to_assets("button_output.png"))
Button_output = Button(
    image=button_image_output,
    borderwidth=0,
    highlightthickness=0,
    command=select_output_folder,
    relief="flat",
    activebackground="#D9D9D9",
    background="#D9D9D9"
)
Button_output.place(
    x=25.0,
    y=218.0,
    width=749.0,
    height=45.0
)

# Imagine pentru butonul de intrare (Button_input)
button_image_input = PhotoImage(file=relative_to_assets("button_input.png"))
Button_input = Button(
    image=button_image_input,
    borderwidth=0,
    highlightthickness=0,
    command=select_input_folder,
    relief="flat",
    activebackground="#D9D9D9",
    background="#D9D9D9"
)
Button_input.place(
    x=22.0,
    y=84.0,
    width=755.0,
    height=56.0
)
# Imagine pentru butonul de accelerație grafică (Button5)
button_image_5 = PhotoImage(file=relative_to_assets("button_5_on.png"))
button_image_5_off = PhotoImage(file=relative_to_assets("button_5_off.png"))

# Global variable to keep track of the button state
button_5_state = True

def toggle_button_5():
    global button_5_state  # Refer to the global button_5_state
    if button_5_state:
        button_5.config(image=button_image_5_off)
        button_5_state = False
        print("Buton accelerație grafică dezactivat")
    else:
        button_5.config(image=button_image_5)
        button_5_state = True
        print("Buton accelerație grafică activat")

# Imagine pentru butonul de accelerație grafică (Button5)
button_5 = Button(
    image=button_image_5,
    borderwidth=0,
    highlightthickness=0,
    command=toggle_button_5,
    relief="flat",
    activebackground="#D9D9D9",
    background="#D9D9D9"
)
button_5.place(
    x=470.0,
    y=455.0,
    width=42.0,
    height=28.0
)

def start_processing():
    # Verifică dacă folderul de intrare este selectat
    if not folder_input:
        messagebox.showwarning("Atenție", "Te rugăm să selectezi un folder de intrare.")

    # Verifică dacă folderul de ieșire este selectat
    elif not folder_output:
        messagebox.showwarning("Atenție", "Te rugăm să selectezi un folder de ieșire.")
        
    # Dacă ambele foldere sunt selectate, rulează procesarea
    else:
        run_processing_threaded(button_5_state, progress_bar, folder_input, folder_output, coordonate, reset_progress, root)
# Imagine pentru butonul Start (Button_start)
button_image_start = PhotoImage(file=relative_to_assets("button_start.png"))
Button_start = Button(
    image=button_image_start,
    borderwidth=0,
    highlightthickness=0,
    command=start_processing,
    relief="flat",
    activebackground="#D9D9D9",
    background="#D9D9D9"
)
Button_start.place(
    x=28.0,
    y=487.0,
    width=746.0,
    height=46.0
)
# Definirea Progress Bar-ului
progress_bar = Progressbar(root, orient="horizontal", length=744, mode="determinate")
progress_bar.place(x=28, y=535)  # Poziționăm progresul sub butonul de Start
'''
28.0,
    535.0,
    772.0,
    547.0,
'''
canvas.create_text(
    277.0,
    460.0,
    anchor="nw",
    text="Folosire accelerație grafică",
    fill="#1E1E1E",
    font=("Inter", 16 * -1)
)
def create_main_window(root):
    root.deiconify()
    root.title("F230-OCR")
    root.geometry("800x600")
    
    # Fundal și icon
    root.iconbitmap('Assets/favicon.ico')
    # Funcție pentru închidere corectă a aplicației
    def on_close():
        root.quit()   # Oprește event loop-ul Tkinter
        root.destroy()  # Distruge fereastra principală
        exit()  # Închide complet aplicația
    
    # Leagă funcția de închidere de evenimentul de închidere al ferestrei
    root.protocol("WM_DELETE_WINDOW", on_close)

root.withdraw()
show_splash(root, create_main_window)
root.mainloop()
