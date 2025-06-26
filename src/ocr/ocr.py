import os
import tkinter as tk
from tkinter import messagebox
import threading
import easyocr
try:
    from efficient_ocr import EffOCR
except ImportError:
    print("EfficientOCR nu este instalat. Folosim EasyOCR ca fallback.")
    import easyocr
    EffOCR = None
from src.processing.process import set_reader, proceseaza_fisier
from src.utils.utils import update_progress
try:
    import pdf2image
except ImportError:
    print("pdf2image nu este instalat. Funcționalitatea PDF nu va fi disponibilă.")
    pdf2image = None
from PIL import Image
# from main import update_progress

# Inițializăm reader-ul cu o valoare implicită pentru GPU
reader = None

def initialize_reader(button_5_state):
    global reader
    global eff_ocr
    eff_ocr = False  # Setează True dacă EfficientOCR este disponibil, altfel False
    if EffOCR is not None and eff_ocr == True:
        # Folosim EfficientOCR dacă este disponibil
        try:
            if button_5_state == 1:
                print("Inițializăm EfficientOCR pentru GPU cu modele engleze...")
            else:
                print("Inițializăm EfficientOCR pentru CPU cu modele engleze...")
            
            reader = EffOCR(
                config={
                    'Recognizer': {
                        'char': {
                            'model_backend': 'onnx',
                            'model_dir': './models',
                            'hf_repo_id': 'dell-research-harvard/effocr_en/char_recognizer',
                        },
                        'word': {
                            'model_backend': 'onnx',
                            'model_dir': './models',
                            'hf_repo_id': 'dell-research-harvard/effocr_en/word_recognizer',
                        },
                    },
                    'Localizer': {
                        'model_dir': './models',
                        'hf_repo_id': 'dell-research-harvard/effocr_en',
                        'model_backend': 'onnx'
                    },
                    'Line': {
                        'model_dir': './models',
                        'hf_repo_id': 'dell-research-harvard/effocr_en',
                        'model_backend': 'onnx',
                    },
                },
                gpu=(button_5_state == 1)
            )
            print("EfficientOCR inițializat cu succes!")
        except Exception as e:
            print(f"Eroare la inițializarea EfficientOCR: {e}")
            print("Revenind la EasyOCR...")
            reader = None
    
    if EffOCR is None or reader is None and eff_ocr == False:
        # Fallback la EasyOCR
        try:
            if button_5_state == 1:
                print("Inițializăm EasyOCR pentru GPU.")
                reader = easyocr.Reader(['en', 'ro'], gpu=True)
            else:
                print("Inițializăm EasyOCR pentru CPU.")
                reader = easyocr.Reader(['en', 'ro'], gpu=False)
        except Exception as e:
            print(f"Eroare la inițializarea OCR: {e}")
            # Fallback final fără GPU
            reader = easyocr.Reader(['en', 'ro'], gpu=False)
    
    set_reader(reader)  # set reader-ul in process.py

def run_processing(button_5_state, progress_bar, folder_input, folder_output, coordonate, reset_progress_callback, root):
    # Inițializează reader-ul OCR
    initialize_reader(button_5_state)

    # Verificăm dacă folderul de intrare există
    if not os.path.exists(folder_input):
        messagebox.showerror("Eroare", f"Folderul de intrare '{folder_input}' nu există!")
        return

    # Verificăm dacă folderul de ieșire există, dacă nu, îl creăm
    if not os.path.exists(folder_output):
        os.makedirs(folder_output)

    # Procesăm PDF-urile dacă pdf2image este disponibil
    if pdf2image is not None:
        # Luăm fiecare PDF și îl convertim în imagini
        pdf_files = [os.path.join(folder_input, f) for f in os.listdir(folder_input) if f.lower().endswith('.pdf')]

        for pdf_file in pdf_files:
            try:
                images = pdf2image.convert_from_path(pdf_file, poppler_path=None) # teoretic nu deschide cmd
                # images = pdf2image.convert_from_path(pdf_file) # deschide cmd
                for i, image in enumerate(images):
                    # Redimensionăm imaginea la dimensiunea A4
                    image = image.resize((1241, 1754), Image.LANCZOS)
                    image_path = os.path.join(folder_input, f"{os.path.splitext(os.path.basename(pdf_file))[0]}_page_{i + 1}.png")
                    image.save(image_path)
                # Ștergem fișierul PDF
                os.remove(pdf_file)
            except Exception as e:
                print(f"Eroare la procesarea PDF {pdf_file}: {e}")
    else:
        print("PDF processing nu este disponibil. pdf2image nu este instalat.")
    
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
            update_progress(progress_bar, i + 1, total_files,root)

        # Afișăm un mesaj de succes
        messagebox.showinfo("Succes", "Procesarea fișierelor a fost finalizată.")
    except Exception as e:
        print(f"Eroare în timpul procesării: {e}")
        messagebox.showerror("Eroare", f"Eroare în timpul procesării: {e}")
    finally:
        # Call the reset progress callback after processing is complete
        reset_progress_callback()

'''
def run_processing_threaded(gpu_var, progress_bar, folder_input, folder_output, coordonate, reset_progress_callback):
    threading.Thread(target=lambda: run_processing(gpu_var, progress_bar, folder_input, folder_output, coordonate, reset_progress_callback)).start()
'''

def run_processing_threaded(button_5_state, progress_bar, folder_input, folder_output, coordonate, reset_progress_callback, root):
    threading.Thread(target=lambda: run_processing(button_5_state, progress_bar, folder_input, folder_output, coordonate, reset_progress_callback, root)).start()