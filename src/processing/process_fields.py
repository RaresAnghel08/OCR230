from src.processing.filtre import capitalize_words, filtru_nume, filtru_litere, filtru_cifre,replace_diacritics

def cautare_anaf(localitate):
    lower_localitate = localitate.lower()
    
    from src.anaf.alba import alba
    from src.anaf.bucuresti import bucuresti
    from src.anaf.cluj import cluj
    from src.anaf.craiova import craiova
    from src.anaf.galati import galati
    from src.anaf.iasi import iasi
    from src.anaf.ploiesti import ploiesti
    from src.anaf.timisoara import timisoara

    anaf_data = [alba, bucuresti, cluj, craiova, galati, iasi, ploiesti, timisoara]

    for data in anaf_data:
        for judet, unitati in data.items():
            if isinstance(unitati, dict):  # Verifică dacă unitati este un dicționar
                for unitate, localitati in unitati.items():
                    if isinstance(localitati, list):  # Verifică dacă localitati este o listă
                        for loc in localitati:
                            if loc.lower() == lower_localitate:
                                return unitate, judet
    return "Unknown", "Unknown"

# Example usage:
# print(cautare_anaf("Bacău"))
def process_fields(text_initial, idx, debug_switch=False):
    # Inițializăm toate variabilele
    prenume = ""
    nume = ""
    initiala_tatalui = ""
    strada = ""
    numar = ""
    cnp_total = ""
    email = ""
    judet = ""
    localitate = ""
    cp = ""
    bloc = ""
    scara = ""
    etaj = ""
    apartament = ""
    phone = ""
    doiani = ""
    folder_localitate = ""
    folder_localitate_mic = ""
    folder_localitate_mare = ""
    def debug_afisare(idx, nume_camp, text_initial, text_filtrat):
        print(f"Zona {idx + 1}: {nume_camp}")
        print(f"Text inițial: {text_initial}")
        print(f"Text filtrat: {text_filtrat}")
        print("*" * 50)
    
    try:
        if idx == 0:  # Prenume (zona 1)
            text_filtrat = capitalize_words(filtru_nume(text_initial))
            prenume = text_filtrat
            if debug_switch:
                debug_afisare(idx, "Prenume", text_initial, text_filtrat)
        elif idx == 1:  # Nume (zona 2)
            text_filtrat = capitalize_words(filtru_nume(text_initial))
            nume = text_filtrat
            if debug_switch:
                debug_afisare(idx, "Nume", text_initial, text_filtrat)
        elif idx == 2:  # Inițiala tatălui (zona 3)
            text_filtrat = filtru_litere(text_initial)
            initiala_tatalui = text_filtrat
            if debug_switch:
                debug_afisare(idx, "Inițiala tatălui", text_initial, text_filtrat)
        elif idx == 3:  # Strada (zona 4)
            text_filtrat = text_initial.capitalize()
            strada = text_filtrat
            if debug_switch:
                debug_afisare(idx, "Strada", text_initial, text_filtrat)
        elif idx == 4:  # Număr (zona 5)
            text_filtrat = text_initial.lstrip('0')
            numar = text_filtrat
            if debug_switch:
                debug_afisare(idx, "Număr", text_initial, text_filtrat)
        elif idx == 5:  # CNP (zona 6)
            text_filtrat = filtru_cifre(text_initial)
            cnp_total = text_filtrat  # Inițializăm cnp_total
            if debug_switch:
                debug_afisare(idx, "CNP", text_initial, text_filtrat)
        elif idx == 6:  # Email (zona 7)
            text_filtrat = text_initial.replace(' ', '.')  # Înlocuiește spațiile cu puncte
            text_filtrat = text_filtrat.replace('..', '.')  # Înlocuiește punctele duble
            text_filtrat = text_filtrat.replace('com.', 'com')  # Înlocuiește "com." cu "com"
            if text_filtrat.find('.com') == -1:
                text_filtrat = text_filtrat.replace('com', '.com')  # Adaugă un punct înainte de "com"
            email = text_filtrat  # Actualizează variabila email
            if debug_switch:
                debug_afisare(idx, "Email", text_initial, text_filtrat)
        elif idx == 7:  # Județ (zona 8)
            text_filtrat = capitalize_words(text_initial)
            text_filtrat = replace_diacritics(text_filtrat)
            judet = text_filtrat
            if debug_switch:
                debug_afisare(idx, "Județ", text_initial, text_filtrat)
        elif idx == 8:  # Localitate (zona 9)
            text_initial = text_initial.replace('-', ' ')  # Înlocuiește cratimele cu spațiu
            text_initial = text_initial.replace(',', ' ')  # Înlocuiește virgulele cu spațiu
            text_filtrat = capitalize_words(text_initial)
            text_filtrat = replace_diacritics(text_filtrat)
            #strip text
            text_filtrat = text_filtrat.strip()
            localitate = text_filtrat
            folder_localitate_mic, folder_localitate_mare = cautare_anaf(localitate) # Caută localitatea în baza de date ANAF
            if folder_localitate_mic == "Unknown":
                folder_localitate = localitate
                #debug_afisare(idx, "Localitate", text_initial, text_filtrat)
                print(cautare_anaf(localitate))
                print(f"Localitatea {localitate} nu a fost găsită în baza de date ANAF")
            if folder_localitate_mic != "Unknown":
                folder_localitate = folder_localitate_mic
            if debug_switch:
                debug_afisare(idx, "Localitate", text_initial, text_filtrat)
        elif idx == 9:  # Cod postal (zona 10)
            text_filtrat = filtru_cifre(text_initial) if text_initial else ""
            cp = text_filtrat
            if debug_switch:
                debug_afisare(idx, "Cod postal", text_initial, text_filtrat)
        elif idx == 10:  # Bloc (zona 11)
            text_filtrat = text_initial.upper() if text_initial else ""
            bloc = text_filtrat
            if debug_switch:
                debug_afisare(idx, "Bloc", text_initial, text_filtrat)
        elif idx == 11:  # Scara (zona 12)
            text_filtrat = text_initial.upper() if text_initial else ""
            scara = text_filtrat
            if debug_switch:
                debug_afisare(idx, "Scara", text_initial, text_filtrat)
        elif idx == 12:  # Etaj (zona 13)
            text_filtrat = filtru_cifre(text_initial) if text_initial else ""
            etaj = text_filtrat
            if debug_switch:
                debug_afisare(idx, "Etaj", text_initial, text_filtrat)
        elif idx == 13:  # Apartament (zona 14)
            text_filtrat = text_initial
            apartament = text_filtrat
            if debug_switch:
                debug_afisare(idx, "Apartament", text_initial, text_filtrat)
        elif idx == 14:  # Telefon (zona 15)
            text_filtrat = filtru_cifre(text_initial)
            phone = text_filtrat
            if debug_switch:
                debug_afisare(idx, "Telefon", text_initial, text_filtrat)
        elif idx == 15:  # 2 ani (zona 16)
            if text_initial != "":
                doiani = "Da"
            else:
                doiani = "Nu"
            if debug_switch:
                debug_afisare(idx, "2 ani", text_initial, doiani)
    except Exception as e:
        print(f"Eroare la procesarea zonei {idx + 1}: {e}")
    
    return prenume, nume, initiala_tatalui, strada, numar, cnp_total, email, judet, localitate, cp, bloc, scara, etaj, apartament, phone, doiani, folder_localitate
