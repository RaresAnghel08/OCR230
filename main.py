import os
import shutil
from PIL import Image
import easyocr
import re
import numpy as np
from coordonate import coordonate

# Căile directoarelor
folder_input = "fisiere"  # Folderul cu imagini
folder_output = "FORMULARE"  # Folderul unde vor fi salvate subfolderele cu localitățile

# Funcție pentru a păstra doar cifre (fără spații)
def filtru_cifre(text):
    return ''.join(re.findall(r'[0-9]', text))  # Păstrează doar cifrele

# Funcție pentru a păstra doar litere (fără spații și alte caractere)
def filtru_litere(text):
    text = text.replace('-', ' ')
    return ''.join(re.findall(r'[a-zA-ZăâîșțĂÂÎȘȚ ]', text))  # Păstrează doar literele

def filtru_nume(text):
    # virgula si cratima sa fie spatiu
    text = text.replace('-', ' ')
    text = text.replace(',', ' ')
    return ''.join(re.findall(r'[a-zA-ZăâîșțĂÂÎȘȚ ]', text))  # Păstrează doar literele
# Creează un obiect EasyOCR Reader cu GPU activat
reader = easyocr.Reader(['en', 'ro'], gpu=False)

# Funcție pentru procesarea unei zone
def proceseaza_zona(coord, idx, image):
    zona_decupata = image.crop(coord)  # Decupează zona
    
    # Mărimim imaginea pentru o procesare mai detaliată
    if idx == 13:  # Apartament (zona 14)
        zona_decupata = zona_decupata.resize((zona_decupata.width * 4, zona_decupata.height * 4))  # Mărire imagine
    elif idx == 6:  # Email (zona 7)
        zona_decupata = zona_decupata.resize((zona_decupata.width * 3, zona_decupata.height * 3))  # Mărire imagine
    else:
        zona_decupata = zona_decupata.resize((zona_decupata.width * 4, zona_decupata.height * 4))  # Mărire imagine
    zona_np = np.array(zona_decupata)  # Convertește în array NumPy
    rezultate = reader.readtext(zona_np)  # OCR
    text = " ".join([rezultat[1] for rezultat in rezultate])  # Extrage textul
    return text

# Funcție pentru a capitaliza prima literă din fiecare cuvânt
def capitalize_words(text):
    return ' '.join([word.capitalize() for word in text.split()])

# Funcție pentru procesarea fișierelor
def proceseaza_fisier(image_path):
    # Încarcă imaginea
    image = Image.open(image_path)

    # Inițializăm variabilele pentru fiecare câmp
    strada = ""
    numar = ""
    localitate = ""
    judet = ""
    bloc = ""
    scara = ""
    etaj = ""
    apartament = ""
    cp = ""
    prenume = ""
    nume = ""
    cnp_total = ""
    email = ""

    # Funcție auxiliară pentru debug
    def debug_afisare(idx, nume_camp, text_initial, text_filtrat):
        print(f"Zona {idx + 1}: {nume_camp}")
        print(f"Text inițial: {text_initial}")
        print(f"Text filtrat: {text_filtrat}")
        print("*" * 50)

    # Parcurgem coordonatele și procesăm fiecare zonă
    for idx, coord in enumerate(coordonate):
        try:
            text_initial = proceseaza_zona(coord, idx, image)
            text_filtrat = ""

            if idx == 0:  # Prenume (zona 1)
                text_filtrat = capitalize_words(filtru_nume(text_initial))
                prenume = text_filtrat
                debug_afisare(idx, "Prenume", text_initial, text_filtrat)
            elif idx == 1:  # Nume (zona 2)
                text_filtrat = capitalize_words(filtru_nume(text_initial))
                nume = text_filtrat
                debug_afisare(idx, "Nume", text_initial, text_filtrat)
            elif idx == 2:  # Inițiala tatălui (zona 3)
                text_filtrat = filtru_litere(text_initial)
                initiala_tatalui = text_filtrat
                debug_afisare(idx, "Inițiala tatălui", text_initial, text_filtrat)
            elif idx == 3:  # Strada (zona 4)
                text_filtrat = text_initial.capitalize()
                strada = text_filtrat
                debug_afisare(idx, "Strada", text_initial, text_filtrat)
            elif idx == 4:  # Număr (zona 5)
                text_filtrat = text_initial.lstrip('0')
                numar = text_filtrat
                debug_afisare(idx, "Număr", text_initial, text_filtrat)
            elif idx == 8:  # Localitate (zona 9)
                text_filtrat = filtru_litere(text_initial)
                localitate = text_filtrat
                debug_afisare(idx, "Localitate", text_initial, text_filtrat)
            elif idx == 7:  # Județ (zona 8)
                text_filtrat = filtru_litere(text_initial)
                judet = text_filtrat
                debug_afisare(idx, "Județ", text_initial, text_filtrat)
            elif idx == 10:  # Bloc (zona 11)
                text_filtrat = text_initial.upper() if text_initial else ""
                bloc = text_filtrat
                debug_afisare(idx, "Bloc", text_initial, text_filtrat)
            elif idx == 11:  # Scara (zona 12)
                text_filtrat = text_initial.upper() if text_initial else ""
                scara = text_filtrat
                debug_afisare(idx, "Scara", text_initial, text_filtrat)
            elif idx == 12:  # Etaj (zona 13)
                text_filtrat = filtru_cifre(text_initial) if text_initial else ""
                etaj = text_filtrat
                debug_afisare(idx, "Etaj", text_initial, text_filtrat)
            elif idx == 13:  # Apartament (zona 14)
                text_filtrat = filtru_cifre(text_initial) if text_initial else ""
                apartament = text_filtrat
                debug_afisare(idx, "Apartament", text_initial, text_filtrat)
            elif idx == 9:  # Cod postal (zona 10)
                text_filtrat = filtru_cifre(text_initial) if text_initial else ""
                cp = text_filtrat
                debug_afisare(idx, "Cod postal", text_initial, text_filtrat)
            elif idx == 5:  # CNP (zona 6)
                text_filtrat = filtru_cifre(text_initial)
                cnp_total += text_filtrat
                debug_afisare(idx, "CNP", text_initial, text_filtrat)
            elif idx == 6:  # Email (zona 7)
                text_filtrat = text_initial.strip()
                email = text_filtrat
                debug_afisare(idx, "Email", text_initial, text_filtrat)

        except Exception as e:
            print(f"Eroare la procesarea zonei {idx + 1}: {e}")
            continue

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
    folder_localitate = os.path.join(folder_output, capitalize_words(localitate))
    if not os.path.exists(folder_localitate):
        os.makedirs(folder_localitate)

    # Mutăm și redenumim imaginea
    noua_cale_imagine = os.path.join(folder_localitate, nume_fisier_nou)
    shutil.move(image_path, noua_cale_imagine)

    # Creează fișierul text
    fisier_txt = os.path.join(folder_localitate, f"{nume} {prenume}.txt")
    with open(fisier_txt, 'w', encoding='utf-8') as f:  # Specifică codificarea UTF-8
        f.write(f"{nume}\n{initiala_tatalui}\n{prenume}\n{cnp_total}\n{adresa}\n{email}\n")

    print(f"Imaginea {nume_fisier_nou} a fost mutată și redenumită în folderul {folder_localitate}")
    print(f"Fișierul text {fisier_txt} a fost creat.")

#main
for fisier in os.listdir(folder_input):
    if fisier.endswith(('.jpg', '.jpeg', '.png')):
        fisier_path = os.path.join(folder_input, fisier)
        proceseaza_fisier(fisier_path)
