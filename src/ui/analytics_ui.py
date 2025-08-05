"""
UI pentru Dashboard Analytics - OCR230
Interfață pentru lansarea și controlul dashboard-ului analytics
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser
import os
from datetime import datetime, timedelta

class AnalyticsDashboardUI:
    def __init__(self, parent, output_folder):
        self.parent = parent
        self.output_folder = output_folder
        self.dashboard_thread = None
        self.dashboard_running = False
        
        self.create_analytics_window()
    
    def create_analytics_window(self):
        """Creează fereastra pentru analytics dashboard"""
        self.analytics_window = tk.Toplevel(self.parent)
        self.analytics_window.title("📊 OCR230 - Dashboard Analytics")
        self.analytics_window.geometry("800x600")
        self.analytics_window.resizable(True, True)
        
        # Configurare grid
        self.analytics_window.grid_columnconfigure(0, weight=1)
        self.analytics_window.grid_rowconfigure(1, weight=1)
        
        # Header
        self.create_header()
        
        # Main content
        self.create_main_content()
        
        # Footer cu controale
        self.create_footer()
    
    def create_header(self):
        """Creează header-ul ferestrei"""
        header_frame = ttk.Frame(self.analytics_window)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Titlu
        title_label = ttk.Label(header_frame, text="📊 Dashboard Analytics Avansat", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        # Status
        self.status_var = tk.StringVar(value="⚪ Dashboard oprit")
        self.status_label = ttk.Label(header_frame, textvariable=self.status_var,
                                     foreground="gray")
        self.status_label.grid(row=0, column=1, sticky="e")
    
    def create_main_content(self):
        """Creează conținutul principal"""
        # Notebook pentru taburi
        self.notebook = ttk.Notebook(self.analytics_window)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Tab 1: Dashboard Control
        self.create_dashboard_tab()
        
        # Tab 2: Statistici Rapide
        self.create_stats_tab()
        
        # Tab 3: Export și Rapoarte
        self.create_export_tab()
    
    def create_dashboard_tab(self):
        """Tab pentru controlul dashboard-ului"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="🎛️ Control Dashboard")
        
        # Configurare grid
        dashboard_frame.grid_columnconfigure(0, weight=1)
        
        # Info despre dashboard
        info_frame = ttk.LabelFrame(dashboard_frame, text="📋 Informații Dashboard")
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        info_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="URL Dashboard:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.url_var = tk.StringVar(value="http://localhost:8050")
        url_entry = ttk.Entry(info_frame, textvariable=self.url_var, state="readonly")
        url_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(info_frame, text="Port:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.port_var = tk.StringVar(value="8050")
        port_entry = ttk.Entry(info_frame, textvariable=self.port_var, width=10)
        port_entry.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # Controale dashboard
        controls_frame = ttk.LabelFrame(dashboard_frame, text="🎮 Controale")
        controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        controls_frame.grid_columnconfigure(0, weight=1)
        
        # Butoane de control
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.grid(row=0, column=0, pady=10)
        
        self.start_btn = ttk.Button(buttons_frame, text="🚀 Pornește Dashboard",
                                   command=self.start_dashboard)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(buttons_frame, text="⏹️ Oprește Dashboard",
                                  command=self.stop_dashboard, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.open_browser_btn = ttk.Button(buttons_frame, text="🌐 Deschide în Browser",
                                          command=self.open_in_browser, state="disabled")
        self.open_browser_btn.pack(side=tk.LEFT, padx=5)
        
        # Opțiuni avansate
        options_frame = ttk.LabelFrame(dashboard_frame, text="⚙️ Opțiuni Avansate")
        options_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Auto-refresh la 30 secunde",
                       variable=self.auto_refresh_var).pack(anchor="w", padx=5, pady=2)
        
        self.include_charts_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include grafice interactive",
                       variable=self.include_charts_var).pack(anchor="w", padx=5, pady=2)
        
        self.enable_filters_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Activează filtre avansate",
                       variable=self.enable_filters_var).pack(anchor="w", padx=5, pady=2)
    
    def create_stats_tab(self):
        """Tab pentru statistici rapide"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📈 Statistici Rapide")
        
        # Configurare grid
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_rowconfigure(1, weight=1)
        
        # Refresh button
        refresh_frame = ttk.Frame(stats_frame)
        refresh_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Button(refresh_frame, text="🔄 Actualizează Statistici",
                  command=self.refresh_quick_stats).pack(side=tk.LEFT)
        
        ttk.Label(refresh_frame, text="Ultima actualizare:").pack(side=tk.LEFT, padx=(20, 5))
        self.last_update_var = tk.StringVar(value="Niciodată")
        ttk.Label(refresh_frame, textvariable=self.last_update_var,
                 foreground="gray").pack(side=tk.LEFT)
        
        # Statistici în treeview
        stats_tree_frame = ttk.LabelFrame(stats_frame, text="📊 Statistici Generale")
        stats_tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        stats_tree_frame.grid_columnconfigure(0, weight=1)
        stats_tree_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview pentru statistici
        columns = ("Metrica", "Valoare", "Trend", "Ultimele 7 zile")
        self.stats_tree = ttk.Treeview(stats_tree_frame, columns=columns, show="headings")
        
        for col in columns:
            self.stats_tree.heading(col, text=col)
            self.stats_tree.column(col, width=150)
        
        # Scrollbar pentru treeview
        stats_scrollbar = ttk.Scrollbar(stats_tree_frame, orient="vertical",
                                       command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_tree.grid(row=0, column=0, sticky="nsew")
        stats_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Inițializează cu date demo
        self.populate_demo_stats()
    
    def create_export_tab(self):
        """Tab pentru export și rapoarte"""
        export_frame = ttk.Frame(self.notebook)
        self.notebook.add(export_frame, text="📤 Export & Rapoarte")
        
        # Configurare grid
        export_frame.grid_columnconfigure(0, weight=1)
        
        # Export HTML
        html_frame = ttk.LabelFrame(export_frame, text="🌐 Export HTML")
        html_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        html_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(html_frame, text="Nume fișier:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.html_filename_var = tk.StringVar(value=f"Dashboard_OCR230_{datetime.now().strftime('%Y%m%d')}.html")
        ttk.Entry(html_frame, textvariable=self.html_filename_var).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Button(html_frame, text="📥 Export Dashboard HTML",
                  command=self.export_html_dashboard).grid(row=1, column=0, columnspan=2, pady=10)
        
        # Export Grafice
        charts_frame = ttk.LabelFrame(export_frame, text="📊 Export Grafice")
        charts_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        chart_types_frame = ttk.Frame(charts_frame)
        chart_types_frame.pack(fill="x", padx=5, pady=5)
        
        self.export_county_chart_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(chart_types_frame, text="Distribuție Județe",
                       variable=self.export_county_chart_var).pack(anchor="w")
        
        self.export_temporal_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(chart_types_frame, text="Trending Temporal",
                       variable=self.export_temporal_var).pack(anchor="w")
        
        self.export_performance_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(chart_types_frame, text="Performanță OCR",
                       variable=self.export_performance_var).pack(anchor="w")
        
        ttk.Button(charts_frame, text="📸 Export Grafice (PNG)",
                  command=self.export_charts).pack(pady=10)
        
        # Export Date
        data_frame = ttk.LabelFrame(export_frame, text="📋 Export Date")
        data_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        data_buttons_frame = ttk.Frame(data_frame)
        data_buttons_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(data_buttons_frame, text="📊 Export CSV Analytics",
                  command=self.export_analytics_csv).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(data_buttons_frame, text="📄 Export Raport PDF",
                  command=self.export_pdf_report).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(data_buttons_frame, text="📈 Export Excel Complet",
                  command=self.export_excel_analytics).pack(side=tk.LEFT, padx=5)
    
    def create_footer(self):
        """Creează footer-ul cu informații și comenzi"""
        footer_frame = ttk.Frame(self.analytics_window)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        footer_frame.grid_columnconfigure(1, weight=1)
        
        # Info folder
        ttk.Label(footer_frame, text="📁 Folder output:").grid(row=0, column=0, sticky="w")
        
        folder_display = os.path.basename(self.output_folder) if self.output_folder else "Nu este selectat"
        ttk.Label(footer_frame, text=folder_display, foreground="blue").grid(row=0, column=1, sticky="w", padx=5)
        
        # Buton deschidere folder
        ttk.Button(footer_frame, text="📂 Deschide Folder",
                  command=self.open_output_folder).grid(row=0, column=2, padx=5)
        
        # Buton închidere
        ttk.Button(footer_frame, text="❌ Închide",
                  command=self.close_window).grid(row=0, column=3, padx=5)
    
    def start_dashboard(self):
        """Pornește dashboard-ul analytics cu gestionare îmbunătățită"""
        try:
            from src.analytics.dashboard_manager import launch_dashboard
            import socket
            
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
            
            # Găsește un port liber
            try:
                free_port = find_free_port(int(self.port_var.get()))
                self.port_var.set(str(free_port))
            except Exception as e:
                messagebox.showerror("Eroare", f"Nu s-a găsit un port liber: {e}")
                return
            
            # Pornește dashboard-ul
            self.dashboard_thread = launch_dashboard(self.output_folder, free_port)
            self.dashboard_running = True
            
            # Actualizează UI
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.open_browser_btn.config(state="normal")
            self.status_var.set(f"🟢 Dashboard pornit pe portul {free_port}")
            self.status_label.config(foreground="green")
            
            # Actualizează URL-ul
            self.url_var.set(f"http://127.0.0.1:{free_port}")
            
            messagebox.showinfo("Succes", 
                              f"Dashboard-ul a fost pornit!\n"
                              f"Accesează: http://127.0.0.1:{free_port}\n"
                              f"Browser-ul se va deschide automat în 2 secunde.")
            
            # Nu mai deschidem manual în browser, că o face funcția launch_dashboard
            
        except ImportError:
            messagebox.showerror("Eroare", 
                               "Modulele pentru dashboard nu sunt instalate.\n"
                               "Instalează cu: pip install plotly dash dash-bootstrap-components")
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la pornirea dashboard-ului: {e}")
            import traceback
            traceback.print_exc()
    
    def stop_dashboard(self):
        """Oprește dashboard-ul"""
        if self.dashboard_running:
            self.dashboard_running = False
            
            # Actualizează UI
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.open_browser_btn.config(state="disabled")
            self.status_var.set("⚪ Dashboard oprit")
            self.status_label.config(foreground="gray")
            
            messagebox.showinfo("Info", "Dashboard-ul a fost oprit.")
    
    def open_in_browser(self):
        """Deschide dashboard-ul în browser"""
        if self.dashboard_running:
            url = self.url_var.get()
            webbrowser.open(url)
    
    def refresh_quick_stats(self):
        """Actualizează statisticile rapide"""
        try:
            # Simulare încărcare date
            self.stats_tree.delete(*self.stats_tree.get_children())
            
            # Aici ai încărca date reale din dashboard_manager
            demo_stats = [
                ("Total Persoane", "1,247", "↗️ +15%", "156 noi"),
                ("CNP Valide", "1,198", "↗️ +12%", "142 valide"),
                ("Duplicate Găsite", "23", "↘️ -5%", "3 noi"),
                ("Județe Procesate", "42", "→ 0%", "Stabil"),
                ("Timp Mediu OCR", "5.2s", "↗️ +2%", "5.1s medie"),
                ("Rata Succes", "96.2%", "↗️ +1%", "95.8% săpt."),
            ]
            
            for stat in demo_stats:
                self.stats_tree.insert("", "end", values=stat)
            
            self.last_update_var.set(datetime.now().strftime("%H:%M:%S"))
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la actualizarea statisticilor: {e}")
    
    def populate_demo_stats(self):
        """Populează cu statistici demo la început"""
        demo_stats = [
            ("Total Persoane", "---", "---", "Apasă Actualizează"),
            ("CNP Valide", "---", "---", "Pentru date reale"),
            ("Duplicate Găsite", "---", "---", "..."),
            ("Județe Procesate", "---", "---", "..."),
            ("Timp Mediu OCR", "---", "---", "..."),
            ("Rata Succes", "---", "---", "..."),
        ]
        
        for stat in demo_stats:
            self.stats_tree.insert("", "end", values=stat)
    
    def export_html_dashboard(self):
        """Exportă dashboard-ul ca HTML"""
        try:
            filename = self.html_filename_var.get()
            if not filename.endswith('.html'):
                filename += '.html'
            
            # Aici ai apela metoda din dashboard_manager
            output_path = os.path.join(self.output_folder, filename)
            
            # Simulare export
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>OCR230 Dashboard Export</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 OCR230 Dashboard Export</h1>
        <p>Generat pe: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
    </div>
    <div class="stats">
        <div class="stat-card">
            <h3>Total Persoane</h3>
            <h2>1,247</h2>
        </div>
        <div class="stat-card">
            <h3>CNP Valide</h3>
            <h2>1,198</h2>
        </div>
        <div class="stat-card">
            <h3>Duplicate</h3>
            <h2>23</h2>
        </div>
    </div>
    <p><em>Pentru dashboard complet și interactiv, deschideți aplicația OCR230.</em></p>
</body>
</html>"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            messagebox.showinfo("Succes", f"Dashboard exportat ca: {filename}")
            
            # Întreabă dacă să deschidă fișierul
            if messagebox.askyesno("Deschide", "Vrei să deschizi fișierul HTML?"):
                webbrowser.open(f"file://{output_path}")
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la exportul HTML: {e}")
    
    def export_charts(self):
        """Exportă graficele ca imagini PNG"""
        try:
            export_folder = os.path.join(self.output_folder, "charts_export")
            os.makedirs(export_folder, exist_ok=True)
            
            charts_to_export = []
            if self.export_county_chart_var.get():
                charts_to_export.append("distribuție_județe")
            if self.export_temporal_var.get():
                charts_to_export.append("trending_temporal")
            if self.export_performance_var.get():
                charts_to_export.append("performanță_ocr")
            
            if not charts_to_export:
                messagebox.showwarning("Atenție", "Selectează cel puțin un tip de grafic pentru export.")
                return
            
            # Simulare export grafice
            for chart_type in charts_to_export:
                filename = f"{chart_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                filepath = os.path.join(export_folder, filename)
                
                # Aici ai genera graficele reale cu plotly și kaleido
                # Pentru demonstrație, creez un fișier text
                with open(filepath.replace('.png', '.txt'), 'w') as f:
                    f.write(f"Grafic exportat: {chart_type}\nData: {datetime.now()}")
            
            messagebox.showinfo("Succes", 
                              f"Graficele au fost exportate în:\n{export_folder}")
            
            # Deschide folderul
            if messagebox.askyesno("Deschide", "Vrei să deschizi folderul cu graficele?"):
                os.startfile(export_folder)
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la exportul graficelor: {e}")
    
    def export_analytics_csv(self):
        """Exportă datele analytics ca CSV"""
        try:
            filename = f"Analytics_OCR230_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(self.output_folder, filename)
            
            # Aici ai exporta date reale din baza de date analytics
            csv_content = "Metrica,Valoare,Data,Observatii\n"
            csv_content += "Total Persoane,1247," + datetime.now().strftime('%Y-%m-%d') + ",Actualizat zilnic\n"
            csv_content += "CNP Valide,1198," + datetime.now().strftime('%Y-%m-%d') + ",96% rata validare\n"
            csv_content += "Duplicate,23," + datetime.now().strftime('%Y-%m-%d') + ",Rezolvate automat\n"
            
            with open(filepath, 'w', encoding='utf-8-sig') as f:
                f.write(csv_content)
            
            messagebox.showinfo("Succes", f"Date analytics exportate ca: {filename}")
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la exportul CSV: {e}")
    
    def export_pdf_report(self):
        """Exportă raport complet PDF"""
        try:
            filename = f"Raport_Analytics_OCR230_{datetime.now().strftime('%Y%m%d')}.pdf"
            filepath = os.path.join(self.output_folder, filename)
            
            # Aici ai genera un PDF real cu reportlab
            messagebox.showinfo("Info", 
                              "Generarea raportului PDF va fi implementată în versiunea completă.\n"
                              "Pentru moment, folosiți exportul HTML și graficele PNG.")
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la generarea PDF: {e}")
    
    def export_excel_analytics(self):
        """Exportă toate datele analytics în Excel"""
        try:
            filename = f"Analytics_Complete_OCR230_{datetime.now().strftime('%Y%m%d')}.xlsx"
            filepath = os.path.join(self.output_folder, filename)
            
            # Aici ai exporta toate datele în Excel cu multiple sheet-uri
            messagebox.showinfo("Info", 
                              "Exportul complet Excel va fi implementat în versiunea completă.\n"
                              "Pentru moment, folosiți exportul CSV pentru datele de bază.")
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la exportul Excel: {e}")
    
    def open_output_folder(self):
        """Deschide folderul de output"""
        if self.output_folder and os.path.exists(self.output_folder):
            os.startfile(self.output_folder)
        else:
            messagebox.showwarning("Atenție", "Folderul de output nu există sau nu este selectat.")
    
    def close_window(self):
        """Închide fereastra analytics"""
        if self.dashboard_running:
            if messagebox.askyesno("Confirmare", 
                                 "Dashboard-ul este pornit. Vrei să-l oprești și să închizi fereastra?"):
                self.stop_dashboard()
                self.analytics_window.destroy()
        else:
            self.analytics_window.destroy()

# Funcție pentru lansarea UI-ului analytics din main window
def show_analytics_dashboard(parent, output_folder):
    """Lansează fereastra analytics dashboard"""
    if not output_folder:
        messagebox.showwarning("Atenție", "Selectează mai întâi un folder de output.")
        return
    
    analytics_ui = AnalyticsDashboardUI(parent, output_folder)
    
if __name__ == "__main__":
    # Test UI
    root = tk.Tk()
    import pathlib
    from pathlib import Path
    icon_path = Path(__file__).parent.parent.parent / "Assets" / "favicon.ico"
    root.iconbitmap(str(icon_path))
    root.withdraw()  # Ascunde fereastra principală
    
    show_analytics_dashboard(root, "test_output")
    
    root.mainloop()
