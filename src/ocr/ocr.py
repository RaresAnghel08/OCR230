import os
import tkinter as tk
from tkinter import messagebox
import threading

# Importăm easyocr doar când avem nevoie de el
easyocr = None
EffOCR = None

global eff_ocr
eff_ocr = False

# Variabilă globală pentru a controla procesarea
processing_active = False
stop_processing = False

def import_ocr_libraries():
    """Import condițional pentru bibliotecile OCR"""
    global easyocr, EffOCR
    
    try:
        if eff_ocr == True:
            print("Încercăm să importăm EfficientOCR...")
            try:
                from efficient_ocr import EffOCR
                print("EfficientOCR importat cu succes.")
                effocr = EffOCR(
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
    }
)
            except ImportError as e:
                print(f"EfficientOCR nu poate fi importat: {e}")
                EffOCR = None
        else:
            print("Importăm EasyOCR...")
            try:
                import easyocr
                print("EasyOCR importat cu succes.")
            except ImportError as e:
                print(f"EasyOCR nu poate fi importat: {e}")
                raise ImportError("EasyOCR este necesar pentru funcționarea aplicației")
    except Exception as e:
        print(f"Eroare generală la importul bibliotecilor OCR: {e}")
        print("Încercăm fallback la EasyOCR...")
        try:
            import easyocr
        except ImportError as e2:
            print(f"Eroare critică - nu s-a putut importa nici o bibliotecă OCR: {e2}")
            raise ImportError("Nu s-a putut importa nici EasyOCR, nici EfficientOCR")
        EffOCR = None

from src.processing.process import set_reader, proceseaza_fisier
from src.utils.utils import update_progress
from PIL import Image

# Variabilă globală pentru pdf2image
pdf2image = None

def import_pdf2image():
    """Import condițional pentru pdf2image"""
    global pdf2image
    try:
        import pdf2image as pdf2img
        pdf2image = pdf2img
        print("pdf2image importat cu succes.")
        return True
    except ImportError as e:
        print(f"pdf2image nu este disponibil: {e}")
        print("Funcționalitatea PDF nu va fi disponibilă.")
        pdf2image = None
        return False
    except Exception as e:
        print(f"Eroare neașteptată la importul pdf2image: {e}")
        pdf2image = None
        return False

# Inițializăm reader-ul cu o valoare implicită pentru GPU
reader = None

def initialize_reader(button_5_state):
    global reader
    
    # Importăm bibliotecile OCR doar când avem nevoie
    import_ocr_libraries()

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

def run_processing(button_5_state, progress_bar, folder_input, folder_output, coordonate, reset_progress_callback, root, update_button_callback=None, dashboard_callback=None, user_config=None):
    global processing_active, stop_processing
    
    # Setăm starea de procesare
    processing_active = True
    stop_processing = False
    
    # Resetăm contoarele pentru CNP-uri
    run_processing.cnp_stats = {'valid': 0, 'invalid': 0, 'duplicates': 0}
    
    # Actualizăm butonul la starea de procesare (Stop)
    if update_button_callback:
        update_button_callback(True)
    
    try:
        # Inițializează reader-ul OCR
        initialize_reader(button_5_state)
        
        # Inițializează pdf2image dacă este disponibil
        import_pdf2image()

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
                if stop_processing:  # Verificăm dacă trebuie să oprim
                    print("Procesarea a fost oprită de utilizator.")
                    return
                try:
                    images = pdf2image.convert_from_path(pdf_file)
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

        total_files = len(files)
        
        for i, file in enumerate(files):
            # Verificăm dacă trebuie să oprim procesarea
            if stop_processing:
                print("Procesarea a fost oprită de utilizator.")
                messagebox.showinfo("Oprit", f"Procesarea a fost oprită. Au fost procesate {i} din {total_files} fișiere.")
                return
            
            # Actualizăm dashboard-ul cu fișierul curent ÎNAINTE de procesare
            if dashboard_callback:
                dashboard_callback('current_file', os.path.basename(file))
                dashboard_callback('processed_files', i)  # Numărul de fișiere procesate până acum
                print(f"Dashboard: Procesez fișierul {os.path.basename(file)} ({i+1}/{total_files})")
                
            # Procesăm fiecare fișier și obținem CNP-ul real extras
            extracted_cnp = proceseaza_fisier(file, folder_output, coordonate)
            print(f"Procesăm fișierul: {file}")

            # Actualizăm progress bar-ul
            update_progress(progress_bar, i + 1, total_files, root)
            
            # Actualizăm dashboard-ul DUPĂ procesare cu statistici complete
            if dashboard_callback:
                dashboard_callback('processed_files', i + 1)  # Actualizăm cu fișierul procesat
                
                # Validăm CNP-ul real extras din OCR
                try:
                    # Importăm clasa ExcelManager pentru validarea CNP
                    from src.excel.excel_manager import ExcelManager
                    excel_manager = ExcelManager(folder_output)
                    
                    # Folosim CNP-ul real extras din OCR în loc de CNP-uri de test
                    if extracted_cnp and extracted_cnp.strip():
                        is_valid, message = excel_manager.validate_cnp(extracted_cnp.strip())
                        
                        # Actualizez contoarele
                        if is_valid:
                            run_processing.cnp_stats['valid'] += 1
                        else:
                            run_processing.cnp_stats['invalid'] += 1
                        
                        dashboard_callback('valid_cnp', run_processing.cnp_stats['valid'])
                        dashboard_callback('invalid_cnp', run_processing.cnp_stats['invalid'])
                        dashboard_callback('duplicates_found', run_processing.cnp_stats['duplicates'])
                        
                        print(f"CNP validat: {extracted_cnp} -> {'Valid' if is_valid else 'Invalid'} ({message})")
                    else:
                        print(f"CNP nu a fost extras corect din fișierul {os.path.basename(file)}")
                        # Incrementăm contorul de CNP-uri invalide pentru cazurile fără CNP
                        run_processing.cnp_stats['invalid'] += 1
                        dashboard_callback('invalid_cnp', run_processing.cnp_stats['invalid'])
                    
                    print(f"Dashboard actualizat: CNP valide={run_processing.cnp_stats['valid']}, invalide={run_processing.cnp_stats['invalid']}")
                        
                except Exception as e:
                    print(f"Eroare la validarea CNP direct: {e}")
                    import traceback
                    traceback.print_exc()

        # Afișăm un mesaj de succes doar dacă nu am fost opriți
        if not stop_processing:
            excel_path = os.path.join(folder_output, "Date_Persoane_OCR.xlsx")
            if os.path.exists(excel_path):
                messagebox.showinfo("Succes", f"Procesarea fișierelor a fost finalizată.\nFișierul Excel a fost actualizat: {excel_path}")
            else:
                messagebox.showinfo("Succes", "Procesarea fișierelor a fost finalizată.")
            
    except Exception as e:
        print(f"Eroare în timpul procesării: {e}")
        messagebox.showerror("Eroare", f"Eroare în timpul procesării: {e}")
    finally:
        # Resetăm starea de procesare
        processing_active = False
        stop_processing = False
        
        # 🔴 MARCHEAZĂ PROCESAREA CA FIIND COMPLETĂ PENTRU DASHBOARD
        if dashboard_callback:
            try:
                dashboard_callback('processing_complete', True)
                print("✅ Dashboard notificat că procesarea s-a terminat")
            except Exception as e:
                print(f"⚠️ Eroare la notificarea dashboard-ului: {e}")
        
        # Actualizăm butonul înapoi la starea inițială (Start)
        if update_button_callback:
            update_button_callback(False)
        
        # Afișăm raportul înainte de a deschide folderul și Excel-ul
        def open_final_results():
            """Deschide folderul de output și toate fișierele generate (Excel, PDF, CSV)"""
            # open output folder if it exists
            if os.path.exists(folder_output):
                os.startfile(folder_output)
                
            # open excel file if it exists
            excel_path = os.path.join(folder_output, "Date_Persoane_OCR.xlsx")
            if os.path.exists(excel_path):
                os.startfile(excel_path)
                
            # open PDF report if it exists
            pdf_path = os.path.join(folder_output, "Raport_OCR_F230.pdf")
            if os.path.exists(pdf_path):
                os.startfile(pdf_path)
                
            # Opțional: deschide și CSV-ul (poate fi prea mult)
            # csv_path = os.path.join(folder_output, "Date_Persoane_OCR.csv")
            # if os.path.exists(csv_path):
            #     os.startfile(csv_path)
        
        # Afișăm fereastra de rapoarte doar dacă nu am fost opriți
        if not stop_processing:
            try:
                from src.ui.rapoarte import show_rapoarte_window
                reports_window = show_rapoarte_window(folder_output, open_final_results, user_config)
            except Exception as e:
                print(f"Eroare la afișarea raportului: {e}")
                # Dacă raportul nu poate fi afișat, deschide direct rezultatele
                open_final_results()
        else:
            # Dacă procesarea a fost oprită, deschide direct rezultatele
            open_final_results()
        
        # Call the reset progress callback after processing is complete
        reset_progress_callback()
        
    

'''
def run_processing_threaded(gpu_var, progress_bar, folder_input, folder_output, coordonate, reset_progress_callback):
    threading.Thread(target=lambda: run_processing(gpu_var, progress_bar, folder_input, folder_output, coordonate, reset_progress_callback)).start()
'''

def run_processing_threaded(button_5_state, progress_bar, folder_input, folder_output, coordonate, reset_progress_callback, root, update_button_callback=None, dashboard_callback=None, user_config=None):
    threading.Thread(target=lambda: run_processing(button_5_state, progress_bar, folder_input, folder_output, coordonate, reset_progress_callback, root, update_button_callback, dashboard_callback, user_config)).start()

def stop_current_processing():
    """Oprește procesarea curentă"""
    global stop_processing
    stop_processing = True
    print("Solicitare de oprire a procesării...")

def is_processing_active():
    """Returnează True dacă procesarea este activă"""
    return processing_active