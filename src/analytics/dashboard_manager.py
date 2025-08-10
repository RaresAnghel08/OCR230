"""
Dashboard Manager pentru Analytics Avansat - OCR230
Crează dashboard-uri interactive cu Plotly/Dash pentru analiză avansată
"""

import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import sqlite3
from pathlib import Path

class DashboardManager:
    def __init__(self, output_folder: str, user_config: dict = None):
        self.output_folder = output_folder
        self.user_config = user_config or {}
        self.db_path = os.path.join(output_folder, "analytics.db")
        self.sessions_file = os.path.join(output_folder, "processing_sessions.json")
        self.live_stats_file = os.path.join(output_folder, "live_stats.json")  # Pentru statistici live
        self.current_session_id = None  # ID-ul sesiunii curente
        self._excel_last_modified = None  # Pentru a detecta modificări Excel
        self._processing_complete = False  # Flag pentru a opri refresh-urile inutile
        
        # Cache pentru datele finale - pentru a opri update-urile după procesare
        self._final_data_cache = None
        self._final_charts_cache = {}
        self._cache_created_at = None
        self._stop_updates_after_complete = False
        
        self.init_database()
        
    def init_database(self):
        """Inițializează baza de date pentru analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel pentru sesiunile de procesare
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processing_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TEXT,
                files_processed INTEGER,
                cnp_valid INTEGER,
                cnp_invalid INTEGER,
                duplicates_found INTEGER,
                processing_time REAL,
                avg_ocr_confidence REAL,
                errors_count INTEGER
            )
        ''')
        
        # Tabel pentru statistici detaliate pe județe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS county_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                county_name TEXT,
                persons_count INTEGER,
                anaf_sector TEXT,
                avg_processing_time REAL,
                FOREIGN KEY (session_id) REFERENCES processing_sessions (id)
            )
        ''')
        
        # Tabel pentru performanța OCR
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ocr_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                file_name TEXT,
                processing_time REAL,
                ocr_confidence REAL,
                errors_detected INTEGER,
                cnp_extracted TEXT,
                FOREIGN KEY (session_id) REFERENCES processing_sessions (id)
            )
        ''')
        
        conn.commit()
        
        
        conn.close()
    
    def log_processing_session(self, session_data: Dict):
        """Loghează o sesiune de procesare"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO processing_sessions 
            (session_date, files_processed, cnp_valid, cnp_invalid, duplicates_found, 
             processing_time, avg_ocr_confidence, errors_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_data.get('date', datetime.now().isoformat()),
            session_data.get('files_processed', 0),
            session_data.get('cnp_valid', 0),
            session_data.get('cnp_invalid', 0),
            session_data.get('duplicates_found', 0),
            session_data.get('processing_time', 0),
            session_data.get('avg_ocr_confidence', 0),
            session_data.get('errors_count', 0)
        ))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id
    
    def start_live_session(self):
        """Începe o sesiune live de procesare"""
        # Resetează flag-ul de procesare completă pentru o nouă sesiune
        self._processing_complete = False
        self._excel_last_modified = None
        
        live_stats = {
            'session_start': datetime.now().isoformat(),
            'files_processed': 0,
            'cnp_valid': 0,
            'cnp_invalid': 0,
            'duplicates_found': 0,
            'current_file': '',
            'processing_speed': 0.0,
            'estimated_time_left': 0,
            'errors_count': 0
        }
        
        # Salvează în fișier pentru actualizare live
        with open(self.live_stats_file, 'w', encoding='utf-8') as f:
            json.dump(live_stats, f, indent=2)
        
        # Creează o sesiune în baza de date
        session_data = {
            'date': live_stats['session_start'],
            'files_processed': 0,
            'cnp_valid': 0,
            'cnp_invalid': 0,
            'duplicates_found': 0,
            'processing_time': 0,
            'avg_ocr_confidence': 0,
            'errors_count': 0
        }
        
        self.current_session_id = self.log_processing_session(session_data)
        print("🔄 Nouă sesiune live începută - dashboard refresh reactivat")
        return self.current_session_id
    
    def update_live_stats(self, **kwargs):
        """Actualizează statisticile live"""
        try:
            # Încarcă statisticile curente
            if os.path.exists(self.live_stats_file):
                with open(self.live_stats_file, 'r', encoding='utf-8') as f:
                    live_stats = json.load(f)
            else:
                live_stats = {}
            
            # Actualizează cu noile valori
            for key, value in kwargs.items():
                live_stats[key] = value
            
            # Calculează viteza și timpul rămas
            if 'files_processed' in live_stats and 'session_start' in live_stats:
                start_time = datetime.fromisoformat(live_stats['session_start'])
                elapsed_time = (datetime.now() - start_time).total_seconds()
                
                if elapsed_time > 0 and live_stats['files_processed'] > 0:
                    live_stats['processing_speed'] = live_stats['files_processed'] / (elapsed_time / 60)  # fișiere/min
                    
                    if 'total_files' in live_stats and live_stats['processing_speed'] > 0:
                        remaining_files = live_stats['total_files'] - live_stats['files_processed']
                        live_stats['estimated_time_left'] = remaining_files / (live_stats['processing_speed'] / 60)
            
            # Salvează statisticile actualizate
            with open(self.live_stats_file, 'w', encoding='utf-8') as f:
                json.dump(live_stats, f, indent=2)
                
            print(f"🔄 Live stats updated: {kwargs}")
            
        except Exception as e:
            print(f"❌ Eroare la actualizarea statisticilor live: {e}")
    
    def mark_processing_complete(self):
        """Marchează procesarea ca fiind completă pentru a opri refresh-urile automate"""
        self._processing_complete = True
        print("✅ Procesarea marcată ca fiind completă - dashboard refresh automat va fi oprit")
    
    def reset_processing_state(self):
        """Resetează starea procesării pentru o nouă sesiune"""
        self._processing_complete = False
        self._excel_last_modified = None
        print("🔄 Starea procesării resetată - dashboard refresh reactivat")
    
    def get_live_stats(self):
        """Obține statisticile live curente"""
        try:
            if os.path.exists(self.live_stats_file):
                with open(self.live_stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Eroare la citirea statisticilor live: {e}")
        return {}
    
    def finish_live_session(self):
        """Finalizează sesiunea live și actualizează baza de date"""
        try:
            live_stats = self.get_live_stats()
            if live_stats and self.current_session_id:
                # Calculează timpul total de procesare
                start_time = datetime.fromisoformat(live_stats['session_start'])
                total_time = (datetime.now() - start_time).total_seconds()
                
                # Actualizează sesiunea în baza de date
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE processing_sessions 
                    SET files_processed = ?, cnp_valid = ?, cnp_invalid = ?, 
                        duplicates_found = ?, processing_time = ?, errors_count = ?
                    WHERE id = ?
                ''', (
                    live_stats.get('files_processed', 0),
                    live_stats.get('cnp_valid', 0),
                    live_stats.get('cnp_invalid', 0),
                    live_stats.get('duplicates_found', 0),
                    total_time,
                    live_stats.get('errors_count', 0),
                    self.current_session_id
                ))
                
                conn.commit()
                conn.close()
                
                # MARCHEAZĂ procesarea ca fiind completă pentru a opri update-urile automate
                self._processing_complete = True  # ACTIVAT pentru a opri update-urile dashboard
                
                # Păstrează datele în fișierul live pentru afișare continuă
                final_stats = live_stats.copy()
                final_stats['session_active'] = False
                final_stats['processing_speed'] = 0
                final_stats['estimated_time_left'] = 0
                
                with open(self.live_stats_file, 'w', encoding='utf-8') as f:
                    json.dump(final_stats, f, ensure_ascii=False, indent=2)
                
                print(f"✅ Sesiunea live finalizată: {live_stats['files_processed']} fișiere procesate")
                print("� Datele rămân disponibile în dashboard pentru vizualizare continuă")
                
        except Exception as e:
            print(f"❌ Eroare la finalizarea sesiunii live: {e}")
        finally:
            self.current_session_id = None
    
    def _create_sample_data(self):
        """Creează date de test pentru dashboard"""
        import random
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        judete = ['BUCURESTI', 'CLUJ', 'TIMIS', 'BRASOV', 'CONSTANTA', 'IASI', 'DOLJ', 'GALATI', 'HUNEDOARA', 'PRAHOVA']
        
        # Creează 10 sesiuni de test din ultimele 30 de zile
        for i in range(10):
            date = datetime.now() - timedelta(days=random.randint(0, 30))
            files_proc = random.randint(5, 50)
            cnp_valid = random.randint(int(files_proc * 0.7), files_proc)
            cnp_invalid = files_proc - cnp_valid
            duplicates = random.randint(0, int(files_proc * 0.1))
            
            session_data = {
                'date': date.isoformat(),
                'files_processed': files_proc,
                'cnp_valid': cnp_valid,
                'cnp_invalid': cnp_invalid,
                'duplicates_found': duplicates,
                'processing_time': random.uniform(30, 300),
                'avg_ocr_confidence': random.uniform(75, 95),
                'errors_count': random.randint(0, 5)
            }
            
            cursor.execute('''
                INSERT INTO processing_sessions 
                (session_date, files_processed, cnp_valid, cnp_invalid, duplicates_found, 
                 processing_time, avg_ocr_confidence, errors_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_data['date'],
                session_data['files_processed'],
                session_data['cnp_valid'],
                session_data['cnp_invalid'],
                session_data['duplicates_found'],
                session_data['processing_time'],
                session_data['avg_ocr_confidence'],
                session_data['errors_count']
            ))
            
            session_id = cursor.lastrowid
            
            # Adaugă statistici pentru județe
            for judet in random.sample(judete, random.randint(3, 7)):
                cursor.execute('''
                    INSERT INTO county_stats (session_id, county_name, persons_count, anaf_sector, avg_processing_time)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    session_id,
                    judet,
                    random.randint(1, 15),
                    f"ANAF_{judet}",
                    random.uniform(5, 30)
                ))
        
        conn.commit()
        conn.close()
        print("✅ Date de test create pentru dashboard!")
    
    def create_interactive_dashboard(self):
        """Creează dashboard-ul interactiv cu Dash"""
        app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        
        # Informații utilizator pentru personalizare
        user_name = self.user_config.get('name', 'Utilizator')
        user_ong = self.user_config.get('ong', 'Organizație')
        user_email = self.user_config.get('email', '')
        user_admin_id = self.user_config.get('admin_id', '')
        
        app.layout = dbc.Container([
            # Header personalizat cu informații utilizator
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H1("📊 OCR230 - Dashboard Analytics", 
                                   className="text-center mb-2", 
                                   style={'color': '#2c3e50'}),
                            html.H4(f"👤 {user_name}", 
                                   className="text-center mb-1", 
                                   style={'color': '#34495e'}),
                            html.H5(f"🏢 {user_ong}", 
                                   className="text-center mb-1", 
                                   style={'color': '#7f8c8d'}),
                            html.P(f"📧 {user_email}" if user_email else "", 
                                  className="text-center mb-1", 
                                  style={'color': '#95a5a6', 'fontSize': '14px'}),
                            html.P(f"🆔 ID: {user_admin_id}" if user_admin_id else "", 
                                  className="text-center mb-1", 
                                  style={'color': '#95a5a6', 'fontSize': '12px'}),
                            html.P(f"📂 Folder: {self.output_folder}", 
                                  className="text-center mb-0", 
                                  style={'color': '#bdc3c7', 'fontSize': '11px'})
                        ])
                    ], color="light")
                ])
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    html.Hr()
                ])
            ]),
            
            # Control Panel
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🎛️ Panou Control"),
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Perioada:"),
                                    dcc.DatePickerRange(
                                        id='date-picker-range',
                                        start_date=datetime.now() - timedelta(days=30),
                                        end_date=datetime.now(),
                                        display_format='DD/MM/YYYY'
                                    )
                                ], width=6),
                                dbc.Col([
                                    html.Label("Județ:"),
                                    dcc.Dropdown(
                                        id='county-dropdown',
                                        options=[{'label': 'Toate Județele', 'value': 'all'}],
                                        value='all'
                                    )
                                ], width=6)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("🔄 Actualizează", id="refresh-btn", color="primary", className="mt-2"),
                                    dbc.Button("📥 Export HTML", id="export-btn", color="success", className="mt-2 ms-2")
                                ])
                            ])
                        ])
                    ])
                ])
            ], className="mb-4"),
            
            # Statistici Generale + Live Stats
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📈 Statistici Generale", className="card-title"),
                            dcc.Graph(id='general-stats-chart')
                        ])
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("⚡ Sesiune Live", className="card-title"),
                            dcc.Graph(id='live-stats-chart')
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),
            
            # Distribuție Județe
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🗺️ Distribuție Județe", className="card-title"),
                            dcc.Graph(id='county-distribution-chart')
                        ])
                    ])
                ])
            ], className="mb-4"),
            
            # Heatmap România și Performance OCR
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🌡️ Heatmap România", className="card-title"),
                            dcc.Graph(id='romania-heatmap')
                        ])
                    ])
                ], width=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("⚡ Performance OCR", className="card-title"),
                            dcc.Graph(id='ocr-performance-chart')
                        ])
                    ])
                ], width=4)
            ], className="mb-4"),
            
            # Trending Temporal
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("📊 Trending Temporal", className="card-title"),
                            dcc.Graph(id='temporal-trends-chart')
                        ])
                    ])
                ])
            ], className="mb-4"),
            
            # Comparare Sesiuni
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("🔄 Comparare Sesiuni", className="card-title"),
                            dcc.Graph(id='sessions-comparison-chart')
                        ])
                    ])
                ])
            ])
            
        ], fluid=True)
        
        # Adaugă un interval pentru refresh automat doar dacă procesarea nu este completă
        app.layout.children.append(
            dcc.Interval(
                id='interval-component',
                interval=3*1000,  # Actualizează la fiecare 3 secunde
                n_intervals=0,
                disabled=False  # Va fi dezactivat când procesarea este completă
            )
        )
        
        # Callbacks pentru interactivitate
        self._setup_callbacks(app)
        
        return app
    
    def _setup_callbacks(self, app):
        """Configurează callback-urile pentru dashboard"""
        
        @app.callback(
            [Output('general-stats-chart', 'figure'),
             Output('live-stats-chart', 'figure'),
             Output('county-distribution-chart', 'figure'),
             Output('romania-heatmap', 'figure'),
             Output('ocr-performance-chart', 'figure'),
             Output('temporal-trends-chart', 'figure'),
             Output('sessions-comparison-chart', 'figure'),
             Output('interval-component', 'disabled')],  # Adaugă control pentru interval
            [Input('refresh-btn', 'n_clicks'),
             Input('interval-component', 'n_intervals'),
             Input('date-picker-range', 'start_date'),
             Input('date-picker-range', 'end_date'),
             Input('county-dropdown', 'value')]
        )
        def update_dashboard(n_clicks, n_intervals, start_date, end_date, selected_county):
                    # Verifică dacă procesarea este completă pentru a opri intervalul
                    live_stats = self.get_live_stats()

                    # OPREȘTE COMPLET UPDATE-URILE DUPĂ PROCESARE
                    should_disable_interval = False

                    # Verifică IMEDIAT dacă procesarea s-a terminat - fără să mai aștepte intervale
                    if self._processing_complete:
                        should_disable_interval = True
                        print("✅ Procesarea completă - OPRESC IMEDIAT toate update-urile dashboard!")

                        # Returnează ultimele chart-uri cached dacă sunt disponibile
                        if hasattr(self, '_final_charts_cache') and self._final_charts_cache:
                            return tuple(list(self._final_charts_cache.values()) + [should_disable_interval])
                        else:
                            # Dacă nu avem cache, creează unul gol pentru a opri complet update-urile
                            empty_fig = go.Figure().add_annotation(text="Procesare completă - Dashboard oprit", x=0.5, y=0.5)
                            empty_charts = [empty_fig] * 7  # 7 chart-uri
                            return tuple(empty_charts + [should_disable_interval])

                    # Verifică și prin live_stats dacă sesiunea nu mai este activă
                    if live_stats and not live_stats.get('session_active', True):
                        should_disable_interval = True
                        print("✅ Sesiune inactivă - OPRESC IMEDIAT toate update-urile dashboard!")
                        # Similar pentru sesiune inactivă
                        if hasattr(self, '_final_charts_cache') and self._final_charts_cache:
                            return tuple(list(self._final_charts_cache.values()) + [should_disable_interval])
                        else:
                            empty_fig = go.Figure().add_annotation(text="Sesiune inactivă - Dashboard oprit", x=0.5, y=0.5)
                            empty_charts = [empty_fig] * 7
                            return tuple(empty_charts + [should_disable_interval])

                    # Încarcă datele doar dacă nu trebuie să oprim update-urile
                    if should_disable_interval and hasattr(self, '_final_charts_cache') and self._final_charts_cache:
                        # Returnează cache-ul final fără să mai facă query-uri
                        return tuple(list(self._final_charts_cache.values()) + [should_disable_interval])

                    data = self._load_analytics_data(start_date, end_date, selected_county)

                    # Creează graficele
                    general_stats = self._create_general_stats_chart(data)
                    live_stats_chart = self._create_live_stats_chart()
                    county_dist = self._create_county_distribution_chart(data)
                    romania_heatmap = self._create_romania_heatmap(data)
                    ocr_performance = self._create_ocr_performance_chart(data)
                    temporal_trends = self._create_temporal_trends_chart(data)
                    sessions_comparison = self._create_sessions_comparison_chart(data)

                    # Salvează în cache pentru utilizare ulterioară
                    self._final_charts_cache = {
                        'general_stats': general_stats,
                        'live_stats_chart': live_stats_chart,
                        'county_dist': county_dist,
                        'romania_heatmap': romania_heatmap,
                        'ocr_performance': ocr_performance,
                        'temporal_trends': temporal_trends,
                        'sessions_comparison': sessions_comparison
                    }

                    return (general_stats, live_stats_chart, county_dist, romania_heatmap, 
                           ocr_performance, temporal_trends, sessions_comparison, should_disable_interval)
    
    def _load_analytics_data(self, start_date, end_date, county_filter):
        """Încarcă datele pentru analytics din baza de date și Excel"""
        conn = sqlite3.connect(self.db_path)
        
        # Query principal pentru sesiuni
        query = '''
            SELECT * FROM processing_sessions 
            WHERE session_date BETWEEN ? AND ?
            ORDER BY session_date DESC
        '''
        
        sessions_df = pd.read_sql_query(query, conn, params=[start_date, end_date])
        
        # Query pentru statistici județe
        county_query = '''
            SELECT cs.*, ps.session_date 
            FROM county_stats cs
            JOIN processing_sessions ps ON cs.session_id = ps.id
            WHERE ps.session_date BETWEEN ? AND ?
        '''
        
        if county_filter != 'all':
            county_query += ' AND cs.county_name = ?'
            params = [start_date, end_date, county_filter]
        else:
            params = [start_date, end_date]
            
        county_df = pd.read_sql_query(county_query, conn, params=params)
        conn.close()
        
        # 📊 ÎNCARCĂ ȘI DATELE DIN EXCEL DACĂ EXISTĂ
        excel_data = self._load_excel_data()
        if excel_data is not None:
            # Integrează datele din Excel cu cele din baza de date
            excel_counties = excel_data.groupby('ANAF_Apartin').size().reset_index(name='persons_count')
            excel_counties.columns = ['county_name', 'persons_count']
            excel_counties['session_date'] = datetime.now().isoformat()
            excel_counties['anaf_sector'] = excel_counties['county_name']
            excel_counties['avg_processing_time'] = 15.0  # valoare medie
            
            # Combină datele
            if not county_df.empty:
                county_df = pd.concat([county_df, excel_counties], ignore_index=True)
            else:
                county_df = excel_counties
        
        return {
            'sessions': sessions_df,
            'counties': county_df
        }
    
    def _load_excel_data(self):
        """Încarcă datele din Excel dacă există"""
        excel_path = os.path.join(self.output_folder, "Date_Persoane_OCR.xlsx")
        if os.path.exists(excel_path):
            try:
                # Verifică timpul de modificare pentru a evita încărcări inutile
                current_modified = os.path.getmtime(excel_path)
                
                # Dacă fișierul nu s-a modificat și procesarea e completă, nu-l mai încărca
                if (self._excel_last_modified == current_modified and 
                    self._processing_complete):
                    return None
                
                # Dacă s-a modificat sau este prima încărcare
                if self._excel_last_modified != current_modified:
                    df = pd.read_excel(excel_path, sheet_name='Date_Persoane')
                    self._excel_last_modified = current_modified
                    
                    # Printează mesajul doar dacă procesarea nu este completă
                    if not self._processing_complete:
                        print(f"📊 Încărcat Excel cu {len(df)} înregistrări")
                    
                    return df
                else:
                    # Returnează datele cached - ÎNTOTDEAUNA încarcă datele pentru chart-uri
                    try:
                        df = pd.read_excel(excel_path, sheet_name='Date_Persoane')
                        return df
                    except Exception as e:
                        print(f"⚠️ Eroare la încărcarea Excel pentru cache: {e}")
                        return None
                    
            except Exception as e:
                print(f"⚠️ Eroare la încărcarea Excel: {e}")
                return None
        return None
    
    def _create_general_stats_chart(self, data):
        """Creează graficul cu statistici generale"""
        # 🔥 OBȚINE STATISTICILE LIVE PENTRU A INCLUDE SESIUNEA CURENTĂ
        live_stats = self.get_live_stats()
        
        if data['sessions'].empty:
            # Încearcă să încarce date din Excel chiar dacă nu există sesiuni
            excel_data = self._load_excel_data()
            if excel_data is not None:
                total_files = len(excel_data)
                total_valid_cnp = len(excel_data[excel_data['CNP'].notna()])
                total_invalid_cnp = total_files - total_valid_cnp
                
                # 📈 ADAUGĂ DATELE LIVE LA TOTALURI DACĂ EXISTĂ
                if live_stats:
                    total_files += live_stats.get('files_processed', 0)
                    total_valid_cnp += live_stats.get('cnp_valid', 0)
                    total_invalid_cnp += live_stats.get('cnp_invalid', 0)
                
                fig = go.Figure()
                
                fig.add_trace(go.Indicator(
                    mode = "number",
                    value = total_files,
                    title = {"text": "📄 Total Fișiere Procesate" + (" (Include Live)" if live_stats and live_stats.get('files_processed', 0) > 0 else "")},
                    domain = {'row': 0, 'column': 0}
                ))
                
                fig.add_trace(go.Indicator(
                    mode = "number+gauge",
                    value = (total_valid_cnp / (total_valid_cnp + total_invalid_cnp) * 100) if (total_valid_cnp + total_invalid_cnp) > 0 else 0,
                    title = {"text": "✅ Rata CNP Complete (%)"},
                    gauge = {'axis': {'range': [None, 100]},
                            'bar': {'color': "green"},
                            'steps': [{'range': [0, 50], 'color': "lightgray"},
                                     {'range': [50, 80], 'color': "yellow"},
                                     {'range': [80, 100], 'color': "lightgreen"}]},
                    domain = {'row': 0, 'column': 1}
                ))
                
                fig.update_layout(
                    grid = {'rows': 1, 'columns': 2, 'pattern': "independent"},
                    height=300,
                    title="Statistici Generale" + (" + Live Session" if live_stats and live_stats.get('files_processed', 0) > 0 else "")
                )
                
                return fig
            else:
                # Dacă nu există nici Excel nici sesiuni, dar există date live
                if live_stats and live_stats.get('files_processed', 0) > 0:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Indicator(
                        mode = "number",
                        value = live_stats.get('files_processed', 0),
                        title = {"text": "📄 Total Fișiere Procesate (Live)"},
                        domain = {'row': 0, 'column': 0}
                    ))
                    
                    total_cnp = live_stats.get('cnp_valid', 0) + live_stats.get('cnp_invalid', 0)
                    cnp_rate = (live_stats.get('cnp_valid', 0) / total_cnp * 100) if total_cnp > 0 else 0
                    
                    fig.add_trace(go.Indicator(
                        mode = "number+gauge",
                        value = cnp_rate,
                        title = {"text": "✅ Rata CNP Complete (%)"},
                        gauge = {'axis': {'range': [None, 100]},
                                'bar': {'color': "green"},
                                'steps': [{'range': [0, 50], 'color': "lightgray"},
                                         {'range': [50, 80], 'color': "yellow"},
                                         {'range': [80, 100], 'color': "lightgreen"}]},
                        domain = {'row': 0, 'column': 1}
                    ))
                    
                    fig.update_layout(
                        grid = {'rows': 1, 'columns': 2, 'pattern': "independent"},
                        height=300,
                        title="Statistici Live"
                    )
                    
                    return fig
                else:
                    return go.Figure().add_annotation(text="Nu există date disponibile. Rulează o procesare pentru a vedea statistici.", x=0.5, y=0.5)
        
        df = data['sessions']
        
        # Calculează totalurile din sesiunile anterioare
        total_files = df['files_processed'].sum()
        total_valid_cnp = df['cnp_valid'].sum()
        total_invalid_cnp = df['cnp_invalid'].sum()
        total_duplicates = df['duplicates_found'].sum()
        
        # 🔥 ADAUGĂ DATELE LIVE LA TOTALURI DACĂ EXISTĂ O SESIUNE ACTIVĂ
        if live_stats and live_stats.get('files_processed', 0) > 0:
            total_files += live_stats.get('files_processed', 0)
            total_valid_cnp += live_stats.get('cnp_valid', 0)
            total_invalid_cnp += live_stats.get('cnp_invalid', 0)
            total_duplicates += live_stats.get('duplicates_found', 0)
        
        fig = go.Figure()
        
        # Adaugă indicatori
        fig.add_trace(go.Indicator(
            mode = "number+delta",
            value = total_files,
            title = {"text": "📄 Total Fișiere Procesate" + (" (Include Live)" if live_stats and live_stats.get('files_processed', 0) > 0 else "")},
            domain = {'row': 0, 'column': 0}
        ))
        
        fig.add_trace(go.Indicator(
            mode = "number+gauge",
            value = (total_valid_cnp / (total_valid_cnp + total_invalid_cnp) * 100) if (total_valid_cnp + total_invalid_cnp) > 0 else 0,
            title = {"text": "✅ Rata CNP Valide (%)"},
            gauge = {'axis': {'range': [None, 100]},
                    'bar': {'color': "green"},
                    'steps': [{'range': [0, 50], 'color': "lightgray"},
                             {'range': [50, 80], 'color': "yellow"},
                             {'range': [80, 100], 'color': "lightgreen"}]},
            domain = {'row': 0, 'column': 1}
        ))
        
        fig.update_layout(
            grid = {'rows': 1, 'columns': 2, 'pattern': "independent"},
            height=300,
            title="Statistici din Sesiuni de Procesare" + (" + Live Session" if live_stats and live_stats.get('files_processed', 0) > 0 else "")
        )
        
        return fig
    
    def _create_live_stats_chart(self):
        """Creează graficul cu statistici live din sesiunea curentă"""
        live_stats = self.get_live_stats()
        
        # Dacă nu avem date live, încarcă ultimele date din baza de date
        if not live_stats:
            # Încearcă să încărce datele din ultima sesiune
            conn = sqlite3.connect(self.db_path)
            try:
                query = "SELECT * FROM processing_sessions ORDER BY session_date DESC LIMIT 1"
                result = pd.read_sql_query(query, conn)
                if not result.empty:
                    latest_session = result.iloc[0]
                    live_stats = {
                        'files_processed': latest_session['files_processed'],
                        'total_files': latest_session['files_processed'],  # Folosim același număr
                        'cnp_valid': latest_session['cnp_valid'],
                        'cnp_invalid': latest_session['cnp_invalid'],
                        'processing_speed': 0,  # Procesarea s-a terminat
                        'estimated_time_left': 0,
                        'session_active': False
                    }
            except Exception as e:
                print(f"⚠️ Nu s-au putut încărca datele din baza de date: {e}")
            finally:
                conn.close()
        
        # Dacă tot nu avem date, afișează mesaj
        if not live_stats:
            return go.Figure().add_annotation(
                text="Nu există date de procesare disponibile",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16, color="gray")
            )
        
        # Determină statusul procesării
        is_active = live_stats.get('session_active', False) or live_stats.get('processing_speed', 0) > 0
        status_text = "🟢 Procesare ACTIVĂ" if is_active else "🔴 Procesare COMPLETĂ"
        
        # Creează indicatori pentru sesiunea live
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Fișiere Procesate", f"CNP Valide - {status_text}"),
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]],
            vertical_spacing=0.25
        )
        
        # Fișiere procesate
        fig.add_trace(go.Indicator(
            mode="number+gauge",
            value=live_stats.get('files_processed', 0),
            title={"text": "Fișiere"},
            gauge={'axis': {'range': [None, live_stats.get('total_files', 100)]},
                   'bar': {'color': "darkblue"},
                   'steps': [{'range': [0, live_stats.get('total_files', 100) * 0.5], 'color': "lightgray"},
                            {'range': [live_stats.get('total_files', 100) * 0.5, live_stats.get('total_files', 100)], 'color': "gray"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                                'thickness': 0.75, 'value': live_stats.get('total_files', 100)}}
        ), row=1, col=1)
        
        # CNP Valide
        total_cnp = live_stats.get('cnp_valid', 0) + live_stats.get('cnp_invalid', 0)
        cnp_rate = (live_stats.get('cnp_valid', 0) / total_cnp * 100) if total_cnp > 0 else 0
        
        fig.add_trace(go.Indicator(
            mode="number+gauge",
            value=cnp_rate,
            title={"text": "CNP (%)"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "green"},
                   'steps': [{'range': [0, 70], 'color': "lightgray"},
                            {'range': [70, 90], 'color': "yellow"},
                            {'range': [90, 100], 'color': "lightgreen"}]}
        ), row=1, col=2)
        
        # Viteză procesare
        fig.add_trace(go.Indicator(
            mode="number",
            value=live_stats.get('processing_speed', 0),
            title={"text": "Viteză Procesare (fișiere/min)"},
            number={'suffix': " f/min"}
        ), row=2, col=1)
        
        # Timp rămas
        eta = live_stats.get('estimated_time_left', 0)
        eta_unit = "min" if eta > 60 else "sec"
        eta_value = eta/60 if eta > 60 else eta
        
        fig.add_trace(go.Indicator(
            mode="number",
            value=eta_value,
            title={"text": f"ETA ({eta_unit})"},
            number={'suffix': f" {eta_unit}"}
        ), row=2, col=2)
        
        fig.update_layout(
            height=350,  # Măresc înălțimea și mai mult pentru spațiu optim
            title_text="🔥 Sesiune Live de Procesare",
            title_x=0.5
        )
        
        return fig
    
    def _create_county_distribution_chart(self, data):
        """Creează graficul de distribuție pe județe"""
        if data['counties'].empty:
            # Încearcă să încarce din Excel
            excel_data = self._load_excel_data()
            if excel_data is not None and 'ANAF_Apartin' in excel_data.columns:
                county_counts = excel_data['ANAF_Apartin'].value_counts().head(10)
                df = pd.DataFrame({
                    'county_name': county_counts.index,
                    'persons_count': county_counts.values
                })
                
                fig = px.bar(df, x='county_name', y='persons_count',
                            title="Top 10 Județe din Excel",
                            labels={'county_name': 'Județ', 'persons_count': 'Număr Persoane'})
                fig.update_layout(height=300)
                return fig
            else:
                return go.Figure().add_annotation(text="Nu există date despre județe")
        
        df = data['counties'].groupby('county_name')['persons_count'].sum().reset_index()
        df = df.sort_values('persons_count', ascending=False).head(10)
        
        fig = px.bar(df, x='county_name', y='persons_count',
                    title="Top 10 Județe după numărul de persoane",
                    labels={'county_name': 'Județ', 'persons_count': 'Număr Persoane'})
        
        fig.update_layout(height=300)
        return fig
    
    def _create_romania_heatmap(self, data):
        """Creează heatmap-ul pentru România"""
        if data['counties'].empty:
            return go.Figure().add_annotation(text="Nu există date disponibile")
        
        # Simulare coordonate pentru județe (în practică ai nevoie de un fișier GeoJSON)
        county_stats = data['counties'].groupby('county_name').agg({
            'persons_count': 'sum',
            'avg_processing_time': 'mean'
        }).reset_index()
        
        # Pentru demonstrație, creez un scatter plot
        # În realitate ai avea nevoie de coordonatele geografice ale județelor
        fig = px.scatter(county_stats, 
                        x='county_name', 
                        y='persons_count',
                        size='persons_count',
                        color='avg_processing_time',
                        title="Intensitatea procesării pe județe",
                        labels={'county_name': 'Județ', 'persons_count': 'Nr. Persoane'})
        
        fig.update_layout(height=400)
        return fig
    
    def _create_ocr_performance_chart(self, data):
        """Creează graficul de performanță OCR"""
        if data['sessions'].empty:
            return go.Figure().add_annotation(text="Nu există date disponibile")
        
        df = data['sessions']
        
        fig = go.Figure()
        
        # Timpul mediu de procesare
        fig.add_trace(go.Scatter(
            x=df['session_date'],
            y=df['processing_time'],
            mode='lines+markers',
            name='Timp procesare (s)',
            line=dict(color='blue')
        ))
        
        # Încrederea OCR
        fig.add_trace(go.Scatter(
            x=df['session_date'],
            y=df['avg_ocr_confidence'],
            mode='lines+markers',
            name='Încredere OCR (%)',
            yaxis='y2',
            line=dict(color='green')
        ))
        
        fig.update_layout(
            title="Performanța OCR în timp",
            xaxis_title="Data",
            yaxis=dict(title="Timp procesare (s)", side="left"),
            yaxis2=dict(title="Încredere OCR (%)", side="right", overlaying="y"),
            height=300
        )
        
        return fig
    
    def _create_temporal_trends_chart(self, data):
        """Creează graficul de trending temporal"""
        if data['sessions'].empty:
            return go.Figure().add_annotation(text="Nu există date disponibile")
        
        df = data['sessions'].copy()
        df['session_date'] = pd.to_datetime(df['session_date'])
        df = df.sort_values('session_date')
        
        fig = make_subplots(rows=2, cols=1, 
                           subplot_titles=('Fișiere procesate în timp', 'Calitatea procesării'),
                           specs=[[{"secondary_y": False}], [{"secondary_y": True}]])
        
        # Fișiere procesate
        fig.add_trace(go.Scatter(x=df['session_date'], y=df['files_processed'],
                                mode='lines+markers', name='Fișiere procesate'),
                     row=1, col=1)
        
        # CNP valide vs invalide
        fig.add_trace(go.Scatter(x=df['session_date'], y=df['cnp_valid'],
                                mode='lines+markers', name='CNP Valide'),
                     row=2, col=1)
        
        fig.add_trace(go.Scatter(x=df['session_date'], y=df['cnp_invalid'],
                                mode='lines+markers', name='CNP Invalide'),
                     row=2, col=1)
        
        fig.update_layout(height=500, title_text="Trending Temporal - Activitate Procesare")
        return fig
    
    def _create_sessions_comparison_chart(self, data):
        """Creează graficul de comparare între sesiuni"""
        if data['sessions'].empty:
            return go.Figure().add_annotation(text="Nu există date disponibile")
        
        df = data['sessions'].tail(5)  # Ultimele 5 sesiuni
        
        categories = ['Fișiere procesate', 'CNP Valide', 'CNP Invalide', 'Duplicate găsite']
        
        fig = go.Figure()
        
        for idx, row in df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row['files_processed'], row['cnp_valid'], row['cnp_invalid'], row['duplicates_found']],
                theta=categories,
                fill='toself',
                name=f"Sesiunea {row['session_date'][:10]}"
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True)
            ),
            title="Comparare Sesiuni de Procesare",
            height=400
        )
        
        return fig
    
    def export_dashboard_html(self, filename: Optional[str] = None):
        """Exportă dashboard-ul ca HTML pentru prezentări"""
        if not filename:
            filename = f"OCR230_Dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Creează dashboard-ul
        app = self.create_interactive_dashboard()
        
        # Generează HTML static (aici ai nevoie de o implementare mai complexă)
        # Pentru moment, salvez configurația
        export_path = os.path.join(self.output_folder, filename)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OCR230 Dashboard Export</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <h1>OCR230 Analytics Dashboard - Export</h1>
            <p>Generat pe: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            <p>Pentru dashboard interactiv complet, rulați aplicația OCR230.</p>
        </body>
        </html>
        """
        
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return export_path

# Funcție utilitară pentru lansarea dashboard-ului
def launch_dashboard(output_folder: str, port: int = 8050, analytics_manager_instance=None, user_config: dict = None):
    """
    Lansează dashboard-ul analytics cu gestionare îmbunătățită a porturilor
    
    Args:
        output_folder: Folderul cu datele de output
        port: Portul pe care să ruleze (default 8050)
        analytics_manager_instance: Instanță existentă de DashboardManager (opțional)
        user_config: Configurația utilizatorului pentru personalizare (opțional)
    """
    import socket
    import threading
    import webbrowser
    import time
    
    def find_free_port(start_port: int = 8050) -> int:
        """Găsește un port liber începând cu start_port"""
        for port_try in range(start_port, start_port + 10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port_try))
                    return port_try
            except OSError:
                continue
        raise RuntimeError("Nu s-a găsit niciun port liber între 8050-8059")
    
    def start_server():
        """Pornește serverul Dash în thread separat"""
        try:
            # Folosește instanța existentă sau creează una nouă
            if analytics_manager_instance is not None:
                dashboard = analytics_manager_instance
                # Actualizează configurația utilizatorului dacă este furnizată
                if user_config:
                    dashboard.user_config = user_config
                print("🔗 Folosesc instanța existentă de DashboardManager")
            else:
                dashboard = DashboardManager(output_folder, user_config)
                print("🆕 Creez o nouă instanță de DashboardManager")
                
            app = dashboard.create_interactive_dashboard()
            
            # Găsește un port liber
            free_port = find_free_port(port)
            url = f"http://127.0.0.1:{free_port}"
            
            print(f"🚀 Lansând dashboard analytics pe {url}")
            
            # Deschide browser-ul automat după o scurtă întârziere
            def open_browser():
                time.sleep(2)
                try:
                    webbrowser.open(url)
                    print(f"✅ Browser deschis automat pentru {url}")
                except Exception as e:
                    print(f"⚠️ Nu s-a putut deschide browser-ul automat: {e}")
                    print(f"🔗 Accesează manual: {url}")
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            # Pornește serverul
            app.run(debug=False, port=free_port, host='127.0.0.1')
            
        except Exception as e:
            print(f"❌ Eroare la lansarea dashboard-ului: {e}")
            import traceback
            traceback.print_exc()
    
    # Pornește serverul în thread separat pentru a nu bloca UI-ul
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    return server_thread

if __name__ == "__main__":
    # Test
    test_folder = "test_output"
    os.makedirs(test_folder, exist_ok=True)
    
    # Test cu configurație utilizator
    test_user_config = {
        'name': 'Ion Popescu',
        'ong': 'ONG Test România',
        'email': 'ion.popescu@test.ro',
        'admin_id': 'TEST001'
    }
    
    dashboard = DashboardManager(test_folder, test_user_config)
    
    # Simulare date pentru test
    test_session = {
        'date': datetime.now().isoformat(),
        'files_processed': 25,
        'cnp_valid': 23,
        'cnp_invalid': 2,
        'duplicates_found': 1,
        'processing_time': 125.5,
        'avg_ocr_confidence': 87.3,
        'errors_count': 2
    }
    
    dashboard.log_processing_session(test_session)
    print("✅ Test dashboard creat cu succes!")
    
    # Test lansare dashboard
    launch_dashboard(test_folder, user_config=test_user_config)
