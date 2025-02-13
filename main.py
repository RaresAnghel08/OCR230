import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar
from PIL import Image, ImageTk
from src.utils.utils import select_folder_input, select_folder_output, update_progress
from src.ocr.ocr import initialize_reader, run_processing_threaded
from src.ui.splash import show_splash
from src.processing.coordonate import coordonate

# Setăm stilul CustomTkinter
ctk.set_appearance_mode("light")  # Poți schimba în "dark" dacă vrei
ctk.set_default_color_theme("blue")

# Variabile globale
folder_input = None
folder_output = None

def create_main_window(root):
    root.deiconify()
    root.title("F230-OCR")
    root.geometry("800x600")
    
    # Fundal și icon
    root.iconbitmap('Assets/favicon.ico')

    bg_image = Image.open("Assets/favicon40transparenta.png").resize((800, 600), Image.Resampling.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    background_label = ctk.CTkLabel(root, image=bg_photo, text="")
    background_label.image = bg_photo
    background_label.place(relwidth=1, relheight=1)

    # Selectare folder input
    label_input = ctk.CTkLabel(root, text="Folder de intrare", font=("Arial", 14, "bold"))
    label_input.pack(pady=5)

    entry_input = ctk.CTkEntry(root, width=400, font=("Arial", 12))
    entry_input.pack(pady=5)

    def on_select_folder_input():
        global folder_input
        folder_input = filedialog.askdirectory(title="Selectează folderul de intrare")
        if folder_input:
            entry_input.delete(0, "end")
            entry_input.insert(0, folder_input)

    button_input = ctk.CTkButton(root, text="📂 Selectează", command=on_select_folder_input)
    button_input.pack(pady=5)

    # Selectare folder output
    label_output = ctk.CTkLabel(root, text="Folder de ieșire", font=("Arial", 14, "bold"))
    label_output.pack(pady=5)

    entry_output = ctk.CTkEntry(root, width=400, font=("Arial", 12))
    entry_output.pack(pady=5)

    def on_select_folder_output():
        global folder_output
        folder_output = filedialog.askdirectory(title="Selectează folderul de ieșire")
        if folder_output:
            entry_output.delete(0, "end")
            entry_output.insert(0, folder_output)

    button_output = ctk.CTkButton(root, text="📁 Selectează", command=on_select_folder_output)
    button_output.pack(pady=5)

    # SWITCH pentru accelerare grafică
    gpu_var = ctk.BooleanVar(value=False)
    
    switch_gpu = ctk.CTkSwitch(root, text="Folosește accelerare grafică", variable=gpu_var, onvalue=True, offvalue=False)
    switch_gpu.pack(pady=10)

    # Progress bar
    progress_bar = Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=10)

    # Buton Start
    def reset_progress():
        progress_bar["value"] = 0

    button_run = ctk.CTkButton(root, text="Start", font=("Arial", 16, "bold"), width=200, height=40, 
                               fg_color="#4CAF50", hover_color="#45a049", text_color="white",
                               command=lambda: run_processing_threaded(gpu_var, progress_bar, folder_input, folder_output, coordonate, reset_progress))
    button_run.pack(pady=20)

    # Buton Ajutor
    button_help = ctk.CTkButton(root, text="Ajutor", fg_color="#CCCCCC", command=lambda: messagebox.showinfo("Ajutor", "Instrucțiuni de utilizare..."))
    button_help.pack(pady=5)

    # Închidere corectă a aplicației
    def on_close():
        root.quit()
        root.destroy()
        exit()

    root.protocol("WM_DELETE_WINDOW", on_close)

# Creare fereastră și afișare splash
root = ctk.CTk()
root.withdraw()
show_splash(root, create_main_window)
root.mainloop()
