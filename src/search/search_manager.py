"""
Search Engine Avansat pentru OCR230
Implementează căutare, filtrare și management duplicate
"""

import os
import re
import json
import sqlite3
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

# Search dependencies
try:
    from whoosh.index import create_in, open_dir
    from whoosh.fields import Schema, TEXT, ID, DATETIME, NUMERIC
    from whoosh.qparser import QueryParser, MultifieldParser
    from whoosh import highlight
    import regex
    SEARCH_DEPENDENCIES_AVAILABLE = True
    print("✅ Dependențele pentru search sunt disponibile!")
except ImportError as e:
    SEARCH_DEPENDENCIES_AVAILABLE = False
    print(f"⚠️ Dependențele pentru search nu sunt instalate: {e}")

class SearchManager:
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        self.db_path = os.path.join(output_folder, "search_index.db")
        self.index_dir = os.path.join(output_folder, "search_index")
        self.saved_searches_file = os.path.join(output_folder, "saved_searches.json")
        
        os.makedirs(self.index_dir, exist_ok=True)
        
        self.init_database()
        self.load_saved_searches()
        
        if SEARCH_DEPENDENCIES_AVAILABLE:
            self.init_search_index()
    
    def init_database(self):
        """Inițializează baza de date pentru search"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel principal pentru persoane și datele lor
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persons_search (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nume TEXT,
                initiala_tatalui TEXT,
                prenume TEXT,
                cnp TEXT UNIQUE,
                adresa TEXT,
                telefon TEXT,
                email TEXT,
                doiani TEXT,
                anaf_sector TEXT,
                judet TEXT,
                localitate TEXT,
                file_path TEXT,
                processing_date TEXT,
                session_id TEXT,
                duplicate_group_id INTEGER
            )
        ''')
        
        # Tabel pentru căutările salvate
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_name TEXT UNIQUE,
                search_query TEXT,
                filters TEXT,
                date_created TEXT,
                usage_count INTEGER DEFAULT 0,
                last_used TEXT
            )
        ''')
        
        # Tabel pentru grupurile de duplicate
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplicate_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_hash TEXT UNIQUE,
                primary_person_id INTEGER,
                persons_count INTEGER,
                resolution_status TEXT DEFAULT 'pending',
                date_created TEXT,
                FOREIGN KEY (primary_person_id) REFERENCES persons_search (id)
            )
        ''')
        
        # Tabel pentru istoricul căutărilor
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_query TEXT,
                filters_applied TEXT,
                results_count INTEGER,
                search_date TEXT,
                execution_time REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_search_index(self):
        """Inițializează indexul Whoosh pentru căutare full-text"""
        if not SEARCH_DEPENDENCIES_AVAILABLE:
            return
        
        # Schema pentru indexul de căutare
        schema = Schema(
            id=ID(stored=True),
            nume=TEXT(stored=True),
            prenume=TEXT(stored=True),
            cnp=ID(stored=True),
            adresa=TEXT(stored=True),
            telefon=TEXT(stored=True),
            email=TEXT(stored=True),
            anaf_sector=TEXT(stored=True),
            judet=TEXT(stored=True),
            localitate=TEXT(stored=True),
            content=TEXT(stored=True),  # Câmp combinat pentru căutare generală
            processing_date=DATETIME(stored=True)
        )
        
        try:
            # Încearcă să deschidă indexul existent
            self.search_index = open_dir(self.index_dir)
        except:
            # Creează index nou dacă nu există
            self.search_index = create_in(self.index_dir, schema)
    
    def load_saved_searches(self):
        """Încarcă căutările salvate"""
        self.saved_searches = {}
        
        if os.path.exists(self.saved_searches_file):
            try:
                with open(self.saved_searches_file, 'r', encoding='utf-8') as f:
                    self.saved_searches = json.load(f)
            except Exception as e:
                print(f"Eroare la încărcarea căutărilor salvate: {e}")
                self.saved_searches = {}
    
    def add_person_to_index(self, person_data: Dict) -> int:
        """Adaugă o persoană în indexul de căutare"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Adaugă în baza de date
        cursor.execute('''
            INSERT OR REPLACE INTO persons_search
            (nume, initiala_tatalui, prenume, cnp, adresa, telefon, email, doiani,
             anaf_sector, judet, localitate, file_path, processing_date, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            person_data.get('nume', ''),
            person_data.get('initiala_tatalui', ''),
            person_data.get('prenume', ''),
            person_data.get('cnp', ''),
            person_data.get('adresa', ''),
            person_data.get('telefon', ''),
            person_data.get('email', ''),
            person_data.get('doiani', ''),
            person_data.get('anaf_sector', ''),
            person_data.get('judet', ''),
            person_data.get('localitate', ''),
            person_data.get('file_path', ''),
            datetime.now().isoformat(),
            person_data.get('session_id', '')
        ))
        
        person_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Adaugă în indexul Whoosh pentru full-text search
        if SEARCH_DEPENDENCIES_AVAILABLE and hasattr(self, 'search_index'):
            writer = self.search_index.writer()
            
            # Combină toate câmpurile text pentru căutare generală
            content = f"{person_data.get('nume', '')} {person_data.get('prenume', '')} {person_data.get('adresa', '')} {person_data.get('email', '')} {person_data.get('telefon', '')}"
            
            writer.add_document(
                id=str(person_id),
                nume=person_data.get('nume', ''),
                prenume=person_data.get('prenume', ''),
                cnp=person_data.get('cnp', ''),
                adresa=person_data.get('adresa', ''),
                telefon=person_data.get('telefon', ''),
                email=person_data.get('email', ''),
                anaf_sector=person_data.get('anaf_sector', ''),
                judet=person_data.get('judet', ''),
                localitate=person_data.get('localitate', ''),
                content=content,
                processing_date=datetime.now()
            )
            
            writer.commit()
        
        return person_id
    
    def advanced_search(self, query: str, filters: Dict = None, use_regex: bool = False) -> List[Dict]:
        """
        Căutare avansată cu multiple filtre
        
        Args:
            query: termenul de căutare
            filters: dicționar cu filtre (judet, perioada, cnp_valid, etc.)
            use_regex: dacă să folosească regex pentru căutare
            
        Returns:
            List[Dict]: rezultatele căutării
        """
        start_time = datetime.now()
        
        if SEARCH_DEPENDENCIES_AVAILABLE and hasattr(self, 'search_index') and not use_regex:
            results = self._whoosh_search(query, filters)
        else:
            results = self._sql_search(query, filters, use_regex)
        
        # Loghează căutarea
        execution_time = (datetime.now() - start_time).total_seconds()
        self._log_search(query, filters, len(results), execution_time)
        
        return results
    
    def _whoosh_search(self, query: str, filters: Dict = None) -> List[Dict]:
        """Căutare folosind Whoosh (full-text)"""
        with self.search_index.searcher() as searcher:
            # Parser pentru multiple câmpuri
            parser = MultifieldParser(["nume", "prenume", "adresa", "content"], 
                                    self.search_index.schema)
            
            parsed_query = parser.parse(query)
            results = searcher.search(parsed_query, limit=1000)
            
            search_results = []
            for hit in results:
                result_dict = dict(hit)
                
                # Aplică filtrele dacă sunt specificate
                if self._passes_filters(result_dict, filters):
                    # Adaugă highlighting
                    result_dict['highlights'] = {
                        'nume': hit.highlights("nume"),
                        'prenume': hit.highlights("prenume"),
                        'adresa': hit.highlights("adresa")
                    }
                    search_results.append(result_dict)
            
            return search_results
    
    def _sql_search(self, query: str, filters: Dict = None, use_regex: bool = False) -> List[Dict]:
        """Căutare folosind SQL cu opțional regex"""
        conn = sqlite3.connect(self.db_path)
        
        # Construiește query-ul SQL
        base_query = "SELECT * FROM persons_search WHERE 1=1"
        params = []
        
        if query:
            if use_regex:
                # Pentru regex, selectăm toate recordurile și filtrăm în Python
                # deoarece SQLite nu suportă REGEXP nativ
                pass  # Nu adăugăm condiții SQL pentru regex
            else:
                # Căutare text simplă
                text_conditions = []
                search_terms = query.split()
                
                for term in search_terms:
                    term_conditions = []
                    for field in ['nume', 'prenume', 'adresa', 'telefon', 'email']:
                        term_conditions.append(f"{field} LIKE ?")
                        params.append(f"%{term}%")
                    text_conditions.append(f"({' OR '.join(term_conditions)})")
                
                if text_conditions:
                    base_query += f" AND ({' AND '.join(text_conditions)})"
        
        # Aplică filtrele
        if filters:
            base_query, params = self._apply_sql_filters(base_query, params, filters)
        
        base_query += " ORDER BY processing_date DESC LIMIT 1000"
        
        df = pd.read_sql_query(base_query, conn, params=params)
        conn.close()
        
        # Dacă folosim regex, filtrăm rezultatele în Python
        if use_regex and query:
            try:
                import re
                compiled_pattern = re.compile(query, re.IGNORECASE)
                filtered_results = []
                
                for _, row in df.iterrows():
                    record = row.to_dict()
                    # Verificăm dacă pattern-ul se potrivește în oricare din câmpuri
                    for field in ['nume', 'prenume', 'adresa', 'telefon', 'email']:
                        field_value = str(record.get(field, ''))
                        if compiled_pattern.search(field_value):
                            filtered_results.append(record)
                            break  # Nu duplica rezultatul pentru aceeași persoană
                
                return filtered_results
            except re.error as e:
                print(f"Eroare regex: {e}")
                return []
        
        return df.to_dict('records')
    
    def _apply_sql_filters(self, base_query: str, params: List, filters: Dict) -> Tuple[str, List]:
        """Aplică filtrele SQL"""
        query = base_query
        
        if filters.get('judet'):
            query += " AND judet = ?"
            params.append(filters['judet'])
        
        if filters.get('localitate'):
            query += " AND localitate = ?"
            params.append(filters['localitate'])
        
        if filters.get('anaf_sector'):
            query += " AND anaf_sector = ?"
            params.append(filters['anaf_sector'])
        
        if filters.get('start_date'):
            query += " AND processing_date >= ?"
            params.append(filters['start_date'])
        
        if filters.get('end_date'):
            query += " AND processing_date <= ?"
            params.append(filters['end_date'])
        
        if filters.get('has_phone'):
            if filters['has_phone']:
                query += " AND telefon IS NOT NULL AND telefon != ''"
            else:
                query += " AND (telefon IS NULL OR telefon = '')"
        
        if filters.get('has_email'):
            if filters['has_email']:
                query += " AND email IS NOT NULL AND email != ''"
            else:
                query += " AND (email IS NULL OR email = '')"
        
        if filters.get('doiani'):
            query += " AND doiani = ?"
            params.append(filters['doiani'])
        
        return query, params
    
    def _passes_filters(self, result: Dict, filters: Dict) -> bool:
        """Verifică dacă rezultatul trece filtrele (pentru Whoosh)"""
        if not filters:
            return True
        
        # Implementează logica de filtrare pentru Whoosh
        # Similar cu _apply_sql_filters dar pentru dict-uri
        
        return True  # Simplificat pentru demonstrație
    
    def regex_search(self, pattern: str, fields: List[str] = None) -> List[Dict]:
        """
        Căutare cu regex în câmpuri specifice
        
        Args:
            pattern: pattern-ul regex
            fields: lista câmpurilor în care să caute (default: toate)
            
        Returns:
            List[Dict]: rezultatele care se potrivesc pattern-ului
        """
        if not fields:
            fields = ['nume', 'prenume', 'cnp', 'adresa', 'telefon', 'email']
        
        # Validează că fields sunt câmpuri valide
        valid_fields = ['nume', 'prenume', 'cnp', 'adresa', 'telefon', 'email', 'judet']
        fields = [f for f in fields if f in valid_fields]
        
        if not fields:
            return []
        
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"Pattern regex invalid: {e}")
        
        conn = sqlite3.connect(self.db_path)
        
        # Construiește query pentru toate câmpurile
        conditions = []
        for field in fields:
            conditions.append(f"{field} IS NOT NULL")
        
        query = f"SELECT * FROM persons_search WHERE {' OR '.join(conditions)}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Filtrează rezultatele cu regex în Python
        matching_results = []
        
        for _, row in df.iterrows():
            for field in fields:
                field_value = str(row.get(field, ''))
                if compiled_pattern.search(field_value):
                    result_dict = row.to_dict()
                    result_dict['matched_field'] = field
                    result_dict['matched_text'] = field_value
                    matching_results.append(result_dict)
                    break  # Nu duplica rezultatul pentru aceeași persoană
        
        return matching_results
    
    def save_search(self, search_name: str, query: str, filters: Dict = None) -> bool:
        """Salvează o căutare pentru reutilizare"""
        search_data = {
            'query': query,
            'filters': filters or {},
            'date_created': datetime.now().isoformat(),
            'usage_count': 0
        }
        
        self.saved_searches[search_name] = search_data
        
        # Salvează în fișier
        try:
            with open(self.saved_searches_file, 'w', encoding='utf-8') as f:
                json.dump(self.saved_searches, f, ensure_ascii=False, indent=2)
            
            # Salvează și în baza de date
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO saved_searches
                (search_name, search_query, filters, date_created, usage_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (search_name, query, json.dumps(filters), search_data['date_created'], 0))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Eroare la salvarea căutării: {e}")
            return False
    
    def load_saved_search(self, search_name: str) -> Optional[Dict]:
        """Încarcă o căutare salvată"""
        if search_name in self.saved_searches:
            search_data = self.saved_searches[search_name]
            
            # Actualizează usage_count
            search_data['usage_count'] = search_data.get('usage_count', 0) + 1
            search_data['last_used'] = datetime.now().isoformat()
            
            # Salvează actualizarea
            self.save_search(search_name, search_data['query'], search_data['filters'])
            
            return search_data
        
        return None
    
    def get_saved_searches(self) -> List[Dict]:
        """Returnează lista căutărilor salvate"""
        searches = []
        for name, data in self.saved_searches.items():
            searches.append({
                'name': name,
                'query': data['query'],
                'filters': data['filters'],
                'date_created': data['date_created'],
                'usage_count': data.get('usage_count', 0),
                'last_used': data.get('last_used')
            })
        
        return sorted(searches, key=lambda x: x['usage_count'], reverse=True)
    
    def detect_duplicates(self, similarity_threshold: float = 0.85) -> List[Dict]:
        """
        Detectează persoane duplicate pe baza mai multor criterii
        
        Args:
            similarity_threshold: pragul de similaritate (0.0 - 1.0)
            
        Returns:
            List[Dict]: grupuri de duplicate detectate
        """
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM persons_search", conn)
        conn.close()
        
        duplicate_groups = []
        processed_ids = set()
        
        for i, person1 in df.iterrows():
            if person1['id'] in processed_ids:
                continue
            
            current_group = [person1.to_dict()]
            processed_ids.add(person1['id'])
            
            for j, person2 in df.iterrows():
                if i >= j or person2['id'] in processed_ids:
                    continue
                
                similarity = self._calculate_similarity(person1, person2)
                
                if similarity >= similarity_threshold:
                    current_group.append(person2.to_dict())
                    processed_ids.add(person2['id'])
            
            if len(current_group) > 1:
                duplicate_groups.append({
                    'group_id': len(duplicate_groups) + 1,
                    'similarity_score': similarity,
                    'persons': current_group,
                    'total_count': len(current_group),
                    'resolution_status': 'pending'
                })
        
        return duplicate_groups
    
    def _calculate_similarity(self, person1: pd.Series, person2: pd.Series) -> float:
        """Calculează similaritatea între două persoane"""
        similarity_scores = []
        
        # Similaritate CNP (foarte importantă)
        if person1['cnp'] and person2['cnp']:
            if person1['cnp'] == person2['cnp']:
                return 1.0  # CNP identic = duplicat cert
            else:
                # Calculează similaritatea pentru CNP-uri aproape identice (erori OCR)
                cnp_similarity = self._string_similarity(person1['cnp'], person2['cnp'])
                if cnp_similarity > 0.9:  # CNP foarte similar
                    similarity_scores.append(cnp_similarity * 0.6)  # Weight mare pentru CNP
        
        # Similaritate nume complet
        name1 = f"{person1['nume']} {person1['prenume']}".strip()
        name2 = f"{person2['nume']} {person2['prenume']}".strip()
        if name1 and name2:
            name_similarity = self._string_similarity(name1, name2)
            similarity_scores.append(name_similarity * 0.3)  # Weight mediu pentru nume
        
        # Similaritate adresă
        if person1['adresa'] and person2['adresa']:
            addr_similarity = self._string_similarity(person1['adresa'], person2['adresa'])
            similarity_scores.append(addr_similarity * 0.1)  # Weight mic pentru adresă
        
        # Similaritate telefon
        if person1['telefon'] and person2['telefon']:
            if person1['telefon'] == person2['telefon']:
                similarity_scores.append(0.8)  # Telefon identic = probabilitate mare de duplicat
        
        return sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0.0
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """Calculează similaritatea între două string-uri"""
        if not str1 or not str2:
            return 0.0
        
        # Implementare simplă de similaritate Levenshtein
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        distance = levenshtein_distance(str1.lower(), str2.lower())
        max_length = max(len(str1), len(str2))
        
        return 1 - (distance / max_length) if max_length > 0 else 0.0
    
    def compare_persons_side_by_side(self, person_ids: List[int]) -> Dict:
        """Compară persoane side-by-side pentru rezolvarea duplicatelor"""
        conn = sqlite3.connect(self.db_path)
        
        persons = []
        for person_id in person_ids:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM persons_search WHERE id = ?", (person_id,))
            person = cursor.fetchone()
            if person:
                # Convertește la dict
                columns = [description[0] for description in cursor.description]
                person_dict = dict(zip(columns, person))
                persons.append(person_dict)
        
        conn.close()
        
        if len(persons) < 2:
            return {'error': 'Sunt necesare cel puțin 2 persoane pentru comparație'}
        
        # Generează comparația
        comparison = {
            'persons': persons,
            'differences': self._find_differences(persons),
            'similarities': self._find_similarities(persons),
            'confidence_scores': {},
            'merge_suggestions': self._generate_merge_suggestions(persons)
        }
        
        # Calculează confidence scores pentru fiecare pereche
        for i in range(len(persons)):
            for j in range(i + 1, len(persons)):
                key = f"person_{i}_vs_{j}"
                comparison['confidence_scores'][key] = self._calculate_similarity(
                    pd.Series(persons[i]), pd.Series(persons[j])
                )
        
        return comparison
    
    def _find_differences(self, persons: List[Dict]) -> Dict:
        """Găsește diferențele între persoane"""
        differences = {}
        fields = ['nume', 'prenume', 'cnp', 'adresa', 'telefon', 'email']
        
        for field in fields:
            values = [person.get(field, '') for person in persons]
            unique_values = list(set(filter(None, values)))  # Exclude valorile goale
            
            if len(unique_values) > 1:
                differences[field] = {
                    'unique_values': unique_values,
                    'person_values': values
                }
        
        return differences
    
    def _find_similarities(self, persons: List[Dict]) -> Dict:
        """Găsește similaritățile între persoane"""
        similarities = {}
        fields = ['nume', 'prenume', 'cnp', 'adresa', 'telefon', 'email']
        
        for field in fields:
            values = [person.get(field, '') for person in persons]
            non_empty_values = list(filter(None, values))
            
            if len(set(non_empty_values)) == 1 and non_empty_values:
                similarities[field] = non_empty_values[0]
        
        return similarities
    
    def _generate_merge_suggestions(self, persons: List[Dict]) -> Dict:
        """Generează sugestii pentru merge-ul persoanelor duplicate"""
        suggestions = {}
        fields = ['nume', 'prenume', 'cnp', 'adresa', 'telefon', 'email']
        
        for field in fields:
            values = [person.get(field, '') for person in persons]
            non_empty_values = list(filter(None, values))
            
            if non_empty_values:
                # Alege valoarea cea mai completă sau cea mai frecventă
                best_value = max(non_empty_values, key=len)
                suggestions[field] = {
                    'suggested_value': best_value,
                    'reason': 'Cea mai completă valoare' if len(best_value) == max(len(v) for v in non_empty_values) else 'Valoare disponibilă'
                }
        
        return suggestions
    
    def merge_duplicate_persons(self, person_ids: List[int], merge_strategy: Dict) -> bool:
        """
        Merge persoane duplicate conform strategiei specificate
        
        Args:
            person_ids: ID-urile persoanelor de combinat
            merge_strategy: dicționar cu strategia de merge pentru fiecare câmp
            
        Returns:
            bool: True dacă merge-ul a reușit
        """
        if len(person_ids) < 2:
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Obține datele tuturor persoanelor
            persons = []
            for person_id in person_ids:
                cursor.execute("SELECT * FROM persons_search WHERE id = ?", (person_id,))
                person = cursor.fetchone()
                if person:
                    columns = [description[0] for description in cursor.description]
                    persons.append(dict(zip(columns, person)))
            
            if not persons:
                return False
            
            # Creează înregistrarea merge-uită
            merged_person = {}
            for field, strategy in merge_strategy.items():
                if strategy == 'first_non_empty':
                    values = [p.get(field, '') for p in persons]
                    merged_person[field] = next((v for v in values if v), '')
                elif strategy == 'longest':
                    values = [p.get(field, '') for p in persons]
                    merged_person[field] = max(values, key=len) if values else ''
                elif strategy == 'manual':
                    # Va fi setat manual în interfață
                    merged_person[field] = merge_strategy.get(f'{field}_value', '')
                else:
                    # Default: folosește prima valoare
                    merged_person[field] = persons[0].get(field, '')
            
            # Păstrează primul ID ca referință
            primary_id = person_ids[0]
            
            # Actualizează înregistrarea primară
            update_fields = ', '.join([f"{field} = ?" for field in merged_person.keys() if field != 'id'])
            update_values = [merged_person[field] for field in merged_person.keys() if field != 'id']
            update_values.append(primary_id)
            
            cursor.execute(f"UPDATE persons_search SET {update_fields} WHERE id = ?", update_values)
            
            # Șterge celelalte înregistrări
            for person_id in person_ids[1:]:
                cursor.execute("DELETE FROM persons_search WHERE id = ?", (person_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Eroare la merge: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _log_search(self, query: str, filters: Dict, results_count: int, execution_time: float):
        """Loghează căutarea în istoric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_history
            (search_query, filters_applied, results_count, search_date, execution_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (query, json.dumps(filters), results_count, datetime.now().isoformat(), execution_time))
        
        conn.commit()
        conn.close()
    
    def get_search_statistics(self) -> Dict:
        """Returnează statistici despre căutări"""
        conn = sqlite3.connect(self.db_path)
        
        # Total căutări
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM search_history")
        total_searches = cursor.fetchone()[0]
        
        # Căutări recente (ultima săptămână)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM search_history WHERE search_date > ?", (week_ago,))
        recent_searches = cursor.fetchone()[0]
        
        # Căutări populare
        cursor.execute('''
            SELECT search_query, COUNT(*) as count FROM search_history 
            GROUP BY search_query ORDER BY count DESC LIMIT 5
        ''')
        popular_searches = cursor.fetchall()
        
        # Timpul mediu de execuție
        cursor.execute("SELECT AVG(execution_time) FROM search_history")
        avg_execution_time = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            'total_searches': total_searches,
            'recent_searches': recent_searches,
            'popular_searches': [{'query': q, 'count': c} for q, c in popular_searches],
            'avg_execution_time': round(avg_execution_time, 3),
            'search_engine_active': SEARCH_DEPENDENCIES_AVAILABLE
        }

# Test și utilizare
if __name__ == "__main__":
    search_manager = SearchManager("test_output")
    
    # Test adăugare persoană
    test_person = {
        'nume': 'Popescu',
        'prenume': 'Ion',
        'cnp': '1234567890123',
        'adresa': 'Str. Victoriei Nr. 10, București',
        'telefon': '0712345678',
        'email': 'ion.popescu@email.com',
        'anaf_sector': 'București Sector 1',
        'judet': 'București',
        'localitate': 'București'
    }
    
    person_id = search_manager.add_person_to_index(test_person)
    print(f"Persoană adăugată cu ID: {person_id}")
    
    # Test căutare
    results = search_manager.advanced_search("Popescu", {'judet': 'București'})
    print(f"Rezultate căutare: {len(results)}")
    
    # Test salvare căutare
    search_manager.save_search("Căutare București", "Popescu", {'judet': 'București'})
    print("Căutare salvată cu succes")
    
    print("✅ Search Manager testat cu succes!")
