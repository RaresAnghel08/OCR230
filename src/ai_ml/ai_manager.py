"""
AI/ML Manager pentru Îmbunătățiri Automate - OCR230
Implementează funcționalități de auto-correct, predictive text și learning
"""

import os
import re
import json
import pickle
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import sqlite3
from pathlib import Path

# ML și NLP
try:
    import spacy
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import textdistance
    from fuzzywuzzy import fuzz, process
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("⚠️ Dependențele AI/ML nu sunt instalate. Rulați: pip install -r requirements.txt")

class AIMLManager:
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        self.db_path = os.path.join(output_folder, "ai_learning.db")
        self.models_path = os.path.join(output_folder, "ai_models")
        os.makedirs(self.models_path, exist_ok=True)
        
        # Fișiere pentru persistența datelor
        self.corrections_file = os.path.join(self.models_path, "corrections_database.json")
        self.patterns_file = os.path.join(self.models_path, "learned_patterns.json")
        self.anomalies_file = os.path.join(self.models_path, "anomaly_patterns.json")
        
        self.init_database()
        self.load_romanian_names()
        self.load_learned_patterns()
        
        if DEPENDENCIES_AVAILABLE:
            self.init_nlp_models()
    
    def init_database(self):
        """Inițializează baza de date pentru AI/ML"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel pentru corecții manuale (learning)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manual_corrections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_text TEXT,
                corrected_text TEXT,
                field_type TEXT,
                confidence_score REAL,
                date_added TEXT,
                user_validated BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Tabel pentru pattern-uri învățate
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_regex TEXT,
                confidence REAL,
                success_rate REAL,
                usage_count INTEGER DEFAULT 0,
                date_created TEXT
            )
        ''')
        
        # Tabel pentru anomalii detectate
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detected_anomalies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_type TEXT,
                original_value TEXT,
                anomaly_type TEXT,
                confidence REAL,
                suggested_correction TEXT,
                date_detected TEXT,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_nlp_models(self):
        """Inițializează modelele NLP"""
        if not DEPENDENCIES_AVAILABLE:
            return
        
        try:
            # Încarcă modelul românesc de spaCy (dacă e disponibil)
            try:
                self.nlp = spacy.load("ro_core_news_sm")
            except OSError:
                print("⚠️ Modelul românesc spaCy nu este instalat. Se folosește modelul englezesc...")
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                except OSError:
                    print("⚠️ Niciun model spaCy disponibil. Se dezactivează NLP.")
                    self.nlp = None
            
            # Inițializează vectorizatorul TF-IDF
            self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            
        except Exception as e:
            print(f"Eroare la inițializarea NLP: {e}")
            self.nlp = None
    
    def load_romanian_names(self):
        """Încarcă bazele de date cu nume românești pentru validare"""
        # Baze de date cu nume românești comune
        self.romanian_first_names = {
            'masculin': [
                'Adrian', 'Alexandru', 'Andrei', 'Bogdan', 'Cristian', 'Daniel', 'David',
                'Florin', 'Gabriel', 'George', 'Ion', 'Marius', 'Mihai', 'Nicolae',
                'Paul', 'Radu', 'Sebastian', 'Stefan', 'Valentin', 'Victor'
            ],
            'feminin': [
                'Adriana', 'Alexandra', 'Andreea', 'Ana', 'Cristina', 'Daniela',
                'Elena', 'Florina', 'Gabriela', 'Ioana', 'Maria', 'Mihaela',
                'Monica', 'Nicoleta', 'Paula', 'Simona', 'Valentina'
            ]
        }
        
        self.romanian_last_names = [
            'Popescu', 'Ionescu', 'Popa', 'Radu', 'Stoica', 'Stan', 'Dinu',
            'Gheorghe', 'Marin', 'Tudor', 'Florea', 'Constantin', 'Toma',
            'Mocanu', 'Barbu', 'Nistor', 'Cristea', 'Preda', 'Matei'
        ]
        
        # Pattern-uri pentru detecția erorilor OCR comune
        self.common_ocr_errors = {
            'letters': {
                '0': 'O', '1': 'I', '5': 'S', '8': 'B',
                'rn': 'm', 'cl': 'd', 'vv': 'w', 'nn': 'n'
            },
            'romanian_specific': {
                'ă': ['a', '8'], 'â': ['a', '^'], 'î': ['i', '1'],
                'ș': ['s'], 'ț': ['t'], 'ş': ['s'], 'ţ': ['t']
            }
        }
    
    def load_learned_patterns(self):
        """Încarcă pattern-urile învățate anterior"""
        self.learned_patterns = {}
        
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    self.learned_patterns = json.load(f)
            except Exception as e:
                print(f"Eroare la încărcarea pattern-urilor: {e}")
                self.learned_patterns = {}
    
    def auto_correct_ocr_errors(self, text: str, field_type: str) -> Tuple[str, float]:
        """
        Auto-correct pentru erorile OCR folosind ML și pattern matching
        
        Args:
            text: textul original din OCR
            field_type: tipul câmpului (nume, prenume, cnp, etc.)
            
        Returns:
            Tuple[str, float]: (text corectat, confidence score)
        """
        if not text or not text.strip():
            return text, 0.0
        
        original_text = text.strip()
        corrected_text = original_text
        confidence = 1.0
        
        # 1. Corecții de bază pentru erorile OCR comune
        corrected_text = self._apply_basic_ocr_corrections(corrected_text)
        
        # 2. Corecții specifice pe tip de câmp
        if field_type in ['nume', 'prenume']:
            corrected_text, conf = self._correct_name_field(corrected_text, field_type)
            confidence *= conf
        elif field_type == 'cnp':
            corrected_text, conf = self._correct_cnp_field(corrected_text)
            confidence *= conf
        elif field_type == 'email':
            corrected_text, conf = self._correct_email_field(corrected_text)
            confidence *= conf
        elif field_type == 'telefon':
            corrected_text, conf = self._correct_phone_field(corrected_text)
            confidence *= conf
        
        # 3. Verifică în baza de date cu corecții învățate
        learned_correction = self._check_learned_corrections(original_text, field_type)
        if learned_correction:
            corrected_text = learned_correction['corrected_text']
            confidence = learned_correction['confidence_score']
        
        # 4. Salvează corecția pentru învățare viitoare (dacă e semnificativă)
        if corrected_text != original_text and confidence > 0.7:
            self._save_correction_for_learning(original_text, corrected_text, field_type, confidence)
        
        return corrected_text, confidence
    
    def _apply_basic_ocr_corrections(self, text: str) -> str:
        """Aplică corecții de bază pentru erorile OCR"""
        corrected = text
        
        # Corecții simple letter-by-letter
        for wrong, correct in self.common_ocr_errors['letters'].items():
            corrected = corrected.replace(wrong, correct)
        
        # Corecții pentru caractere românești
        for correct_char, wrong_variants in self.common_ocr_errors['romanian_specific'].items():
            for wrong in wrong_variants:
                corrected = corrected.replace(wrong, correct_char)
        
        return corrected
    
    def _correct_name_field(self, text: str, field_type: str) -> Tuple[str, float]:
        """Corectează câmpurile de nume folosind baza de date românească"""
        if not DEPENDENCIES_AVAILABLE:
            return text, 1.0
        
        # Normalizează textul
        normalized = re.sub(r'[^a-zA-ZăâîșțĂÂÎȘȚ\s]', '', text).strip()
        
        if not normalized:
            return text, 0.5
        
        # Determină lista de nume de verificat
        name_list = []
        if field_type == 'nume':
            name_list = self.romanian_last_names
        else:  # prenume
            name_list = self.romanian_first_names['masculin'] + self.romanian_first_names['feminin']
        
        # Caută cea mai bună potrivire
        best_match = process.extractOne(normalized, name_list, scorer=fuzz.ratio)
        
        if best_match and best_match[1] > 70:  # Confidence > 70%
            return best_match[0], best_match[1] / 100.0
        
        return text, 0.8
    
    def _correct_cnp_field(self, text: str) -> Tuple[str, float]:
        """Corectează câmpul CNP"""
        # Extrage doar cifrele
        digits_only = re.sub(r'[^0-9]', '', text)
        
        if len(digits_only) == 13:
            return digits_only, 0.95
        elif len(digits_only) == 12:
            # Încearcă să ghicească cifra lipsă (de obicei prima)
            if digits_only[0] in ['1', '2', '5', '6']:  # Cifre valide pentru primul digit CNP
                return digits_only, 0.85
        
        return text, 0.6
    
    def _correct_email_field(self, text: str) -> Tuple[str, float]:
        """Corectează câmpul email"""
        # Pattern pentru email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Corecții comune pentru email
        corrected = text.lower().strip()
        corrected = corrected.replace(' ', '')
        corrected = corrected.replace('gmail.com', 'gmail.com')
        corrected = corrected.replace('yahoo.com', 'yahoo.com')
        
        if re.match(email_pattern, corrected):
            return corrected, 0.9
        
        return text, 0.5
    
    def _correct_phone_field(self, text: str) -> Tuple[str, float]:
        """Corectează câmpul telefon"""
        # Extrage doar cifrele
        digits_only = re.sub(r'[^0-9]', '', text)
        
        # Verifică formatele românești
        if len(digits_only) == 10 and digits_only.startswith('07'):
            return digits_only, 0.95
        elif len(digits_only) == 9 and digits_only.startswith('7'):
            return '0' + digits_only, 0.9
        
        return text, 0.6
    
    def _check_learned_corrections(self, text: str, field_type: str) -> Optional[Dict]:
        """Verifică în baza de date cu corecții învățate"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT corrected_text, confidence_score FROM manual_corrections
            WHERE original_text = ? AND field_type = ? AND user_validated = TRUE
            ORDER BY confidence_score DESC LIMIT 1
        ''', (text, field_type))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'corrected_text': result[0],
                'confidence_score': result[1]
            }
        
        return None
    
    def _save_correction_for_learning(self, original: str, corrected: str, field_type: str, confidence: float):
        """Salvează corecția pentru învățare viitoare"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO manual_corrections
            (original_text, corrected_text, field_type, confidence_score, date_added)
            VALUES (?, ?, ?, ?, ?)
        ''', (original, corrected, field_type, confidence, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def predictive_text_completion(self, partial_text: str, field_type: str) -> List[Dict]:
        """
        Predictive text pentru câmpuri incomplete
        
        Returns:
            List[Dict]: [{'text': str, 'confidence': float, 'source': str}]
        """
        suggestions = []
        
        if not partial_text or len(partial_text) < 2:
            return suggestions
        
        partial_lower = partial_text.lower()
        
        # Sugestii pe baza tipului de câmp
        if field_type in ['nume', 'prenume']:
            suggestions.extend(self._get_name_suggestions(partial_text, field_type))
        elif field_type == 'localitate':
            suggestions.extend(self._get_locality_suggestions(partial_text))
        elif field_type == 'judet':
            suggestions.extend(self._get_county_suggestions(partial_text))
        
        # Sugestii din pattern-urile învățate
        learned_suggestions = self._get_learned_suggestions(partial_text, field_type)
        suggestions.extend(learned_suggestions)
        
        # Sortează după confidence și returnează top 5
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:5]
    
    def _get_name_suggestions(self, partial: str, field_type: str) -> List[Dict]:
        """Sugestii pentru nume"""
        suggestions = []
        partial_lower = partial.lower()
        
        name_list = []
        if field_type == 'nume':
            name_list = self.romanian_last_names
        else:
            name_list = self.romanian_first_names['masculin'] + self.romanian_first_names['feminin']
        
        for name in name_list:
            if name.lower().startswith(partial_lower):
                confidence = 0.9 - (len(name) - len(partial)) * 0.1
                suggestions.append({
                    'text': name,
                    'confidence': max(confidence, 0.5),
                    'source': 'romanian_names_db'
                })
        
        return suggestions
    
    def _get_locality_suggestions(self, partial: str) -> List[Dict]:
        """Sugestii pentru localități (implementare de bază)"""
        # În practică aici ai încărca o bază de date cu localități românești
        common_localities = [
            'București', 'Cluj-Napoca', 'Timișoara', 'Iași', 'Constanța',
            'Craiova', 'Brașov', 'Galați', 'Ploiești', 'Oradea'
        ]
        
        suggestions = []
        partial_lower = partial.lower()
        
        for locality in common_localities:
            if locality.lower().startswith(partial_lower):
                suggestions.append({
                    'text': locality,
                    'confidence': 0.8,
                    'source': 'localities_db'
                })
        
        return suggestions
    
    def _get_county_suggestions(self, partial: str) -> List[Dict]:
        """Sugestii pentru județe"""
        counties = [
            'Alba', 'Arad', 'Argeș', 'Bacău', 'Bihor', 'Bistrița-Năsăud',
            'Botoșani', 'Brașov', 'Brăila', 'Buzău', 'Caraș-Severin',
            'Călărași', 'Cluj', 'Constanța', 'Covasna', 'Dâmbovița',
            'Dolj', 'Galați', 'Giurgiu', 'Gorj', 'Harghita', 'Hunedoara',
            'Ialomița', 'Iași', 'Ilfov', 'Maramureș', 'Mehedinți', 'Mureș',
            'Neamț', 'Olt', 'Prahova', 'Satu Mare', 'Sălaj', 'Sibiu',
            'Suceava', 'Teleorman', 'Timiș', 'Tulcea', 'Vaslui', 'Vâlcea',
            'Vrancea', 'București'
        ]
        
        suggestions = []
        partial_lower = partial.lower()
        
        for county in counties:
            if county.lower().startswith(partial_lower):
                suggestions.append({
                    'text': county,
                    'confidence': 0.9,
                    'source': 'counties_db'
                })
        
        return suggestions
    
    def _get_learned_suggestions(self, partial: str, field_type: str) -> List[Dict]:
        """Sugestii din pattern-urile învățate"""
        suggestions = []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT corrected_text, AVG(confidence_score) as avg_confidence
            FROM manual_corrections
            WHERE field_type = ? AND corrected_text LIKE ? AND user_validated = TRUE
            GROUP BY corrected_text
            ORDER BY avg_confidence DESC LIMIT 3
        ''', (field_type, f"{partial}%"))
        
        results = cursor.fetchall()
        conn.close()
        
        for text, confidence in results:
            suggestions.append({
                'text': text,
                'confidence': confidence,
                'source': 'learned_patterns'
            })
        
        return suggestions
    
    def detect_anomalies(self, data: Dict, field_type: str) -> List[Dict]:
        """
        Detectează anomalii în date (CNP suspecte, adrese inexistente etc.)
        
        Returns:
            List[Dict]: [{'anomaly_type': str, 'confidence': float, 'suggestion': str}]
        """
        anomalies = []
        
        if field_type == 'cnp':
            anomalies.extend(self._detect_cnp_anomalies(data.get('cnp', '')))
        elif field_type == 'adresa':
            anomalies.extend(self._detect_address_anomalies(data))
        elif field_type == 'telefon':
            anomalies.extend(self._detect_phone_anomalies(data.get('telefon', '')))
        elif field_type == 'email':
            anomalies.extend(self._detect_email_anomalies(data.get('email', '')))
        
        return anomalies
    
    def _detect_cnp_anomalies(self, cnp: str) -> List[Dict]:
        """Detectează anomalii în CNP"""
        anomalies = []
        
        if not cnp or len(cnp) != 13:
            return anomalies
        
        # Verifică prima cifră (secolul și sexul)
        first_digit = cnp[0]
        if first_digit not in ['1', '2', '5', '6']:
            anomalies.append({
                'anomaly_type': 'invalid_century_sex',
                'confidence': 0.9,
                'suggestion': f'Prima cifră trebuie să fie 1, 2, 5 sau 6, nu {first_digit}'
            })
        
        # Verifică luna
        month = cnp[3:5]
        if not (1 <= int(month) <= 12):
            anomalies.append({
                'anomaly_type': 'invalid_month',
                'confidence': 0.95,
                'suggestion': f'Luna {month} nu este validă'
            })
        
        # Verifică ziua
        day = cnp[5:7]
        if not (1 <= int(day) <= 31):
            anomalies.append({
                'anomaly_type': 'invalid_day',
                'confidence': 0.95,
                'suggestion': f'Ziua {day} nu este validă'
            })
        
        return anomalies
    
    def _detect_address_anomalies(self, data: Dict) -> List[Dict]:
        """Detectează anomalii în adresă"""
        anomalies = []
        
        # Verifică dacă județul și localitatea se potrivesc
        judet = data.get('judet', '').strip()
        localitate = data.get('localitate', '').strip()
        
        if judet and localitate:
            # Aici ai implementa logica de verificare județ-localitate
            # Pentru demonstrație, o verificare simplă
            if judet.lower() == 'bucuresti' and localitate.lower() not in ['bucuresti', 'sector']:
                anomalies.append({
                    'anomaly_type': 'county_locality_mismatch',
                    'confidence': 0.8,
                    'suggestion': f'Localitatea {localitate} nu se potrivește cu județul {judet}'
                })
        
        return anomalies
    
    def _detect_phone_anomalies(self, phone: str) -> List[Dict]:
        """Detectează anomalii în numărul de telefon"""
        anomalies = []
        
        if not phone:
            return anomalies
        
        digits_only = re.sub(r'[^0-9]', '', phone)
        
        if len(digits_only) < 10:
            anomalies.append({
                'anomaly_type': 'phone_too_short',
                'confidence': 0.9,
                'suggestion': 'Numărul de telefon pare incomplet'
            })
        elif not digits_only.startswith('07') and not digits_only.startswith('02') and not digits_only.startswith('03'):
            anomalies.append({
                'anomaly_type': 'invalid_phone_prefix',
                'confidence': 0.8,
                'suggestion': 'Prefixul telefonului nu pare valid pentru România'
            })
        
        return anomalies
    
    def _detect_email_anomalies(self, email: str) -> List[Dict]:
        """Detectează anomalii în email"""
        anomalies = []
        
        if not email:
            return anomalies
        
        # Verifică formatul de bază
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            anomalies.append({
                'anomaly_type': 'invalid_email_format',
                'confidence': 0.95,
                'suggestion': 'Formatul email-ului nu pare valid'
            })
        
        # Verifică domenii suspecte
        suspicious_domains = ['tempmail', 'throwaway', '10minute']
        domain = email.split('@')[-1] if '@' in email else ''
        
        if any(sus in domain.lower() for sus in suspicious_domains):
            anomalies.append({
                'anomaly_type': 'suspicious_email_domain',
                'confidence': 0.7,
                'suggestion': 'Domeniul email-ului pare temporar'
            })
        
        return anomalies
    
    def learn_from_feedback(self, original_value: str, corrected_value: str, field_type: str, user_confirmed: bool = True):
        """Învață din feedback-ul utilizatorului"""
        if user_confirmed and original_value != corrected_value:
            confidence = 0.95 if user_confirmed else 0.7
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO manual_corrections
                (original_text, corrected_text, field_type, confidence_score, date_added, user_validated)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (original_value, corrected_value, field_type, confidence, datetime.now().isoformat(), user_confirmed))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Învățat corecția: '{original_value}' → '{corrected_value}' pentru {field_type}")
    
    def get_learning_statistics(self) -> Dict:
        """Returnează statistici despre învățarea sistemului"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Numărul total de corecții învățate
        cursor.execute('SELECT COUNT(*) FROM manual_corrections WHERE user_validated = TRUE')
        total_corrections = cursor.fetchone()[0]
        
        # Corecții pe tip de câmp
        cursor.execute('''
            SELECT field_type, COUNT(*) FROM manual_corrections 
            WHERE user_validated = TRUE GROUP BY field_type
        ''')
        corrections_by_type = dict(cursor.fetchall())
        
        # Rata de încredere medie
        cursor.execute('SELECT AVG(confidence_score) FROM manual_corrections WHERE user_validated = TRUE')
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            'total_corrections': total_corrections,
            'corrections_by_type': corrections_by_type,
            'average_confidence': round(avg_confidence, 2),
            'learning_active': DEPENDENCIES_AVAILABLE
        }

# Test și utilizare
if __name__ == "__main__":
    ai_manager = AIMLManager("test_output")
    
    # Test auto-correct
    test_text = "I0n3scu"  # "Ionescu" cu erori OCR
    corrected, confidence = ai_manager.auto_correct_ocr_errors(test_text, "nume")
    print(f"Original: {test_text} → Corectat: {corrected} (Confidence: {confidence:.2f})")
    
    # Test predictive text
    suggestions = ai_manager.predictive_text_completion("Ion", "prenume")
    print(f"Sugestii pentru 'Ion': {suggestions}")
    
    # Test anomaly detection
    test_cnp = "8123456789012"  # CNP cu prima cifră invalidă
    anomalies = ai_manager.detect_anomalies({'cnp': test_cnp}, 'cnp')
    print(f"Anomalii CNP: {anomalies}")
    
    print("✅ AI/ML Manager testat cu succes!")
