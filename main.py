from imports import *

# Creează un obiect EasyOCR Reader cu GPU activat
reader = easyocr.Reader(['en', 'ro'], gpu=False)

#main
for fisier in os.listdir(folder_input):
    if fisier.endswith(('.jpg', '.jpeg', '.png')):
        fisier_path = os.path.join(folder_input, fisier)
        proceseaza_fisier(fisier_path)
