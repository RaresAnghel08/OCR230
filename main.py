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
        zona_decupata = zona_decupata.resize((zona_decupata.width * 3, zona_decupata.height * 3))  # Mărire imagine
    else:
        zona_decupata = zona_decupata.resize((zona_decupata.width * 3, zona_decupata.height * 3))  # Mărire imagine
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

    # Parcurgem coordonatele și procesăm fiecare zonă
    for idx, coord in enumerate(coordonate):
        try:
            text = proceseaza_zona(coord, idx, image)
            if idx == 0:  # Prenume (zona 1)
                prenume = capitalize_words(filtru_nume(text))  # Capitalizăm fiecare cuvânt
            elif idx == 1:  # Nume (zona 2)
                nume = capitalize_words(filtru_nume(text))  # Capitalizăm fiecare cuvânt
            elif idx == 2:  # Inițiala tatălui (zona 3)
                initiala_tatalui = filtru_litere(text)
            elif idx == 3:  # Strada (zona 4)
                strada = text.capitalize()  # Transformăm prima literă în mare
            elif idx == 4:  # Număr (zona 5)
                numar = text.lstrip('0')  # Îndepărtăm zero-ul dacă este la început
            elif idx == 8:  # Localitate (zona 9)
                localitate = filtru_litere(text)
            elif idx == 7:  # Județ (zona 8)
                judet = filtru_litere(text)
            elif idx == 10:  # Bloc (zona 11)
                bloc = text.upper() if text else ""
            elif idx == 11:  # Scara (zona 12)
                scara = text.upper() if text else ""
            elif idx == 12:  # Etaj (zona 13)
                etaj = filtru_cifre(text) if text else ""
            elif idx == 13:  # Apartament (zona 14)
                apartament = filtru_cifre(text) if text else ""
            elif idx == 9:  # Cod postal (zona 10)
                cp = filtru_cifre(text) if text else ""
            elif idx == 5:  # CNP (zona 6)
                cnp_total += filtru_cifre(text)
            elif idx == 6:  # Email (zona 7)
                email = text.strip()

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

    #nume fisier nou
    nume_fisier = os.path.basename(image_path)
    nume_fisier_fara_extensie = os.path.splitext(nume_fisier)[0]
    nume_fisier_nou = f"{nume} {prenume}.jpg"

    #create folder for localitate if not exists
    folder_localitate = os.path.join(folder_output, localitate.capitalize())  #capitalize
    if not os.path.exists(folder_localitate):
        os.makedirs(folder_localitate)

    # move and rename image file
    noua_cale_imagine = os.path.join(folder_localitate, nume_fisier_nou)
    shutil.move(image_path, noua_cale_imagine)

    #create txt file with data from image
    fisier_txt = os.path.join(folder_localitate, f"{nume} {prenume}.txt")
    with open(fisier_txt, 'w') as f:
        f.write(f"{nume}\n{initiala_tatalui}\n{prenume}\n{cnp_total}\n{adresa}\n{email}\n")

    print(f"Imaginea {nume_fisier_nou} a fost mutată și redenumită în folderul {folder_localitate}")
    print(f"Fișierul text {fisier_txt} a fost creat.")

#main
for fisier in os.listdir(folder_input):
    if fisier.endswith(('.jpg', '.jpeg', '.png')):
        fisier_path = os.path.join(folder_input, fisier)
        proceseaza_fisier(fisier_path)
