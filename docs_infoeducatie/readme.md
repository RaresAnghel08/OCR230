# 🧪 Cum să testezi OCR230

Poți testa aplicația OCR230 în două moduri:

## 1. Descarcă din Microsoft Store
- Caută **F230-OCR**  în Microsoft Store sau intră pe [linkul de descărcare](https://apps.microsoft.com/detail/9pmm6w5qn2gv) și instalează aplicația.
- Deschide aplicația.

## 2. Rulează din sursă (pentru dezvoltatori)
- Clonează repository-ul de pe GitHub:
  ```
  git clone https://github.com/RaresAnghel08/OCR230.git
  cd OCR230_infoeducatie
  ```
- Instalează dependențele:
  ```
  pip install -r requirements.txt
  ```
- Rulează aplicația:
  ```
  python main.py
  ```

## 3. Testează cu date de exemplu
- Când ți se cere, selectează arhiva de la linkul de mai jos ca **folder de intrare** (extrage-o mai întâi dacă este zip/rar):

  **[Exemplu de input](https://drive.google.com/file/d/1nI1d_cY7AhxaeA4wava27F50RIcvGuM6/view?usp=drive_link)**

- Selectează **orice** folder de pe disc ca **folder de ieșire** (unde vor fi salvate rezultatele) sau **creează unul nou**.

- Apasă pe **Start** în aplicație și urmărește cum procesează automat toate formularele din folderul de intrare.

Gata! Aplicația va afișa progresul live și va genera rapoarte Excel, PDF și CSV în folderul de ieșire.

## 4. Cum arată rezultatele
- **Excel**: Vei avea un fișier Excel cu toate datele extrase, organizate pe coloane.
- **PDF**: Un raport PDF cu statistici relevante și grafice.
- **CSV**: Un fișier CSV cu datele extrase, util pentru analiză sau import în alte aplicații.
- **TXT**: Fiecare formular procesat va avea un fișier TXT generat cu datele extrase.

**[Exemplu de output](https://drive.google.com/file/d/1B3ceFqAjWMjCvj4Sajq2SyXw3xKQHZN4/view?usp=drive_link)**