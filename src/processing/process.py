import os
import shutil
from PIL import Image
import numpy as np
from src.processing.process_fields import process_fields
from src.processing.filtre import capitalize_words

global eff_ocr
eff_ocr = False  # Setează True dacă EfficientOCR este disponibil, altfel False
if eff_ocr == True:
    try:
        from efficient_ocr import EffOCR
    except ImportError:
        print("EfficientOCR nu este disponibil în process.py")
        EffOCR = None
else:
    import easyocr
    
reader = None  # Inițializăm variabila reader

def set_reader(ocr_reader):
    global reader
    reader = ocr_reader


# Funcția pentru procesarea unei zone
def proceseaza_zona(coord, idx, image):
    zona_decupata = image.crop(coord)  # Decupează zona
    if idx==15:
        zona_decupata = zona_decupata.resize((zona_decupata.width * 2, zona_decupata.height * 2))  # Mărire imagine
    else:
        zona_decupata = zona_decupata.resize((zona_decupata.width * 3, zona_decupata.height * 3))
    #save cropped image for debug in debug_media 
    debug_on = True  # Setează True pentru a activa debug-ul
    if debug_on==True:
        debug_media_folder = "debug_media"
        os.makedirs(debug_media_folder, exist_ok=True)  # Creează folderul debug_media dacă nu există
        zona_decupata.save(os.path.join(debug_media_folder, f"debug_cropped_{idx}.jpg"))  # Salvează imaginea decupată pentru debug
        # Mărim imaginea decupată pentru a îmbunătăți OCR-ul
        zona_decupata = zona_decupata.resize((zona_decupata.width * 3, zona_decupata.height * 3))  # Mărire imagine
        #save resized image for debug in debug_media folder
        zona_decupata.save(os.path.join(debug_media_folder, f"debug_resized_{idx}.jpg"))  # Salvează imaginea mărită pentru debug
    
    zona_np = np.array(zona_decupata)  # convert in numpy array
    
    # Verificăm tipul de reader și folosim metoda corespunzătoare
    try:
        if isinstance(reader, EffOCR) and eff_ocr == True :
            # Folosim EfficientOCR
            print(f"Folosim EfficientOCR pentru zona {idx}")
            rezultate = reader.infer(zona_np)
            text = rezultate if isinstance(rezultate, str) else str(rezultate)
        else:
            # Folosim EasyOCR (fallback)
            print(f"Folosim EasyOCR pentru zona {idx}")
            rezultate = reader.readtext(zona_np)
            text = " ".join([rezultat[1] for rezultat in rezultate])  # extract text from results
    except Exception as e:
        print(f"Eroare la OCR pentru zona {idx}: {e}")
        # Fallback la EasyOCR dacă EfficientOCR eșuează
        try:
            print(f"Fallback la EasyOCR pentru zona {idx}")
            rezultate = reader.readtext(zona_np)
            text = " ".join([rezultat[1] for rezultat in rezultate])
        except Exception as e2:
            print(f"Eroare și la EasyOCR pentru zona {idx}: {e2}")
            text = ""  # Return empty string if both fail
    
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
    temp_folder_localitate_mare = ""
    temp_folder_localitate_med = ""
    temp_folder_localitate_mic = ""
    folder_localitate = ""
    folder_localitate_mare = ""
    folder_localitate_med = ""
    folder_localitate_mic = ""

    # Parcurgem coordonatele și procesăm fiecare zonă
    for idx, coord in enumerate(coordonate):
        text_initial = proceseaza_zona(coord, idx, image)
        print(f"Text inițial pentru zona {idx}: {text_initial}")  # Debug: Afișăm textul inițial
        temp_prenume, temp_nume, temp_initiala_tatalui, temp_strada, temp_numar, temp_cnp_total, temp_email, temp_judet, temp_localitate, temp_cp, temp_bloc, temp_scara, temp_etaj, temp_apartament, temp_phone, temp_doiani, temp_folder_localitate_mic, temp_folder_localitate_med, temp_folder_localitate_mare = process_fields(text_initial, idx, False)  # debug_switch este True pentru debug
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
        if temp_folder_localitate_mic:
            folder_localitate_mic = temp_folder_localitate_mic
        if temp_folder_localitate_med:
            folder_localitate_med = temp_folder_localitate_med
        if temp_folder_localitate_mare:
            folder_localitate_mare = temp_folder_localitate_mare
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

    # Creează folderele pentru localitate (mare, mediu, mic)
    create_folder_hierarchy(output_folder, folder_localitate_mare, folder_localitate_med, folder_localitate_mic)

    # Mutăm și redenumim imaginea
    folder_localitate = os.path.join(output_folder, folder_localitate_mare.strip(), folder_localitate_med.strip(), folder_localitate_mic.strip())
    noua_cale_imagine = os.path.join(folder_localitate, nume_fisier_nou)
    print(f"Mutăm imaginea la: {noua_cale_imagine}")  # Debug
    shutil.move(image_path, noua_cale_imagine)

    # Creează fișierul text
    fisier_txt = os.path.join(folder_localitate, f"{nume} {prenume}.txt")
    with open(fisier_txt, 'w', encoding='utf-8') as f:
        f.write(f"{nume}\n{initiala_tatalui}\n{prenume}\n{cnp_total}\n{adresa}\n{phone}\n{email}\n{doiani}")
    
    print(f"Fișierul text {fisier_txt} a fost creat.")

def create_folder_hierarchy(output_folder, folder_localitate_mare, folder_localitate_med, folder_localitate_mic):
    # Creează folderele pentru localitate și subfolderele corespunzătoare
    folder_localitate_mare_path = os.path.join(output_folder, folder_localitate_mare.strip())
    folder_localitate_med_path = os.path.join(folder_localitate_mare_path, folder_localitate_med.strip())
    folder_localitate_mic_path = os.path.join(folder_localitate_med_path, folder_localitate_mic.strip())

    print(f"Creăm folderul ierarhic: {folder_localitate_mare_path} -> {folder_localitate_med_path} -> {folder_localitate_mic_path}")

    # Crează toate folderele dacă nu există
    os.makedirs(folder_localitate_mare_path, exist_ok=True)
    os.makedirs(folder_localitate_med_path, exist_ok=True)
    os.makedirs(folder_localitate_mic_path, exist_ok=True)

    print(f"Folderele au fost create sau există deja.")
