# Proiect de Procesare a Formularelor 230

Acest proiect oferă o soluție eficientă pentru ONG-uri care doresc să extragă datele din formularele 230. Folosind tehnologia OCR (Optical Character Recognition), programul procesează imagini ale formularelor, extrage informațiile relevante și le salvează într-un format structurat. De asemenea, fișierele sunt organizate în foldere specifice, pe baza localităților, pentru o gestionare ușoară.

## Download
- [English version](https://apps.microsoft.com/detail/9n0198c2nvr1?hl=en-GB&gl=en)

- [Versiunea in română](https://apps.microsoft.com/detail/9n0198c2nvr1?hl=ro-RO&gl=RO)

- [Github Release](https://github.com/RaresAnghel08/OCR230/releases)

## Scopul Proiectului

Acest proiect ajută ONG-urile să automatizeze procesul de extragere a datelor din formularele 230, economisind timp și resurse. Prin utilizarea unui script Python bazat pe `easyocr`, datele sunt extrase și salvate într-un fișier text pentru fiecare persoană, iar fișierul imagine este mutat într-o structură de foldere organizată pe localități.


## Funcționalități
- **Extracție de text din imagini**: Folosește biblioteca `easyocr` pentru a recunoaște și extrage informațiile din diferite zone ale formularului.
- **Filtrarea datelor**: Se aplică filtre pentru a extrage doar datele relevante (de exemplu, numere, litere).
- **Organizarea fișierelor**: Imaginile procesate sunt mutate într-un folder specific localității, iar fișierele text sunt salvate în același folder.
- **Validarea CNP**: Verificare automată a CNP-urilor conform algoritmului oficial românesc.
- **Detectarea duplicatelor**: Identificarea automată a CNP-urilor duplicate cu raportare detaliată.
- **Export CSV**: Generare automată de fișiere CSV pentru compatibilitate cu alte sisteme.
- **Rapoarte PDF**: Creare automată de rapoarte PDF cu statistici și grafice interactive.
- **Raport de validare**: Fereastră de rapoarte cu statistici în timp real după procesare.
- **Deschidere automată**: Fișierele Excel, PDF și folderul de ieșire se deschid automat la finalizare.
- **Notificări prin e-mail**: Notificări automate prin e-mail cu atașamente la raport.
- **Tablou de bord live**: Statistici în timp real și urmărirea progresului în timpul procesării.
- **Funcții de căutare și inteligență artificială**: Capacități avansate de căutare cu suport AI/ML pentru validarea și corectarea datelor. - **Funcții avansate**: Include căutare avansată, gestionarea duplicatelor și funcționalități AI/ML pentru validarea și corectarea datelor.
- **Funcție de trimitere automată a rapoartelor prin e-mail**: Aplicația trimite rapoarte PDF/Excel/CSV direct de la `ocr230@gmail.com` folosind o parolă de aplicație Gmail. Utilizatorul introduce doar adresa destinatarului.
- **Configurarea Gmail**: Trebuie să utilizați o parolă de aplicație generată în Contul dvs. Google (Securitate > Parole de aplicație). Parola directă nu funcționează dacă este activată verificarea în doi pași. Dacă primiți mesajul `535 Nume de utilizator și parolă neacceptate`, verificați parola aplicației sau consultați [Ajutor Google](https://support.google.com/mail/?p=BadCredentials).

## Modele OCR utilizate

Aplicația OCR230 integrează două modele OCR principale pentru a asigura o recunoaștere cât mai precisă a datelor:

- **EasyOCR**  
  Este un model OCR open-source popular, cunoscut pentru ușurința de integrare și suportul pentru multiple limbi. Acesta este folosit în mod implicit pentru extragerea textului din imagini.

- **EfficientOCR (model dezvoltat la Harvard)**  
  Un model performant dezvoltat în cadrul Universității Harvard, care oferă o acuratețe superioară, în special pentru documente formale și cu tipar variat. EfficientOCR este utilizat în paralel sau complementar cu EasyOCR pentru a crește calitatea extragerii datelor, în special în cazurile în care imaginile sunt mai dificil de procesat.

## Instalare

1. Clonează acest repository:
   ```bash
   git clone https://github.com/F230-OCR/OCR230_infoeducatie.git

2. Rulează comanda
   ```bash
   pip install -r requirements.txt

4. Copiaza toate pozele cu formularele in folderul fisiere

5. Rulează scriptul principal main.py

---


# Form 230 Processing Project
This project provides an efficient solution for NGOs that wish to extract data from Form 230. Using OCR (Optical Character Recognition) technology, the program processes images of the forms, extracts relevant information, and saves it in a structured format. Additionally, the files are organized into specific folders based on localities for easy management.

## Project Purpose

This project helps NGOs automate the process of extracting data from Form 230, saving time and resources. Using a Python script based on `easyocr`, the data is extracted and saved in a text file for each individual, and the image file is moved into a folder structure organized by locality.

- **Data filtering**: Filters are applied to extract only relevant data (e.g., numbers, letters).
- **File organization**: Processed images are moved to a folder specific to the locality, and text files are saved in the same folder.
- **CNP validation**: Automatic verification of CNPs according to the official Romanian algorithm.
- **Duplicate detection**: Automatic identification of duplicate CNPs with detailed reporting.
- **CSV export**: Automatic generation of CSV files for compatibility with other systems.
- **PDF reports**: Automatic creation of PDF reports with interactive statistics and charts.
- **Validation report**: Reports window with real-time statistics after processing.
- **Automatic opening**: Excel, PDF and output folder open automatically upon completion.
- **Email notifications**: Automatic email notifications with report attachments.
- **Live Dashboard**: Real-time statistics and progress tracking during processing.
- **Search & AI Features**: Advanced search capabilities with AI/ML support for data validation and correction.
- **Advanced Features**: Includes advanced search, duplicate management, and AI/ML functionalities for data validation and correction.
- **Automatic report emailing feature**: The app sends PDF/Excel/CSV reports directly from `ocr230@gmail.com` using a Gmail App Password. The user only enters the recipient's address.
- **Gmail setup**: You must use an App Password generated in your Google Account (Security > App passwords). Direct password does not work if 2-Step Verification is enabled. If you get `535 Username and Password not accepted`, check your App Password or see [Google Help](https://support.google.com/mail/?p=BadCredentials).


## OCR Models Used

The OCR230 application integrates two main OCR models to ensure the most accurate data recognition:

- **EasyOCR** ​​
It is a popular open-source OCR model, known for its ease of integration and support for multiple languages. It is used by default for text extraction from images.

- **EfficientOCR (Harvard model)**
A high-performance model developed at Harvard University, which offers superior accuracy, especially for formal documents and documents with varied fonts. EfficientOCR is used in parallel or complementary to EasyOCR to increase the quality of data extraction, especially in cases where images are more difficult to process.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/F230-OCR/OCR230_infoeducatie.git

2. Run the command 
   ```bash
    pip install -r requirements.txt

3. Copy all the form images to the fisiere folder.

4. Run the main script main.py.
