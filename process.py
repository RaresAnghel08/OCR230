from imports import *
import os
import sys
import shutil
import easyocr
from PIL import Image
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from process_fields import process_fields

reader = None

def set_reader(ocr_reader):
    global reader
    reader = ocr_reader

# Funcția pentru procesarea unei zone
def proceseaza_zona(coord, idx, image):
    zona_decupata = image.crop(coord)  # Decupează zona
    # Mărimim imaginea pentru o procesare mai detaliată
    zona_decupata = zona_decupata.resize((zona_decupata.width * 4, zona_decupata.height * 4))  # Mărire imagine
    zona_np = np.array(zona_decupata)  # Convertește în array NumPy
    rezultate = reader.readtext(zona_np)  # OCR
    text = " ".join([rezultat[1] for rezultat in rezultate])  # Extrage textul
    return text

# Funcție pentru procesarea fișierelor
def proceseaza_fisier(image_path, output_folder, coordonate):
    # Încarcă imaginea
    image = Image.open(image_path)

    # Inițializăm variabilele pentru fiecare câmp
    strada, numar, localitate, judet, bloc, scara, etaj, apartament, cp, prenume, nume, cnp_total, email, phone, doiani = [""] * 15
    debug_switch = False
    
    # Funcție auxiliară pentru debug
    def debug_afisare(idx, nume_camp, text_initial, text_filtrat):
        print(f"Zona {idx + 1}: {nume_camp}")
        print(f"Text inițial: {text_initial}")
        print(f"Text filtrat: {text_filtrat}")
        print("*" * 50)

    # Parcurgem coordonatele și procesăm fiecare zonă
    for idx, coord in enumerate(coordonate):
        text_initial = proceseaza_zona(coord, idx, image)
        text_filtrat = ""
        results = process_fields(text_initial, idx, debug_switch)
        text_filtrat, prenume, nume, initiala_tatalui, strada, numar, cnp_total, email, phone, doiani = results
        
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
    with ThreadPoolExecutor() as executor:
        executor.map(lambda fisier: proceseaza_fisier(fisier, output_folder, coordonate), fisiere)
