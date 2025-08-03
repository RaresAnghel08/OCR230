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
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        self.db_path = os.path.join(output_folder, "analytics.db")
        self.sessions_file = os.path.join(output_folder, "processing_sessions.json")
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
    
    def create_interactive_dashboard(self):
        """Creează dashboard-ul interactiv cu Dash"""
        app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        
        app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("📊 OCR230 - Dashboard Analytics", className="text-center mb-4"),
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
            
            # Statistici Generale
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
                            html.H4("🗺️ Distribuție Județe", className="card-title"),
                            dcc.Graph(id='county-distribution-chart')
                        ])
                    ])
                ], width=6)
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
        
        # Callbacks pentru interactivitate
        self._setup_callbacks(app)
        
        return app
    
    def _setup_callbacks(self, app):
        """Configurează callback-urile pentru dashboard"""
        
        @app.callback(
            [Output('general-stats-chart', 'figure'),
             Output('county-distribution-chart', 'figure'),
             Output('romania-heatmap', 'figure'),
             Output('ocr-performance-chart', 'figure'),
             Output('temporal-trends-chart', 'figure'),
             Output('sessions-comparison-chart', 'figure')],
            [Input('refresh-btn', 'n_clicks'),
             Input('date-picker-range', 'start_date'),
             Input('date-picker-range', 'end_date'),
             Input('county-dropdown', 'value')]
        )
        def update_dashboard(n_clicks, start_date, end_date, selected_county):
            # Încarcă datele
            data = self._load_analytics_data(start_date, end_date, selected_county)
            
            # Creează graficele
            general_stats = self._create_general_stats_chart(data)
            county_dist = self._create_county_distribution_chart(data)
            romania_heatmap = self._create_romania_heatmap(data)
            ocr_performance = self._create_ocr_performance_chart(data)
            temporal_trends = self._create_temporal_trends_chart(data)
            sessions_comparison = self._create_sessions_comparison_chart(data)
            
            return general_stats, county_dist, romania_heatmap, ocr_performance, temporal_trends, sessions_comparison
    
    def _load_analytics_data(self, start_date, end_date, county_filter):
        """Încarcă datele pentru analytics"""
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
        
        return {
            'sessions': sessions_df,
            'counties': county_df
        }
    
    def _create_general_stats_chart(self, data):
        """Creează graficul cu statistici generale"""
        if data['sessions'].empty:
            return go.Figure().add_annotation(text="Nu există date disponibile")
        
        df = data['sessions']
        
        # Calculează totalurile
        total_files = df['files_processed'].sum()
        total_valid_cnp = df['cnp_valid'].sum()
        total_invalid_cnp = df['cnp_invalid'].sum()
        total_duplicates = df['duplicates_found'].sum()
        
        fig = go.Figure()
        
        # Adaugă indicatori
        fig.add_trace(go.Indicator(
            mode = "number+delta",
            value = total_files,
            title = {"text": "📄 Total Fișiere Procesate"},
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
            height=300
        )
        
        return fig
    
    def _create_county_distribution_chart(self, data):
        """Creează graficul de distribuție pe județe"""
        if data['counties'].empty:
            return go.Figure().add_annotation(text="Nu există date disponibile")
        
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
def launch_dashboard(output_folder: str, port: int = 8050):
    """Lansează dashboard-ul analytics"""
    dashboard = DashboardManager(output_folder)
    app = dashboard.create_interactive_dashboard()
    
    print(f"🚀 Lansând dashboard analytics pe http://localhost:{port}")
    app.run_server(debug=False, port=port, host='127.0.0.1')

if __name__ == "__main__":
    # Test
    test_folder = "test_output"
    os.makedirs(test_folder, exist_ok=True)
    
    dashboard = DashboardManager(test_folder)
    
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
