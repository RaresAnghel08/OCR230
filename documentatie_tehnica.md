# 📄 Documentație Tehnică – OCR230

## ✅ Descriere generală

**OCR230** este o aplicație desktop care automatizează procesarea formularelor 230 (pentru redirecționarea a 3.5% din impozitul pe venit către ONG-uri). Folosește recunoaștere optică a caracterelor (OCR) pentru extragerea rapidă, precisă și sigură a datelor din PDF-uri sau imagini scanate.

Aplicația combină algoritmi avansați de OCR cu o interfață grafică intuitivă, oferind o soluție completă pentru organizațiile care procesează volume mari de formulare 230.

## 🏗️ Arhitectura aplicației

- **Backend & Procesare**: Python 3.13+
- **OCR Engine**: EasyOCR + EffOCR (model custom)
- **Interfață grafică**: Tkinter cu design modern
- **Export date**: Excel (openpyxl) + TXT
- **Structură modulară**:
  - `src/ocr/` – Recunoaștere text și inițializare engine-uri OCR
  - `src/processing/` – Extracție și validare date, coordonate OCR
  - `src/ui/` – Interfață grafică (main_window.py, splash.py)
  - `src/anaf/` – Module pentru validare județe și sectoare ANAF
  - `src/excel/` – Export incremental și gestionare fișiere Excel
  - `src/utils/`, `src/names/` – Funcții auxiliare și validare nume
  - `Assets/` – Resurse grafice și icoane

## 🧠 Funcționalități cheie

- ✅ Procesare automată a formularelor `.PDF`, `.JPG`, `.PNG`, `.JPEG`
- 🔍 Extragere inteligentă date: nume, inițiala tatălui, prenume, CNP, adresă, telefon, email
- 🏛️ Determinare automată ANAF pe baza adresei
- 📁 Organizare automată în foldere pe județe/sectoare
- 📊 Progress bar în timp real pentru feedback vizual
- 🔄 Suport pentru batch processing (formulare multiple)
- 📋 Export incremental în Excel cu formatare corectă (CNP, telefon ca text)
- ⏯️ Funcționalitate Start/Stop pentru control procesare
- 🚫 Gestionare duplicate în Excel
- ⚡ Interfață intuitivă cu buton pentru accelerație grafică GPU/CPU
- 🎨 Splash screen cu animație de încărcare
- 📂 Deschidere automată folder rezultate și Excel la finalizare

## 📈 Performanță

- **Viteză procesare**: ~5-8 sec / formular (CPU) | ~3-5 sec (GPU)
- **Spațiu ocupat**: ~900 MB (incluzând modelele OCR)
- **Consum memorie**: ~500-800 MB RAM în timpul procesării
- **Threading**: pentru procesare non-blocking a interfeței
- **Optimizări**: pentru procesare batch (formulare multiple)
- **Cache**: inteligent pentru reader-uri OCR

## 🔧 Detalii tehnice

### 📊 Structura codului (2,672 linii Python):
- **UI & UX**: 446 linii (17%) - Interfață și experiență utilizator
- **Excel & Export**: 474 linii (18%) - Gestionare export date
- **OCR & Processing**: 673 linii (25%) - Logica principală de procesare
- **ANAF Modules**: 873 linii (33%) - Validare teritorială
- **Utilities**: 204 linii (7%) - Funcții auxiliare

### 📁 Algoritm procesare:
1. **Conversie PDF → PNG** (dacă e cazul) cu pdf2image
2. **Inițializare reader OCR** (EasyOCR/EffOCR)
3. **Extragere text** din zone predefinite (coordonate.py)
4. **Filtrare și curățare text** (filtre.py)
5. **Separare câmpuri individuale** (process_fields.py)
6. **Validare și determinare ANAF** (anaf/*.py)
7. **Creare structură foldere**
8. **Export TXT + adăugare incrementală în Excel**
9. **Actualizare progress bar**

### 💾 Format fișiere output:
- **TXT**: `nume\ninitiala_tatalui\nprenume\ncnp\nadresa\ntelefon\nemail\n2_ani`
- **Excel**: Coloane ordonate cu formatare text pentru CNP și telefon
- **Structură foldere**: `output/ANAF_REGION/persoane/`

## 🔒 Securitate

- 🏠 **Rulare 100% locală**, fără conexiune la internet
- ✅ **Validare robustă** extensii fișiere și formate
- 🛡️ **Tratare comprehensivă erori** cu try/except pentru prevenirea crash-urilor
- 📝 **Fișiere corupte** sau nevalide sunt ignorate automat cu logging
- 🔐 **Respectarea principiilor GDPR** – nicio transmitere externă a datelor
- 🔍 **Verificare integritate date** înainte de export
- 🚫 **Protecție împotriva overwrite** accidental în Excel

## 🧪 Testare

- **Funcțională**: testare cu sute de formulare reale, diverse scenarii
- **Non-funcțională**: testare pe mai multe sisteme Windows (10, 11)
- **Feedback real**: 4 ONG-uri implicate, peste 3.000 formulare procesate
- **Testare performanță**: GPU vs CPU, formulare multiple
- **Securitate**: validare input + rezistență la fișiere greșite
- **Bug tracking**: prin GitHub Issues + TODO.md actualizat
- **Testare interfață**: toate butoanele și funcționalitățile

## 🔁 Versionare și dezvoltare

- **Git**: Sistem de control versiuni + repository public pe GitHub
- **Branch-uri**: separate pentru dezvoltare și versiuni stabile
- **Commit-uri**: frecvente cu descrieri detaliate
- **Issues tracking**: pentru bug-uri și îmbunătățiri
- **TODO.md**: pentru planificare dezvoltare
- **Documentație**: tehnică actualizată continuu

## 📦 Dependențe și resurse externe

- **Core OCR**: EasyOCR + EffOCR (modele pre-antrenate)
- **Procesare imagini**: pdf2image, numpy, Pillow (PIL)
- **Interface**: tkinter (built-in Python), threading pentru multitasking
- **Export date**: pandas, openpyxl pentru Excel
- **Utilități**: scipy pentru optimizări numerice
- **Date ANAF**: Mapare județe și sectoare din surse oficiale anaf.ro

## 🔧 Configurare build

- **Tool**: auto-py-to-exe pentru dezvoltare și testare locală
- **Distribuție**: Microsoft Store pentru utilizatori finali
- **Configurații**: separate pentru laptop și PC (JSON pentru dezvoltare)
- **Include**: Assets, src, requirements.txt în build
- **Optimizare**: mărime aplicație pentru store
- **Customizare**: Icon personalizat și metadata aplicație pentru Microsoft Store

## 🛠️ Ghid instalare

### 📋 Versiunea dezvoltare (pentru programatori):
1. Asigură-te că ai **Python 3.10+** instalat
2. Clonează repository-ul: `git clone [repo-url]`
3. Navighează în folder: `cd OCR230_infoeducatie`
4. Instalează dependențele: `pip install -r requirements.txt`
5. Rulează aplicația: `python main.py`

### 💻 Versiunea compilată (pentru utilizatori finali):
1. Descarcă aplicația din **Microsoft Store**
2. Instalează **OCR230** din store
3. Deschide aplicația din meniul Start
4. Selectează folderele de intrare și ieșire
5. Apasă **Start** pentru a începe procesarea

### ⚙️ Configurare avansată:
- **Accelerație GPU**: bifează opțiunea din interfață pentru performanță sporită
- **Foldere de lucru**: selectează folderul cu formulare și folderul pentru rezultate
- **Funcția Start/Stop**: oprește procesarea în orice moment prin același buton

## 📍 Public țintă

- 🏢 **ONG-uri mici și mijlocii** din România
- 👥 **Voluntari** sau persoane fizice implicate în completarea formularului 230
- 💼 **Operatorii de birou** care doresc automatizarea procesului de digitalizare
- 🏛️ **Organizații** care procesează volume mari de formulare 230
- 📊 **Consultanți fiscali și contabili**

## 🎯 Beneficii cheie

- ⚡ **Reducerea timpului** de procesare cu 95% față de metoda manuală
- ✅ **Eliminarea erorilor umane** în transcrierea datelor
- 📁 **Organizare automată** și structurată a datelor
- 📊 **Export direct în Excel** pentru analize ulterioare
- 🔐 **Conformitate GDPR** prin procesare locală
- 👤 **Interface prietenoasă** pentru utilizatori non-tehnici

## 📈 Statistici proiect

- **Linii de cod**: 2,672 (Python)
- **Fișiere**: 20 module Python
- **Arhitectură**: Modulară și scalabilă
- **Testare**: 3,000+ formulare procesate
- **Performanță**: 95% reducere timp vs. manual
- **Securitate**: 100% procesare locală
- **Compatibilitate**: Windows 10/11

## 📄 Licență și utilizare

### Licența aplicației

**OCR230** este licențiat sub **MIT License** - o licență open-source permisivă care permite:

#### ✅ Permisiuni
- ✔️ **Utilizare comercială** - poate fi utilizat în medii comerciale
- ✔️ **Modificare** - codul poate fi modificat și adaptat
- ✔️ **Distribuire** - aplicația poate fi redistribuită
- ✔️ **Utilizare privată** - poate fi utilizat pentru proiecte private
- ✔️ **Sublicențiere** - poate fi sublicențiat

#### ⚠️ Condiții
- 📋 **Include licența** - licența și drepturile de autor trebuie incluse
- 📋 **Include notificarea de copyright** - trebuie păstrate informațiile despre autori

#### ❌ Limitări
- ❌ **Fără garanție** - software-ul este furnizat "as-is"
- ❌ **Fără responsabilitate** - autorii nu sunt responsabili pentru daune

### Termeni specifici pentru OCR230

#### 🔒 Confidențialitatea datelor
- Aplicația procesează **doar local** datele introduse
- **Nu se transmit** informații către servere externe
- Utilizatorul este responsabil pentru **securitatea datelor** procesate
- Se recomandă **ștergerea periodică** a fișierelor temporare

#### 🏛️ Conformitate legală
- Aplicația respectă **GDPR** prin procesarea exclusiv locală
- Utilizatorul trebuie să se asigure de **conformitatea** cu reglementările locale
- **Nu se colectează** date de utilizare sau telemetrie

#### 🔧 Modificări și contribuții
- Contribuțiile sunt **încurajate** și binevenite
- Modificările trebuie să **respecte arhitectura** existentă
- **Testarea** este obligatorie pentru orice modificare majoră

### Dependențe și licențe terțe

Aplicația utilizează următoarele biblioteci open-source:

#### 📚 Biblioteci Python
- **Tesseract OCR** - Apache License 2.0
- **OpenCV** - Apache License 2.0
- **Pandas** - BSD 3-Clause License
- **OpenPyXL** - MIT License
- **Tkinter** - Python Software Foundation License
- **Pillow (PIL)** - HPND License
- **NumPy** - BSD 3-Clause License

#### ⚖️ Notă asupra licențelor
Toate dependențele utilizate sunt compatibile cu licența MIT și permit utilizarea comercială.

### Contact și suport

#### 📧 Informații de contact
- **Proiect**: InfoEducație România
- **Aplicație**: OCR230 - Microsoft Store
- **Repository**: GitHub - OCR230_infoeducatie
- **Suport**: Issues pe GitHub
- **Email**: raresanghel2008@gmail.com

#### 🤝 Contribuții
Pentru contribuții, vă rugăm să:
1. Creați un **fork** al repository-ului
2. Implementați modificările într-o **branch separată**
3. Creați un **Pull Request** cu descriere detaliată
4. Asigurați-vă că **testele** trec cu succes

---

© 2025 InfoEducație România. Toate drepturile rezervate sub MIT License.

