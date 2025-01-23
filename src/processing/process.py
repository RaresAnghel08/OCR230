import os
import shutil
from PIL import Image
import numpy as np
from src.processing.process_fields import process_fields
from src.processing.filtre import capitalize_words

reader = None  # Inițializăm variabila reader

def set_reader(ocr_reader):
    global reader
    reader = ocr_reader

# Funcția pentru procesarea unei zone
def proceseaza_zona(coord, idx, image):
    zona_decupata = image.crop(coord)  # Decupează zona
    zona_decupata = zona_decupata.resize((zona_decupata.width * 4, zona_decupata.height * 4))  # Mărire imagine
    zona_np = np.array(zona_decupata)  # Convertește în array NumPy
    rezultate = reader.readtext(zona_np)  # OCR
    text = " ".join([rezultat[1] for rezultat in rezultate])  # Extrage textul
    print(f"OCR text pentru zona {idx}: {text}")  # Afișează textul OCR pentru debug
    return text

# Funcția pentru procesarea fișierelor
def proceseaza_fisier(image_path, output_folder, coordonate):
    image = Image.open(image_path)  # Încarcă imaginea
    print(f"Procesăm fișierul: {image_path}")  # Debug: Afișăm numele fișierului procesat

    # Inițializăm variabilele pentru fiecare câmp
    strada, numar, localitate, judet, bloc, scara, etaj, apartament, cp, prenume, nume, cnp_total, email, phone, doiani = [""] * 15
    initiala_tatalui = ""
    folder_localitate_sec = ""

    # Parcurgem coordonatele și procesăm fiecare zonă
    for idx, coord in enumerate(coordonate):
        text_initial = proceseaza_zona(coord, idx, image)
        print(f"Text inițial pentru zona {idx}: {text_initial}")  # Debug: Afișăm textul inițial
        temp_prenume, temp_nume, temp_initiala_tatalui, temp_strada, temp_numar, temp_cnp_total, temp_email, temp_judet, temp_localitate, temp_cp, temp_bloc, temp_scara, temp_etaj, temp_apartament, temp_phone, temp_doiani,temp_folder_localitate = process_fields(text_initial, idx, False)  # debug_switch este True pentru debug
        # Atribuire valorilor returnate la variabilele finale
        if temp_prenume:
            prenume = temp_prenume
        if temp_nume:
            nume = temp_nume
        if temp_initiala_tatalui:
            initiala_tatalui = temp_initiala_tatalui
        if temp_strada:
            strada = temp_strada
        if temp_numar:
            numar = temp_numar
        if temp_cnp_total:
            cnp_total = temp_cnp_total
        if temp_email:
            email = temp_email
        if temp_judet:
            judet = temp_judet
        if temp_localitate:
            localitate = temp_localitate
        if temp_cp:
            cp = temp_cp
        if temp_bloc:
            bloc = temp_bloc
        if temp_scara:
            scara = temp_scara
        if temp_etaj:
            etaj = temp_etaj
        if temp_apartament:
            apartament = temp_apartament
        if temp_phone:
            phone = temp_phone
        if temp_doiani:
            doiani = temp_doiani
        if temp_folder_localitate:
            folder_localitate_sec = temp_folder_localitate
        else :
            folder_localitate_sec = localitate
        #else:
            #folder_localitate_sec = localitate
        # Debug: Afișăm valorile actualizate după fiecare iterație
        print(f"Variabile după process_fields: prenume={prenume}, nume={nume}, strada={strada}, etc.")  # Debug

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

    # Debug: Afișăm adresa generată
    print(f"Rezultate procesare: {nume} {prenume}, {email}, {phone}, {adresa}")  # Debug: Afișăm rezultatele procesării

    # Nume fișier nou
    nume_fisier = os.path.basename(image_path)
    nume_fisier_nou = f"{nume} {prenume}.jpg"

    # Creează folderul pentru localitate
    folder_localitate = os.path.join(output_folder, capitalize_words(folder_localitate_sec))
    if not os.path.exists(folder_localitate):
        os.makedirs(folder_localitate)

    # Mutăm și redenumim imaginea
    noua_cale_imagine = os.path.join(folder_localitate, nume_fisier_nou)
    shutil.move(image_path, noua_cale_imagine)

    # Debug: Afișăm calea imaginii mutate
    print(f"Imaginea {nume_fisier_nou} a fost mutată și redenumită în folderul {folder_localitate}")

    # Creează fișierul text
    fisier_txt = os.path.join(folder_localitate, f"{nume} {prenume}.txt")
    with open(fisier_txt, 'w', encoding='utf-8') as f:
        f.write(f"{nume}\n{initiala_tatalui}\n{prenume}\n{cnp_total}\n{adresa}\n{email}\n{phone}\n{doiani}")

    # Debug: Afișăm calea fișierului text creat
    print(f"Fișierul text {fisier_txt} a fost creat.")
