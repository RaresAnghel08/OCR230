import openai
import os
import sys
from filtre import capitalize_words
# from api_keys import openai_api_key
openai.api_key = "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"

# def corecteaza_adresa(adresa):
#     try:
#         # Pregătim promptul pentru corectare
#         prompt = f"Corectează și formatează această adresă într-un format standardizat:\n\n{adresa}\n\nReturnează doar adresa corectată, cu abrevierile STR. LOC. JUD. NR. SC. BL. ET. AP. ."

#         # Solicităm completarea de la OpenAI
#         response = openai.ChatCompletion.create(
#             model="gpt-4",  # Sau "gpt-3.5-turbo"
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant that formats addresses."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=200,
#             temperature=0.2
#         )

#         # Extragem adresa corectată
#         adresa_corectata = response['choices'][0]['message']['content'].strip()
#         return adresa_corectata

#     except Exception as e:
#         print(f"Eroare la corectarea adresei: {e}")
#         return adresa  # Returnăm adresa originală dacă apare o eroare


# import re

# def corecteaza_adresa(adresa):
#     # Elimină cuvintele și tot ce urmează după abrevieri până la următorul cuvânt relevant
#     pattern = r"\b(NR|Nr|nr|Ap|ap|BL|Bl|bl|SC|Sc|sc|ET|Et|et|CP|Cp|cp)\s*\.*\s*(\d*)\b"
    
#     # Înlocuiește abrevierile pentru a fi formate corect cu punct
#     adresa_fara_abrevieri = re.sub(pattern, lambda m: m.group(0).upper(), adresa)

#     # Elimină numerele și abrevierile repetate
#     adresa_curatata = ' '.join(sorted(set(adresa_fara_abrevieri.split()), key=adresa_fara_abrevieri.index))

#     # Asigură-te că adresa începe cu literă mare pentru fiecare cuvânt
#     return capitalize_words(adresa_curatata)
