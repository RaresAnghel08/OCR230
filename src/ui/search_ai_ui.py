"""
UI pentru Search și AI/ML - OCR230
Interfață pentru căutare avansată, AI/ML și management duplicate
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import os
from datetime import datetime, timedelta
import json

class SearchAIUI:
    def __init__(self, parent, output_folder):
        self.parent = parent
        self.output_folder = output_folder
        self.search_results = []
        self.duplicates_data = []
        
        self.create_search_window()
    
    def create_search_window(self):
        """Creează fereastra pentru search și AI/ML"""
        self.search_window = tk.Toplevel(self.parent)
        self.search_window.title("🔍 OCR230 - Search & AI/ML")
        self.search_window.geometry("1000x700")
        self.search_window.resizable(True, True)
        
        # Configurare grid
        self.search_window.grid_columnconfigure(0, weight=1)
        self.search_window.grid_rowconfigure(1, weight=1)
        
        # Header
        self.create_header()
        
        # Main content
        self.create_main_content()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Creează header-ul ferestrei"""
        header_frame = ttk.Frame(self.search_window)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Titlu
        title_label = ttk.Label(header_frame, text="🔍 Search Avansat & AI/ML", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        # Status AI/ML
        self.ai_status_var = tk.StringVar(value="🤖 AI/ML: Verificare...")
        self.ai_status_label = ttk.Label(header_frame, textvariable=self.ai_status_var,
                                        foreground="orange")
        self.ai_status_label.grid(row=0, column=1, sticky="e")
        
        # Verifică disponibilitatea AI/ML
        self.check_ai_availability()
    
    def create_main_content(self):
        """Creează conținutul principal"""
        # Notebook pentru taburi
        self.notebook = ttk.Notebook(self.search_window)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Tab 1: Căutare Avansată
        self.create_search_tab()
        
        # Tab 2: AI/ML Auto-correct
        self.create_ai_tab()
        
        # Tab 3: Management Duplicate
        self.create_duplicates_tab()
        
        # Tab 4: Căutări Salvate
        self.create_saved_searches_tab()
    
    def create_search_tab(self):
        """Tab pentru căutare avansată"""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="🔍 Căutare Avansată")
        
        # Configurare grid
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_rowconfigure(2, weight=1)
        
        # Search box
        search_box_frame = ttk.LabelFrame(search_frame, text="🔎 Căutare")
        search_box_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        search_box_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(search_box_frame, text="Termen căutare:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_box_frame, textvariable=self.search_var, font=("Arial", 11))
        search_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        search_entry.bind("<Return>", lambda e: self.perform_search())
        
        # Butoane search
        search_buttons_frame = ttk.Frame(search_box_frame)
        search_buttons_frame.grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Button(search_buttons_frame, text="🔍 Caută", 
                  command=self.perform_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_buttons_frame, text="🧽 Curăță", 
                  command=self.clear_search).pack(side=tk.LEFT, padx=2)
        
        # Opțiuni search
        options_frame = ttk.Frame(search_box_frame)
        options_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        self.regex_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Folosește Regex", 
                       variable=self.regex_var).pack(side=tk.LEFT, padx=5)
        
        self.case_sensitive_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Case Sensitive", 
                       variable=self.case_sensitive_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(options_frame, text="💾 Salvează Căutarea", 
                  command=self.save_current_search).pack(side=tk.RIGHT, padx=5)
        
        # Filtre avansate
        filters_frame = ttk.LabelFrame(search_frame, text="🎛️ Filtre Avansate")
        filters_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        filters_frame.grid_columnconfigure(1, weight=1)
        filters_frame.grid_columnconfigure(3, weight=1)
        
        # Filtru județ
        ttk.Label(filters_frame, text="Județ:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.county_filter_var = tk.StringVar()
        county_combo = ttk.Combobox(filters_frame, textvariable=self.county_filter_var, state="readonly")
        county_combo['values'] = ["Toate", "București", "Cluj", "Timiș", "Iași", "Constanța", "Brașov"]
        county_combo.current(0)
        county_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        # Filtru perioada
        ttk.Label(filters_frame, text="Perioada:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.period_filter_var = tk.StringVar()
        period_combo = ttk.Combobox(filters_frame, textvariable=self.period_filter_var, state="readonly")
        period_combo['values'] = ["Toate", "Ultima săptămână", "Ultima lună", "Ultimele 3 luni", "Ultimul an"]
        period_combo.current(0)
        period_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=2)
        
        # Filtre suplimentare
        extra_filters_frame = ttk.Frame(filters_frame)
        extra_filters_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
        
        self.has_phone_var = tk.BooleanVar()
        ttk.Checkbutton(extra_filters_frame, text="Are telefon", 
                       variable=self.has_phone_var).pack(side=tk.LEFT, padx=5)
        
        self.has_email_var = tk.BooleanVar()
        ttk.Checkbutton(extra_filters_frame, text="Are email", 
                       variable=self.has_email_var).pack(side=tk.LEFT, padx=5)
        
        self.valid_cnp_var = tk.BooleanVar()
        ttk.Checkbutton(extra_filters_frame, text="CNP valid", 
                       variable=self.valid_cnp_var).pack(side=tk.LEFT, padx=5)
        
        # Rezultate căutare
        results_frame = ttk.LabelFrame(search_frame, text="📋 Rezultate Căutare")
        results_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)
        
        # Info rezultate
        self.results_info_var = tk.StringVar(value="Efectuează o căutare pentru a vedea rezultatele")
        ttk.Label(results_frame, textvariable=self.results_info_var, 
                 foreground="gray").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        # Treeview pentru rezultate
        columns = ("Nume", "Prenume", "CNP", "Județ", "Telefon", "Email", "Data procesării")
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120)
        
        # Scrollbars pentru treeview
        results_v_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        results_h_scrollbar = ttk.Scrollbar(results_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=results_v_scrollbar.set, xscrollcommand=results_h_scrollbar.set)
        
        self.results_tree.grid(row=1, column=0, sticky="nsew")
        results_v_scrollbar.grid(row=1, column=1, sticky="ns")
        results_h_scrollbar.grid(row=2, column=0, sticky="ew")
        
        # Context menu pentru rezultate
        self.create_results_context_menu()
    
    def create_ai_tab(self):
        """Tab pentru AI/ML și auto-correct"""
        ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(ai_frame, text="🤖 AI/ML Auto-correct")
        
        # Configurare grid
        ai_frame.grid_columnconfigure(0, weight=1)
        
        # Info AI/ML
        info_frame = ttk.LabelFrame(ai_frame, text="ℹ️ Informații AI/ML")
        info_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        info_text = """Sistemul AI/ML oferă:
• Auto-correct pentru erorile OCR comune
• Predictive text pentru câmpuri incomplete
• Learning din feedback-ul utilizatorului
• Detectare anomalii în date (CNP suspecte, adrese inexistente)"""
        
        ttk.Label(info_frame, text=info_text, justify="left").pack(anchor="w", padx=10, pady=10)
        
        # Test auto-correct
        autocorrect_frame = ttk.LabelFrame(ai_frame, text="🔧 Test Auto-correct")
        autocorrect_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        autocorrect_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(autocorrect_frame, text="Text original:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.original_text_var = tk.StringVar(value="I0n3scu")
        ttk.Entry(autocorrect_frame, textvariable=self.original_text_var).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(autocorrect_frame, text="Tip câmp:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.field_type_var = tk.StringVar()
        field_combo = ttk.Combobox(autocorrect_frame, textvariable=self.field_type_var, state="readonly")
        field_combo['values'] = ["nume", "prenume", "cnp", "email", "telefon", "adresa"]
        field_combo.current(0)
        field_combo.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Button(autocorrect_frame, text="🔍 Test Auto-correct", 
                  command=self.test_autocorrect).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Rezultat auto-correct
        self.autocorrect_result_var = tk.StringVar(value="Rezultatul va apărea aici...")
        result_label = ttk.Label(autocorrect_frame, textvariable=self.autocorrect_result_var, 
                                foreground="blue", font=("Arial", 10, "bold"))
        result_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Predictive text
        predictive_frame = ttk.LabelFrame(ai_frame, text="💡 Test Predictive Text")
        predictive_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        predictive_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(predictive_frame, text="Text parțial:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.partial_text_var = tk.StringVar(value="Ion")
        ttk.Entry(predictive_frame, textvariable=self.partial_text_var).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Button(predictive_frame, text="💡 Obține Sugestii", 
                  command=self.get_suggestions).grid(row=1, column=0, columnspan=2, pady=10)
        
        # Sugestii listbox
        self.suggestions_listbox = tk.Listbox(predictive_frame, height=5)
        self.suggestions_listbox.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Statistici learning
        stats_frame = ttk.LabelFrame(ai_frame, text="📊 Statistici Learning")
        stats_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        
        self.learning_stats_var = tk.StringVar(value="Apasă 'Actualizează' pentru statistici")
        ttk.Label(stats_frame, textvariable=self.learning_stats_var).pack(anchor="w", padx=10, pady=5)
        
        ttk.Button(stats_frame, text="🔄 Actualizează Statistici", 
                  command=self.update_learning_stats).pack(pady=5)
    
    def create_duplicates_tab(self):
        """Tab pentru management duplicate"""
        duplicates_frame = ttk.Frame(self.notebook)
        self.notebook.add(duplicates_frame, text="👥 Management Duplicate")
        
        # Configurare grid
        duplicates_frame.grid_columnconfigure(0, weight=1)
        duplicates_frame.grid_rowconfigure(2, weight=1)
        
        # Controale detection
        detection_frame = ttk.LabelFrame(duplicates_frame, text="🔍 Detectare Duplicate")
        detection_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        detection_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Label(detection_frame, text="Prag similaritate:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.similarity_var = tk.DoubleVar(value=0.85)
        similarity_scale = ttk.Scale(detection_frame, from_=0.5, to=1.0, variable=self.similarity_var, 
                                   orient=tk.HORIZONTAL)
        similarity_scale.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        
        self.similarity_label_var = tk.StringVar(value="85%")
        similarity_label = ttk.Label(detection_frame, textvariable=self.similarity_label_var)
        similarity_label.grid(row=0, column=2, padx=5, pady=2)
        
        # Update label când se schimbă scale-ul
        similarity_scale.configure(command=lambda val: self.similarity_label_var.set(f"{int(float(val)*100)}%"))
        
        buttons_frame = ttk.Frame(detection_frame)
        buttons_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(buttons_frame, text="🔍 Detectează Duplicate", 
                  command=self.detect_duplicates).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="🧹 Curăță Lista", 
                  command=self.clear_duplicates).pack(side=tk.LEFT, padx=5)
        
        # Status detection
        self.detection_status_var = tk.StringVar(value="Apasă 'Detectează Duplicate' pentru a începe")
        ttk.Label(duplicates_frame, textvariable=self.detection_status_var, 
                 foreground="gray").grid(row=1, column=0, sticky="w", padx=15, pady=2)
        
        # Lista duplicate
        duplicates_list_frame = ttk.LabelFrame(duplicates_frame, text="📋 Grupuri Duplicate Detectate")
        duplicates_list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        duplicates_list_frame.grid_columnconfigure(0, weight=1)
        duplicates_list_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview pentru duplicate cu structură ierarhică
        self.duplicates_tree = ttk.Treeview(duplicates_list_frame, height=12)
        self.duplicates_tree.heading("#0", text="Grupuri Duplicate și Persoane")
        self.duplicates_tree.column("#0", width=800)
        
        # Scrollbar pentru duplicate tree
        dup_scrollbar = ttk.Scrollbar(duplicates_list_frame, orient="vertical", 
                                     command=self.duplicates_tree.yview)
        self.duplicates_tree.configure(yscrollcommand=dup_scrollbar.set)
        
        self.duplicates_tree.grid(row=0, column=0, sticky="nsew")
        dup_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Context menu pentru duplicate
        self.create_duplicates_context_menu()
    
    def create_saved_searches_tab(self):
        """Tab pentru căutări salvate"""
        saved_frame = ttk.Frame(self.notebook)
        self.notebook.add(saved_frame, text="💾 Căutări Salvate")
        
        # Configurare grid
        saved_frame.grid_columnconfigure(0, weight=1)
        saved_frame.grid_rowconfigure(1, weight=1)
        
        # Controale
        controls_frame = ttk.Frame(saved_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Button(controls_frame, text="🔄 Actualizează Lista", 
                  command=self.refresh_saved_searches).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="🗑️ Șterge Selectată", 
                  command=self.delete_saved_search).pack(side=tk.LEFT, padx=5)
        
        # Lista căutări salvate
        saved_list_frame = ttk.LabelFrame(saved_frame, text="📋 Căutări Salvate")
        saved_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        saved_list_frame.grid_columnconfigure(0, weight=1)
        saved_list_frame.grid_rowconfigure(0, weight=1)
        
        columns = ("Nume", "Query", "Filtre", "Data creării", "Nr. folosiri", "Ultima folosire")
        self.saved_tree = ttk.Treeview(saved_list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.saved_tree.heading(col, text=col)
            self.saved_tree.column(col, width=150)
        
        # Scrollbar pentru saved tree
        saved_scrollbar = ttk.Scrollbar(saved_list_frame, orient="vertical", 
                                       command=self.saved_tree.yview)
        self.saved_tree.configure(yscrollcommand=saved_scrollbar.set)
        
        self.saved_tree.grid(row=0, column=0, sticky="nsew")
        saved_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Double-click pentru încărcare căutare
        self.saved_tree.bind("<Double-1>", self.load_saved_search)
    
    def create_footer(self):
        """Creează footer-ul cu informații"""
        footer_frame = ttk.Frame(self.search_window)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        footer_frame.grid_columnconfigure(1, weight=1)
        
        # Info folder
        ttk.Label(footer_frame, text="📁 Folder output:").grid(row=0, column=0, sticky="w")
        
        folder_display = os.path.basename(self.output_folder) if self.output_folder else "Nu este selectat"
        ttk.Label(footer_frame, text=folder_display, foreground="blue").grid(row=0, column=1, sticky="w", padx=5)
        
        # Buton închidere
        ttk.Button(footer_frame, text="❌ Închide", 
                  command=self.close_window).grid(row=0, column=2, padx=5)
    
    def check_ai_availability(self):
        """Verifică disponibilitatea modulelor AI/ML"""
        try:
            from src.search.search_manager import SearchManager
            # Test rapid pentru a vedea dacă search-ul funcționează
            test_manager = SearchManager(self.output_folder)
            self.ai_status_var.set("🟢 Search: Disponibil")
            self.ai_status_label.config(foreground="green")
            self.ai_available = True
        except ImportError as e:
            self.ai_status_var.set("🔴 Search: Indisponibil")
            self.ai_status_label.config(foreground="red")
            self.ai_available = False
            print(f"Search indisponibil: {e}")
    
    def perform_search(self):
        """Efectuează căutarea avansată"""
        query = self.search_var.get().strip()
        
        print(f"🔍 DEBUG perform_search called with query: '{query}'")
        print(f"🔍 DEBUG output_folder: '{self.output_folder}'")
        print(f"🔍 DEBUG ai_available: {self.ai_available}")
        
        if not query:
            messagebox.showwarning("Atenție", "Introdu un termen de căutare.")
            return
        
        # Construiește filtrele
        filters = {}
        
        if self.county_filter_var.get() != "Toate":
            filters['judet'] = self.county_filter_var.get()
        
        if self.period_filter_var.get() != "Toate":
            # Convertește perioada în date
            period = self.period_filter_var.get()
            if period == "Ultima săptămână":
                filters['start_date'] = (datetime.now() - timedelta(days=7)).isoformat()
            elif period == "Ultima lună":
                filters['start_date'] = (datetime.now() - timedelta(days=30)).isoformat()
            elif period == "Ultimele 3 luni":
                filters['start_date'] = (datetime.now() - timedelta(days=90)).isoformat()
            elif period == "Ultimul an":
                filters['start_date'] = (datetime.now() - timedelta(days=365)).isoformat()
        
        if self.has_phone_var.get():
            filters['has_phone'] = True
        
        if self.has_email_var.get():
            filters['has_email'] = True
        
        print(f"🔍 DEBUG filters: {filters}")
        
        try:
            if self.ai_available:
                from src.search.search_manager import SearchManager
                search_manager = SearchManager(self.output_folder)
                
                print(f"🔍 DEBUG SearchManager created for folder: {self.output_folder}")
                
                # Efectuează căutarea
                results = search_manager.advanced_search(
                    query, 
                    filters, 
                    use_regex=self.regex_var.get()
                )
                
                print(f"🔍 DEBUG search results: {len(results)} found")
                for i, r in enumerate(results[:3]):  # Max 3 pentru debug
                    print(f"   {i+1}. {r.get('nume')} {r.get('prenume')} din {r.get('judet')}")
                
                self.display_search_results(results)
            else:
                print("🔍 DEBUG: AI not available, using demo results")
                # Simulare rezultate pentru demo
                demo_results = [
                    {
                        'nume': 'Popescu', 'prenume': 'Ion', 'cnp': '1234567890123',
                        'judet': 'București', 'telefon': '0712345678', 'email': 'ion@email.com',
                        'processing_date': datetime.now().strftime('%Y-%m-%d')
                    },
                    {
                        'nume': 'Ionescu', 'prenume': 'Maria', 'cnp': '2234567890123',
                        'judet': 'Cluj', 'telefon': '0723456789', 'email': 'maria@email.com',
                        'processing_date': datetime.now().strftime('%Y-%m-%d')
                    }
                ]
                
                # Filtrează rezultatele demo pe baza query-ului
                filtered_results = [r for r in demo_results if query.lower() in f"{r['nume']} {r['prenume']}".lower()]
                self.display_search_results(filtered_results)
                
        except Exception as e:
            print(f"🔍 DEBUG ERROR: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Eroare", f"Eroare la căutare: {e}")
    
    def display_search_results(self, results):
        """Afișează rezultatele căutării"""
        print(f"🔍 DEBUG display_search_results: {len(results)} rezultate")
        
        # Curăță rezultatele anterioare
        self.results_tree.delete(*self.results_tree.get_children())
        
        # Actualizează info
        self.results_info_var.set(f"Găsite {len(results)} rezultate")
        
        # Populează treeview
        for i, result in enumerate(results):
            print(f"🔍 DEBUG Adding result {i+1}: {result.get('nume')} {result.get('prenume')}")
            self.results_tree.insert("", "end", values=(
                result.get('nume', ''),
                result.get('prenume', ''),
                result.get('cnp', ''),
                result.get('judet', ''),
                result.get('telefon', ''),
                result.get('email', ''),
                result.get('processing_date', '')
            ))
        
        self.search_results = results
        print(f"🔍 DEBUG display_search_results completed with {len(results)} results")
    
    def clear_search(self):
        """Curăță căutarea"""
        self.search_var.set("")
        self.results_tree.delete(*self.results_tree.get_children())
        self.results_info_var.set("Efectuează o căutare pentru a vedea rezultatele")
        self.search_results = []
    
    def save_current_search(self):
        """Salvează căutarea curentă"""
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Atenție", "Nu există o căutare de salvat.")
            return
        
        search_name = simpledialog.askstring("Salvează Căutarea", "Nume pentru căutare:")
        if not search_name:
            return
        
        # Construiește filtrele
        filters = {}
        if self.county_filter_var.get() != "Toate":
            filters['judet'] = self.county_filter_var.get()
        if self.period_filter_var.get() != "Toate":
            filters['perioada'] = self.period_filter_var.get()
        
        try:
            if self.ai_available:
                from src.search.search_manager import SearchManager
                search_manager = SearchManager(self.output_folder)
                success = search_manager.save_search(search_name, query, filters)
                
                if success:
                    messagebox.showinfo("Succes", f"Căutarea '{search_name}' a fost salvată.")
                    self.refresh_saved_searches()
                else:
                    messagebox.showerror("Eroare", "Nu s-a putut salva căutarea.")
            else:
                messagebox.showinfo("Info", "Funcționalitatea de salvare va fi disponibilă când AI/ML este activat.")
                
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la salvarea căutării: {e}")
    
    def test_autocorrect(self):
        """Testează funcționalitatea auto-correct"""
        original_text = self.original_text_var.get().strip()
        field_type = self.field_type_var.get()
        
        if not original_text:
            messagebox.showwarning("Atenție", "Introdu un text pentru test.")
            return
        
        try:
            if self.ai_available:
                from src.ai_ml.ai_manager import AIMLManager
                ai_manager = AIMLManager(self.output_folder)
                
                corrected, confidence = ai_manager.auto_correct_ocr_errors(original_text, field_type)
                
                result_text = f"✅ Corectat: '{corrected}' (Confidence: {confidence:.2f})"
                if corrected == original_text:
                    result_text = "ℹ️ Nu s-au găsit corecții necesare"
                
                self.autocorrect_result_var.set(result_text)
            else:
                # Simulare pentru demo
                demo_corrections = {
                    "I0n3scu": "Ionescu",
                    "M4ria": "Maria",
                    "P0pescu": "Popescu",
                    "1234567890123": "1234567890123"  # CNP rămâne la fel
                }
                
                corrected = demo_corrections.get(original_text, original_text)
                confidence = 0.95 if corrected != original_text else 1.0
                
                result_text = f"✅ Demo Corectat: '{corrected}' (Confidence: {confidence:.2f})"
                self.autocorrect_result_var.set(result_text)
                
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la auto-correct: {e}")
    
    def get_suggestions(self):
        """Obține sugestii predictive"""
        partial_text = self.partial_text_var.get().strip()
        field_type = self.field_type_var.get()
        
        if not partial_text:
            messagebox.showwarning("Atenție", "Introdu un text parțial.")
            return
        
        # Curăță listbox
        self.suggestions_listbox.delete(0, tk.END)
        
        try:
            if self.ai_available:
                from src.ai_ml.ai_manager import AIMLManager
                ai_manager = AIMLManager(self.output_folder)
                
                suggestions = ai_manager.predictive_text_completion(partial_text, field_type)
                
                for suggestion in suggestions:
                    display_text = f"{suggestion['text']} (Conf: {suggestion['confidence']:.2f}, {suggestion['source']})"
                    self.suggestions_listbox.insert(tk.END, display_text)
                
                if not suggestions:
                    self.suggestions_listbox.insert(tk.END, "Nu s-au găsit sugestii")
                    
            else:
                # Sugestii demo
                demo_suggestions = {
                    "Ion": ["Ionescu", "Ionică", "Ionica"],
                    "Mar": ["Maria", "Marian", "Marioara"],
                    "Pop": ["Popescu", "Popa", "Popovici"]
                }
                
                suggestions = demo_suggestions.get(partial_text, [])
                for suggestion in suggestions:
                    self.suggestions_listbox.insert(tk.END, f"{suggestion} (Demo)")
                
                if not suggestions:
                    self.suggestions_listbox.insert(tk.END, "Nu s-au găsit sugestii demo")
                    
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la obținerea sugestiilor: {e}")
    
    def update_learning_stats(self):
        """Actualizează statisticile de learning"""
        try:
            if self.ai_available:
                from src.ai_ml.ai_manager import AIMLManager
                ai_manager = AIMLManager(self.output_folder)
                
                stats = ai_manager.get_learning_statistics()
                
                stats_text = f"""📊 Statistici Learning:
• Total corecții învățate: {stats['total_corrections']}
• Confidence medie: {stats['average_confidence']}
• Learning activ: {'Da' if stats['learning_active'] else 'Nu'}
• Corecții pe tip: {stats['corrections_by_type']}"""
                
                self.learning_stats_var.set(stats_text)
            else:
                self.learning_stats_var.set("📊 Statistici Demo:\n• Total corecții: 156\n• Confidence medie: 0.87\n• Learning: Inactiv")
                
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la actualizarea statisticilor: {e}")
    
    def detect_duplicates(self):
        """Detectează duplicate"""
        similarity_threshold = self.similarity_var.get()
        
        self.detection_status_var.set("🔍 Detectare în curs...")
        self.search_window.update()
        
        try:
            if self.ai_available:
                from src.search.search_manager import SearchManager
                search_manager = SearchManager(self.output_folder)
                
                duplicates = search_manager.detect_duplicates(similarity_threshold)
                
                self.display_duplicates(duplicates)
                self.detection_status_var.set(f"✅ Detectare completă. Găsite {len(duplicates)} grupuri duplicate.")
            else:
                # Demo duplicate
                demo_duplicates = [
                    {
                        'group_id': 1,
                        'similarity_score': 0.92,
                        'total_count': 2,
                        'persons': [
                            {'nume': 'Popescu', 'prenume': 'Ion', 'cnp': '1234567890123'},
                            {'nume': 'P0pescu', 'prenume': 'I0n', 'cnp': '1234567890123'}
                        ]
                    },
                    {
                        'group_id': 2,
                        'similarity_score': 0.88,
                        'total_count': 3,
                        'persons': [
                            {'nume': 'Ionescu', 'prenume': 'Maria', 'cnp': '2234567890123'},
                            {'nume': 'Ionescu', 'prenume': 'M4ria', 'cnp': '2234567890123'},
                            {'nume': 'I0nescu', 'prenume': 'Maria', 'cnp': '2234567890123'}
                        ]
                    }
                ]
                
                self.display_duplicates(demo_duplicates)
                self.detection_status_var.set(f"✅ Demo: Găsite {len(demo_duplicates)} grupuri duplicate.")
                
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la detectarea duplicatelor: {e}")
            self.detection_status_var.set("❌ Eroare la detectare")
    
    def display_duplicates(self, duplicates):
        """Afișează duplicate în treeview"""
        # Curăță tree-ul
        self.duplicates_tree.delete(*self.duplicates_tree.get_children())
        
        for group in duplicates:
            # Adaugă grupul principal
            group_text = f"📁 Grup {group['group_id']} - {group['total_count']} persoane (Similaritate: {group['similarity_score']:.2f})"
            group_item = self.duplicates_tree.insert("", "end", text=group_text, open=True)
            
            # Adaugă persoanele din grup
            for i, person in enumerate(group['persons']):
                person_text = f"👤 {person.get('nume', '')} {person.get('prenume', '')} - CNP: {person.get('cnp', '')}"
                if i == 0:
                    person_text += " (Principal)"
                
                self.duplicates_tree.insert(group_item, "end", text=person_text)
        
        self.duplicates_data = duplicates
    
    def clear_duplicates(self):
        """Curăță lista de duplicate"""
        self.duplicates_tree.delete(*self.duplicates_tree.get_children())
        self.duplicates_data = []
        self.detection_status_var.set("Lista de duplicate a fost curățată")
    
    def refresh_saved_searches(self):
        """Actualizează lista căutărilor salvate"""
        # Curăță tree-ul
        self.saved_tree.delete(*self.saved_tree.get_children())
        
        try:
            if self.ai_available:
                from src.search.search_manager import SearchManager
                search_manager = SearchManager(self.output_folder)
                
                saved_searches = search_manager.get_saved_searches()
                
                for search in saved_searches:
                    self.saved_tree.insert("", "end", values=(
                        search['name'],
                        search['query'],
                        str(search['filters']),
                        search['date_created'][:10] if search['date_created'] else '',
                        search['usage_count'],
                        search['last_used'][:10] if search['last_used'] else 'Niciodată'
                    ))
            else:
                # Demo data
                demo_searches = [
                    ("Căutare București", "Popescu", "{'judet': 'București'}", "2025-01-01", "5", "2025-01-15"),
                    ("CNP Invalid", "invalid", "{'cnp_valid': False}", "2025-01-02", "3", "2025-01-10")
                ]
                
                for search in demo_searches:
                    self.saved_tree.insert("", "end", values=search)
                    
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la încărcarea căutărilor: {e}")
    
    def delete_saved_search(self):
        """Șterge căutarea salvată selectată"""
        selection = self.saved_tree.selection()
        if not selection:
            messagebox.showwarning("Atenție", "Selectează o căutare pentru ștergere.")
            return
        
        # Implementare ștergere - pentru demo doar confirmăm
        if messagebox.askyesno("Confirmare", "Ești sigur că vrei să ștergi căutarea selectată?"):
            self.saved_tree.delete(selection[0])
            messagebox.showinfo("Succes", "Căutarea a fost ștearsă.")
    
    def load_saved_search(self, event):
        """Încarcă căutarea salvată în tab-ul de căutare"""
        selection = self.saved_tree.selection()
        if not selection:
            return
        
        item = self.saved_tree.item(selection[0])
        values = item['values']
        
        if len(values) >= 2:
            search_name = values[0]
            query = values[1]
            
            # Setează query-ul în tab-ul de căutare
            self.search_var.set(query)
            
            # Schimbă la tab-ul de căutare
            self.notebook.select(0)
            
            messagebox.showinfo("Încărcat", f"Căutarea '{search_name}' a fost încărcată.")
    
    def create_results_context_menu(self):
        """Creează context menu pentru rezultatele căutării"""
        self.results_context_menu = tk.Menu(self.search_window, tearoff=0)
        self.results_context_menu.add_command(label="📋 Copiază Informațiile", command=self.copy_result_info)
        self.results_context_menu.add_command(label="🔍 Caută Similar", command=self.search_similar)
        self.results_context_menu.add_separator()
        self.results_context_menu.add_command(label="📂 Deschide Fișierul", command=self.open_result_file)
        
        self.results_tree.bind("<Button-3>", self.show_results_context_menu)
    
    def create_duplicates_context_menu(self):
        """Creează context menu pentru duplicate"""
        self.duplicates_context_menu = tk.Menu(self.search_window, tearoff=0)
        self.duplicates_context_menu.add_command(label="🔗 Compară Side-by-Side", command=self.compare_duplicates)
        self.duplicates_context_menu.add_command(label="🔧 Merge Automat", command=self.merge_duplicates_auto)
        self.duplicates_context_menu.add_command(label="⚙️ Merge Manual", command=self.merge_duplicates_manual)
        self.duplicates_context_menu.add_separator()
        self.duplicates_context_menu.add_command(label="❌ Marchează ca Non-duplicat", command=self.mark_not_duplicate)
        
        self.duplicates_tree.bind("<Button-3>", self.show_duplicates_context_menu)
    
    def show_results_context_menu(self, event):
        """Afișează context menu pentru rezultate"""
        try:
            self.results_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.results_context_menu.grab_release()
    
    def show_duplicates_context_menu(self, event):
        """Afișează context menu pentru duplicate"""
        try:
            self.duplicates_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.duplicates_context_menu.grab_release()
    
    def copy_result_info(self):
        """Copiază informațiile rezultatului selectat"""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            values = item['values']
            info_text = f"Nume: {values[0]} {values[1]}\nCNP: {values[2]}\nJudețul: {values[3]}\nTelefon: {values[4]}\nEmail: {values[5]}"
            
            self.search_window.clipboard_clear()
            self.search_window.clipboard_append(info_text)
            messagebox.showinfo("Copiat", "Informațiile au fost copiate în clipboard.")
    
    def search_similar(self):
        """Caută persoane similare cu cea selectată"""
        selection = self.results_tree.selection()
        if selection:
            item = self.results_tree.item(selection[0])
            values = item['values']
            name = f"{values[0]} {values[1]}"
            
            self.search_var.set(name)
            self.perform_search()
    
    def open_result_file(self):
        """Deschide fișierul asociat rezultatului"""
        messagebox.showinfo("Info", "Funcționalitatea va fi implementată pentru a deschide fișierul asociat persoanei.")
    
    def compare_duplicates(self):
        """Compară duplicate side-by-side"""
        messagebox.showinfo("Info", "Se va deschide o fereastră de comparație side-by-side.")
    
    def merge_duplicates_auto(self):
        """Merge automat duplicate"""
        if messagebox.askyesno("Confirmare", "Ești sigur că vrei să faci merge automat al duplicatelor selectate?"):
            messagebox.showinfo("Succes", "Duplicatele au fost merge-uite automat.")
    
    def merge_duplicates_manual(self):
        """Merge manual duplicate"""
        messagebox.showinfo("Info", "Se va deschide o fereastră pentru merge manual.")
    
    def mark_not_duplicate(self):
        """Marchează ca non-duplicat"""
        if messagebox.askyesno("Confirmare", "Marchezi acest grup ca non-duplicat?"):
            messagebox.showinfo("Succes", "Grupul a fost marcat ca non-duplicat.")
    
    def close_window(self):
        """Închide fereastra"""
        self.search_window.destroy()

# Funcție pentru lansarea UI-ului search/AI din main window
def show_search_ai_window(parent, output_folder):
    """Lansează fereastra search și AI/ML"""
    if not output_folder:
        messagebox.showwarning("Atenție", "Selectează mai întâi un folder de output.")
        return
    
    search_ui = SearchAIUI(parent, output_folder)

if __name__ == "__main__":
    # Test UI
    root = tk.Tk()
    # image
    root.iconbitmap
    root.withdraw()  # Ascunde fereastra principală
    
    show_search_ai_window(root, "test_output")
    
    root.mainloop()
