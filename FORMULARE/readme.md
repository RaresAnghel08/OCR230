# Folderul FORMULARE

Acest folder conține fișierele și folderele generate în urma procesării formularelor 230. După ce ai rulat scriptul principal, fiecare formulă procesată va fi organizată și salvată în foldere corespunzătoare localităților. Fiecare localitate va avea propriul său folder, iar în interiorul acestora vor fi fișierele de imagine și fișierele text care conțin datele extrase.

## Structura Folderului
Localitate1
Localitate2
etc.


## Ce Conține Fiecare Folder

1. **Fișierele de imagine**: Imaginile procesate sunt redenumite conform numelui și prenumelui persoanei și sunt mutate în folderul corespunzător localității respective. Fișierele de imagine vor fi în format `.jpg`.

2. **Fișierele text**: Pentru fiecare formulă procesată, va fi generat un fișier text cu informațiile extrase, inclusiv:
   - Nume
   - Inițiala tatălui
   - Prenume
   - CNP
   - Adresă (strada, număr, localitate, județ, bloc, scară, etaj, apartament, cod poștal)
   - Email

Fișierele text vor fi salvate cu același nume ca și imaginea, dar cu extensia `.txt`.

## Exemplu de Fișier Text

Un fișier text generat poate arăta astfel:

Ionescu
M
Maria
1920304050607
Str. Exemplu nr. 10, Loc. București, Jud. Ilfov
maria.ionescu@example.com

## Organizarea și Utilizarea Fișierelor

- **Fișierele de imagine** sunt organizate în folderele corespunzătoare localităților (de exemplu, `București`, `Ilfov`, etc.), iar fiecare imagine este redenumită pentru a reflecta numele și prenumele persoanei.
- **Fișierele text** sunt plasate în aceleași foldere și conțin informațiile extrase din formulare.

Poți accesa aceste fișiere pentru a vizualiza datele extrase sau pentru a le utiliza în scopuri de procesare ulterioară.

## Note

- Asigură-te că folderele pentru fiecare localitate sunt create corect după procesarea formularelor.
- Dacă există erori în procesarea unui formular, fișierele nu vor fi generate pentru acea localitate, iar mesajele de eroare vor fi afișate în consolă.

---

# FORMULARE Folder

This folder contains the files and subfolders generated after processing the Form 230. After running the main script, each processed form will be organized and saved into subfolders corresponding to the localities. Each locality will have its own folder, and inside these folders, you will find the image files and text files containing the extracted data.

## Folder Structure
Locality1  
Locality2  
etc.

## What Each Folder Contains

1. **Image Files**: The processed images are renamed according to the person's first name and last name, and they are moved to the corresponding locality folder. The image files will be in `.jpg` format.

2. **Text Files**: For each processed form, a text file will be generated containing the extracted information, including:
   - Last Name
   - Father's Initial
   - First Name
   - CNP (Personal Identification Number)
   - Address (street, number, locality, county, block, stairwell, floor, apartment, postal code)
   - Email

Text files will be saved with the same name as the image, but with a `.txt` extension.

## Example of a Text File

A generated text file might look like this:

Ionescu
M
Maria
1920304050607
Str. Exemplu nr. 10, Loc. București, Jud. Ilfov
maria.ionescu@example.com


## File Organization and Usage

- **Image files** are organized into subfolders corresponding to the localities (e.g., `București`, `Ilfov`, etc.), and each image is renamed to reflect the person's first name and last name.
- **Text files** are placed in the same subfolders and contain the extracted information from the forms.

You can access these files to view the extracted data or use them for further processing.

## Notes

- Make sure that the subfolders for each locality are created correctly after processing the forms.
- If an error occurs during the processing of a form, no files will be generated for that locality, and error messages will be displayed in the console.
