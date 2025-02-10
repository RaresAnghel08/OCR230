import os
import tkinter as tk
from tkinter import messagebox
import threading
import easyocr
from src.processing.process import set_reader, proceseaza_fisier
from src.utils.utils import update_progress
import pdf2image
import PIL.Image as Image

# Inițializăm reader-ul cu o valoare implicită pentru GPU
reader = None

def initialize_reader(gpu_var):
    global reader
    use_gpu = gpu_var.get()  # Obține valoarea de la checkbox
    reader = easyocr.Reader(['en', 'ro'], gpu=use_gpu)
    set_reader(reader)  # Setează reader-ul în process.py

def run_processing(gpu_var, progress_bar, folder_input, folder_output, coordonate):
    # Inițializează reader-ul OCR
    initialize_reader(gpu_var)

    # Verificăm dacă folderul de intrare există
    if not os.path.exists(folder_input):
        messagebox.showerror("Eroare", f"Folderul de intrare '{folder_input}' nu există!")
        return

    # Verificăm dacă folderul de ieșire există, dacă nu, îl creăm
    if not os.path.exists(folder_output):
        os.makedirs(folder_output)

    #luam fiecare pdf si il convertim in imagini
    pdf_files = [os.path.join(folder_input, f) for f in os.listdir(folder_input) if f.lower().endswith('.pdf')]

    for pdf_file in pdf_files:
        images = pdf2image.convert_from_path(pdf_file)
        for i, image in enumerate(images):
            # Redimensionăm imaginea la dimensiunea A4
            image = image.resize((1241, 1754), Image.LANCZOS)
            image_path = os.path.join(folder_input, f"{os.path.splitext(os.path.basename(pdf_file))[0]}_page_{i + 1}.png")
            image.save(image_path)
        #remove pdf file
        os.remove(pdf_file)
    
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
            update_progress(progress_bar, i + 1, total_files)

        # Afișăm un mesaj de succes
        messagebox.showinfo("Succes", "Procesarea fișierelor a fost finalizată.")
    except Exception as e:
        print(f"Eroare în timpul procesării: {e}")
        messagebox.showerror("Eroare", f"Eroare în timpul procesării: {e}")

def run_processing_threaded(gpu_var, progress_bar, folder_input, folder_output, coordonate):
    threading.Thread(target=lambda: run_processing(gpu_var, progress_bar, folder_input, folder_output, coordonate)).start()