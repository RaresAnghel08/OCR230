# 🧪 Cum să testezi OCR230

Poți testa aplicația OCR230 în două moduri:

## 1. Descarcă din Microsoft Store
- Caută **OCR230** în Microsoft Store și instalează aplicația.
- Deschide aplicația din meniul Start.

## 2. Rulează din sursă (pentru dezvoltatori)
- Clonează repository-ul de pe GitHub:
  ```
  git clone https://github.com/F230-OCR/OCR230_infoeducatie.git
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

  **[Input example](https://example.com/input.zip)**

- Selectează **orice** folder de pe disc ca **folder de ieșire** (unde vor fi salvate rezultatele) sau **creează unul nou**.

- Apasă pe **Start** în aplicație și urmărește cum procesează automat toate formularele din folderul de intrare.

Gata! Aplicația va afișa progresul live și va genera rapoarte Excel, PDF și CSV în folderul de ieșire.
