import easyocr
import numpy as np
from PIL import Image
import os 
import shutil

reader = None  # Inițializăm variabila reader

def set_reader(ocr_reader):
    global reader
    reader = ocr_reader

# Funcția pentru procesarea unei zone
def proceseaza_zona(coord, idx, image):
    zona_decupata = image.crop(coord)  # Decupează zona
    zona_np = np.array(zona_decupata)  # Convertește în array NumPy
    rezultate = reader.readtext(zona_np)  # OCR
    text = " ".join([rezultat[1] for rezultat in rezultate])  # Extrage textul
    return text

# Funcție pentru procesarea fișierelor
def proceseaza_fisier(image_path, output_folder, coordonate):
    from src.processing.filtre import capitalize_words, filtru_nume, filtru_litere, filtru_cifre  # Importăm filtrele necesare
    from src.processing.process_fields import process_fields  # Importăm funcția process_fields

    image = Image.open(image_path)  # Încarcă imaginea

    # Inițializăm variabilele pentru fiecare câmp
    strada, numar, localitate, judet, bloc, scara, etaj, apartament, cp, prenume, nume, cnp_total, email, phone, doiani = [""] * 15
    debug_switch = False

    # Parcurgem coordonatele și procesăm fiecare zonă
    for idx, coord in enumerate(coordonate):
        text_initial = proceseaza_zona(coord, idx, image)
        results = process_fields(text_initial, idx, debug_switch)
        
        # Alocăm valorile returnate de la process_fields
        text_filtrat, prenume, nume, initiala_tatalui, strada, numar, cnp_total, email, judet, localitate, cp, bloc, scara, etaj, apartament, phone, doiani = results

    # Generăm adresa
    adresa = f"Str. {strada} NR. {numar} LOC. {localitate} JUD. {judet}"
    if bloc:
        adresa += f" Bl. {bloc}"
    if scara:
        adresa += f" Sc. {scara}"
    if etaj:
        adresa += f" Et. {etaj}"
    if apartament:
        adresa += f" Ap. {apartament}"
    if cp:
        adresa += f" CP. {cp}"
    
    # Nume fișier nou
    nume_fisier = os.path.basename(image_path)
    nume_fisier_nou = f"{nume} {prenume}.jpg"

    # Creează folderul pentru localitate
    folder_localitate = os.path.join(output_folder, capitalize_words(localitate))
    if not os.path.exists(folder_localitate):
        os.makedirs(folder_localitate)

    # Mutăm și redenumim imaginea
    noua_cale_imagine = os.path.join(folder_localitate, nume_fisier_nou)
    shutil.move(image_path, noua_cale_imagine)

    # Creează fișierul text
    fisier_txt = os.path.join(folder_localitate, f"{nume} {prenume}.txt")
    with open(fisier_txt, 'w', encoding='utf-8') as f:
        f.write(f"{nume}\n{initiala_tatalui}\n{prenume}\n{cnp_total}\n{adresa}\n{email}\n{phone}\n{doiani}")

    print(f"Imaginea {nume_fisier_nou} a fost mutată și redenumită în folderul {folder_localitate}")
    print(f"Fișierul text {fisier_txt} a fost creat.")

# Funcție pentru procesarea fișierelor în paralel
def proceseaza_fisiere_in_paralel(fisiere, output_folder, coordonate):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        executor.map(lambda fisier: proceseaza_fisier(fisier, output_folder, coordonate), fisiere)
