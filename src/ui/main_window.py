from pathlib import Path
import webbrowser
from tkinter import Tk, Canvas, Button, PhotoImage
from tkinter import filedialog
import os
from src.ocr.ocr import run_processing_threaded, is_processing_active, stop_current_processing
from src.ui.splash import show_splash
from ..processing.coordonate import coordonate
from tkinter.ttk import Progressbar
from tkinter import messagebox
from tkinter import ttk
import time
import scipy

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets"
PDF_PATH = OUTPUT_PATH / "assets"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def run_main_window():
    folder_input = ""
    folder_output = ""
    root = Tk()
    def create_main_window(root):
        # Obținem dimensiunile ecranului corect
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Dimensiunile ferestrei (modifică după nevoie)
        window_width = 800
        window_height = 600

        # Calculăm poziția pentru centrare
        win_pos_right = (screen_width // 2) - (window_width // 2)
        win_pos_down = (screen_height // 2) - (window_height // 2)

        # Setăm dimensiunea și poziția ferestrei
        root.geometry(f"{window_width}x{window_height}+{win_pos_right}+{win_pos_down}")
        root.deiconify()
        root.title("OCR230")  # Setăm titlul ferestrei
        root.geometry("800x600")
        root.configure(bg="#D9D9D9")
        # Fundal și icon
        icon_path = Path(__file__).parent.parent.parent / "Assets" / "favicon.ico"
        root.iconbitmap(str(icon_path))
        # Funcție pentru închidere corectă a aplicației
        def on_close():
            root.quit()   # Oprește event loop-ul Tkinter
            root.destroy()  # Distruge fereastra principală
            exit()  # Închide complet aplicația
        
        # Leagă funcția de închidere de evenimentul de închidere al ferestrei
        root.protocol("WM_DELETE_WINDOW", on_close)

    # root.title("F230-OCR")
    # root.iconbitmap('Assets/favicon.ico')
    # root.geometry("800x600")
    # root.configure(bg="#D9D9D9")

    canvas = Canvas(
        root,
        bg="#FFFFFF",
        height=600,
        width=800,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )

    canvas.place(x=0, y=0)
    canvas.create_rectangle(
        0.0,
        0.0,
        800.0,
        600.0,
        fill="#D9D9D9",
        outline="")

    # Imagine pentru butonul Ajutor
    button_image_ajutor = PhotoImage(file=relative_to_assets("button_ajutor.png"))

    # Funcția de ajutor
    def open_guide():
        guide_path = PDF_PATH / "guide.pdf"
        webbrowser.open(guide_path.as_uri())

    Button_ajutor = Button(
        image=button_image_ajutor,
        borderwidth=0,
        highlightthickness=0,
        command=open_guide,
        relief="flat",
        activebackground="#D9D9D9",
        background="#D9D9D9"
    )
    Button_ajutor.place(
        x=723.0,
        y=567.0,
        width=61.0,
        height=26.012451171875
    )

    canvas.create_rectangle(
        -4.0,
        558.0,
        800.0,
        562.0,
        fill="#C4C4C4",
        outline="")

    canvas.create_text(
        323.0,
        571.0,
        anchor="nw",
        text="™ F230-OCR",
        fill="#000000",
        font=("Inter", 14 * -1)
    )

    canvas.create_text(
        14.0,
        571.0,
        anchor="nw",
        text="©2025 Rareș Anghel",
        fill="#000000",
        font=("Inter", 14 * -1)
    )

    canvas.create_text(
        320.0,
        18.0,
        anchor="nw",
        text="F230-OCR",
        fill="#000000",
        font=("Inter", 32 * -1)
    )

    image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
    image_1 = canvas.create_image(
        55.0,
        108.0,
        image=image_image_1
    )

    canvas.create_rectangle(
        23.0,
        215.0,
        778.0,
        271.0,
        fill="#D9D9D9",
        outline="")

    image_image_2 = PhotoImage(file=relative_to_assets("image_2.png"))
    image_2 = canvas.create_image(
        400.0,
        300.0,
        image=image_image_2
    )

    # Păstrăm imaginile 3 și 4
    image_image_3 = PhotoImage(file=relative_to_assets("image_3.png"))
    image_3 = canvas.create_image(
        397.0,
        290.0,
        image=image_image_3
    )

    image_image_4 = PhotoImage(file=relative_to_assets("image_4.png"))
    image_4 = canvas.create_image(
        397.0,
        159.0,
        image=image_image_4
    )

    # Text pentru mesajul că nu s-a selectat folderul de intrare
    entry_folder_text = canvas.create_text(
        297.0,
        150.0,
        anchor="nw",
        text="Nu ai selectat niciun folder",
        fill="#000000",
        font=("Inter", 16 * -1)
    )

    # Text pentru mesajul că nu s-a selectat folderul de ieșire
    output_folder_text = canvas.create_text(
        298.0,
        281.0,
        anchor="nw",
        text="Nu ai selectat niciun folder",
        fill="#000000",
        font=("Inter", 16 * -1)
    )

    # Funcție pentru selectarea folderului de intrare
    def select_input_folder():
        nonlocal folder_input
        input_folder = filedialog.askdirectory()  # Deschide dialogul de selectare a folderului
        if input_folder:
            folder_name_input = os.path.basename(input_folder)  # Extrage doar numele folderului
            canvas.itemconfig(entry_folder_text, text=folder_name_input)  # Modifică textul
            canvas.coords(entry_folder_text, canvas.winfo_width() / 2, canvas.coords(entry_folder_text)[1])  # Centrează pe X
            folder_input = input_folder  # Actualizează folder_input cu calea completă a folderului
        else:
            canvas.itemconfig(entry_folder_text, text="Nu ai selectat niciun folder")
            #canvas.coords(entry_folder_text, canvas.winfo_width() / 2, canvas.coords(entry_folder_text)[1])  # Centrează pe X

    # Funcție pentru selectarea folderului de ieșire
    def select_output_folder():
        nonlocal folder_output
        output_folder = filedialog.askdirectory()  # Deschide dialogul de selectare a folderului
        if output_folder:
            folder_name_output = os.path.basename(output_folder)  # Extrage doar numele folderului
            canvas.itemconfig(output_folder_text, text=folder_name_output)  # Modifică textul
            canvas.coords(output_folder_text, canvas.winfo_width() / 2, canvas.coords(output_folder_text)[1])  # Centrează pe X
            folder_output = output_folder  # Actualizează folder_output cu calea completă a folderului
        else:
            canvas.itemconfig(output_folder_text, text="Nu ai selectat niciun folder")
            #canvas.coords(output_folder_text, canvas.winfo_width() / 2, canvas.coords(output_folder_text)[1])  # Centrează pe X

    # Imagine pentru butonul de ieșire (Button_output)
    button_image_output = PhotoImage(file=relative_to_assets("button_output.png"))
    Button_output = Button(
        image=button_image_output,
        borderwidth=0,
        highlightthickness=0,
        command=select_output_folder,
        relief="flat",
        activebackground="#D9D9D9",
        background="#D9D9D9"
    )
    Button_output.place(
        x=25.0,
        y=218.0,
        width=749.0,
        height=45.0
    )

    # Imagine pentru butonul de intrare (Button_input)
    button_image_input = PhotoImage(file=relative_to_assets("button_input.png"))
    Button_input = Button(
        image=button_image_input,
        borderwidth=0,
        highlightthickness=0,
        command=select_input_folder,
        relief="flat",
        activebackground="#D9D9D9",
        background="#D9D9D9"
    )
    Button_input.place(
        x=22.0,
        y=84.0,
        width=755.0,
        height=56.0
    )
    # Imagine pentru butonul de accelerație grafică (Button5)
    button_image_5 = PhotoImage(file=relative_to_assets("button_5_on.png"))
    button_image_5_off = PhotoImage(file=relative_to_assets("button_5_off.png"))

    # Global variable to keep track of the button state
    button_5_state = True

    def toggle_button_5():
        nonlocal button_5_state  # Refer to the global button_5_state
        if button_5_state:
            button_5.config(image=button_image_5_off)
            button_5_state = False
            # print("Buton accelerație grafică dezactivat")
        else:
            button_5.config(image=button_image_5)
            button_5_state = True
            # print("Buton accelerație grafică activat")

    # Imagine pentru butonul de accelerație grafică (Button5)
    button_5 = Button(
        image=button_image_5,
        borderwidth=0,
        highlightthickness=0,
        command=toggle_button_5,
        relief="flat",
        activebackground="#D9D9D9",
        background="#D9D9D9"
    )
    button_5.place(
        x=470.0,
        y=490.0,  # Mutat cu 20px mai jos (480 + 20)
        width=42.0,
        height=28.0
    )

    # Funcție pentru actualizarea stării butonului
    def update_button_state(is_processing):
        """Actualizează imaginea butonului în funcție de starea de procesare"""
        if is_processing:
            Button_start.config(image=button_image_stop)
        else:
            Button_start.config(image=button_image_start)

    def start_processing():
        # Verificăm dacă procesarea este deja activă
        if is_processing_active():
            # Oprim procesarea
            stop_current_processing()
            # Resetăm butonul imediat
            Button_start.config(image=button_image_start)
            # Ascundem dashboard-ul
            hide_dashboard()
            print("Procesarea a fost oprită de utilizator.")
            return
        
        # Verifică dacă folderul de intrare este selectat
        if not folder_input:
            messagebox.showwarning("Atenție", "Te rugăm să selectezi un folder de intrare.")

        # Verifică dacă folderul de ieșire este selectat
        elif not folder_output:
            messagebox.showwarning("Atenție", "Te rugăm să selectezi un folder de ieșire.")
            
        # Dacă ambele foldere sunt selectate, rulează procesarea
        else:
            # Resetăm și afișăm dashboard-ul
            reset_dashboard()
            show_dashboard()
            
            # Calculăm numărul total de fișiere pentru dashboard
            import os
            files = [f for f in os.listdir(folder_input) if f.lower().endswith(('jpg', 'jpeg', 'png', 'pdf'))]
            update_dashboard_stats('total_files', len(files))
            update_dashboard_stats('start_time', time.time())
            
            # Rulăm procesarea în thread separat cu callback pentru dashboard
            run_processing_threaded(button_5_state, progress_bar, folder_input, folder_output, coordonate, reset_progress, root, update_button_state, update_dashboard_stats)
    # Imagine pentru butonul Start (Button_start)
    button_image_start = PhotoImage(file=relative_to_assets("button_start.png"))
    # Pentru butonul Stop, folosim aceeași imagine (poate fi înlocuită cu o imagine specifică)
    button_image_stop = button_image_start  # Momentan folosim aceeași imagine
        
    Button_start = Button(
        image=button_image_start,
        borderwidth=0,
        highlightthickness=0,
        command=start_processing,
        relief="flat",
        activebackground="#D9D9D9",
        background="#D9D9D9"
    )
    Button_start.place(
        x=28.0,
        y=445.0, 
        width=746.0,
        height=46.0
    )
    
    progress_bar = None
    # Definirea Progress Bar-ului
    def create_custom_progress_bar(root):
        # Creăm un container pentru progresul nostru pentru un efect vizual mai plăcut
        progress_container = Canvas(root, bg="#D9D9D9", width=744, height=20, bd=0, highlightthickness=0, relief="flat")
        progress_container.place(x=28, y=520)  # Poziționăm progresul cu 20px mai jos (500 + 20)

        # Bara de progres personalizată
        progress_bar = Progressbar(progress_container, orient="horizontal", length=744, mode="determinate", 
                                    style="TProgressbar")
        progress_bar.place(x=0, y=0)

        # Schimbăm stilul pentru Progressbar (culori și borduri)
        style = ttk.Style()
        style.configure("TProgressbar",
                        thickness=15,  # Grosimea progresului
                        troughcolor="#E6E6E6",  # Culoarea fundalului barei
                        background="#3DA5D9",  # Culoarea barei de progres
                        )

        return progress_bar
    progress_bar = create_custom_progress_bar(root)

    def smooth_progress(progress_bar, current, total, step_delay=50):
        current_value = progress_bar['value']  # Păstrăm valoarea curentă a progresului
        step_size = 1  # Cât de mult să crească progresul la fiecare pas

        def update_progress_smoothly():
            nonlocal current_value
            if current_value < total:
                current_value += step_size  # Creștem progresul cu pasul definit
                if current_value > total:  # Evităm să depășim valoarea totală
                    current_value = total
                progress_bar['value'] = (current_value / total) * 100  # Actualizăm progresul în procente
                root.update_idletasks()  # Forțăm actualizarea interfeței
                root.after(step_delay, update_progress_smoothly)  # Întârziere înainte de actualizare următoare

        # Începem actualizarea progresului lin
        update_progress_smoothly()
        
    # Funcție pentru resetarea progresului
    def reset_progress():
        """Reset the progress bar to 0% in a smooth and gradual manner."""
        current_value = progress_bar['value']  # Păstrăm valoarea curentă
        step_delay = 20  # Întârzierea în milisecunde între fiecare pas
        step_size = 1  # Cât de mult să scadă progresul la fiecare pas

        # Actualizăm progresul pas cu pas
        while current_value > 0:
            current_value -= step_size  # Reducem progresul cu pasul definit
            if current_value < 0:  # Evităm să scadă sub 0
                current_value = 0
            progress_bar['value'] = current_value  # Actualizăm progresul
            root.update_idletasks()  # Actualizăm interfața
            time.sleep(step_delay / 1000)  # Pauză pentru efect de tranziție lină

        # Asigurăm că progresul este exact 0 după tranziție
        progress_bar['value'] = 0
        
        # Resetăm butonul la starea inițială (Start)
        Button_start.config(image=button_image_start)

    canvas.create_text(
        277.0,
        495.0,
        anchor="nw",
        text="Folosire accelerație grafică",
        fill="#1E1E1E",
        font=("Inter", 16 * -1)
    )

    # ==================== DASHBOARD LIVE ====================
    # Variabile pentru statistici live
    dashboard_stats = {
        'total_files': 0,
        'processed_files': 0,
        'valid_cnp': 0,
        'invalid_cnp': 0,
        'duplicates_found': 0,
        'current_file': '',
        'processing_speed': 0.0,
        'estimated_time_left': 0,
        'start_time': None
    }
    
    dashboard_widgets = {}
    dashboard_frame = None  # Variabilă globală pentru dashboard
    
    def create_live_dashboard(root):
        """Creează dashboard-ul cu statistici live"""
        nonlocal dashboard_frame
        # Container pentru dashboard (mutat mai sus, între folder selection și buton Start)
        dashboard_frame = Canvas(root, bg="#F0F0F0", width=744, height=120, bd=2, relief="solid")
        dashboard_frame.place(x=28, y=310)  # Mutat cu 20px mai jos (290 + 20)
        
        # Titlu dashboard
        dashboard_frame.create_text(372, 15, text="📊 Statistici Live", font=("Inter", 14, "bold"), fill="#2C3E50")
        
        # Linia de separare
        dashboard_frame.create_line(50, 25, 694, 25, fill="#BDC3C7", width=1)
        
        # Coloana 1 - Progres general
        dashboard_frame.create_text(120, 40, text="📋 Progres General", font=("Inter", 10, "bold"), fill="#34495E")
        dashboard_widgets['files_label'] = dashboard_frame.create_text(120, 55, text="Fișiere: 0/0", font=("Inter", 9), fill="#2C3E50")
        dashboard_widgets['speed_label'] = dashboard_frame.create_text(120, 70, text="Viteză: 0.0 fișiere/min", font=("Inter", 9), fill="#2C3E50")
        dashboard_widgets['eta_label'] = dashboard_frame.create_text(120, 85, text="Timp rămas: --", font=("Inter", 9), fill="#2C3E50")
        
        # Coloana 2 - Validare date
        dashboard_frame.create_text(372, 40, text="✅ Validare Date", font=("Inter", 10, "bold"), fill="#34495E")
        dashboard_widgets['cnp_valid_label'] = dashboard_frame.create_text(372, 55, text="CNP valide: 0", font=("Inter", 9), fill="#27AE60")
        dashboard_widgets['cnp_invalid_label'] = dashboard_frame.create_text(372, 70, text="CNP invalide: 0", font=("Inter", 9), fill="#E74C3C")
        dashboard_widgets['duplicates_label'] = dashboard_frame.create_text(372, 85, text="Duplicate: 0", font=("Inter", 9), fill="#F39C12")
        
        # Coloana 3 - Fișier curent
        dashboard_frame.create_text(600, 40, text="📄 Fișier Curent", font=("Inter", 10, "bold"), fill="#34495E")
        dashboard_widgets['current_file_label'] = dashboard_frame.create_text(600, 60, text="În așteptare...", font=("Inter", 8), fill="#7F8C8D", width=200)
        
        return dashboard_frame
    
    def update_dashboard_stats(stat_name, value):
        """Actualizează o statistică în dashboard"""
        print(f"CALLBACK DASHBOARD: {stat_name} = {value}")  # Debug îmbunătățit
        if stat_name in dashboard_stats:
            old_value = dashboard_stats[stat_name]
            dashboard_stats[stat_name] = value
            print(f"Statistică salvată: {stat_name} = {old_value} -> {dashboard_stats[stat_name]}")
            
            # Debug special pentru fișierul curent
            if stat_name == 'current_file':
                print(f"SPECIAL DEBUG - Fișier curent actualizat: '{value}'")
                print(f"SPECIAL DEBUG - Valoare salvată în dashboard_stats: '{dashboard_stats['current_file']}'")
            
            # Forțăm actualizarea în thread-ul principal pentru UI
            root.after(0, refresh_dashboard)
        else:
            print(f"EROARE: Statistică necunoscută: {stat_name}")
            print(f"Statistici disponibile: {list(dashboard_stats.keys())}")
    
    def refresh_dashboard():
        """Actualizează toate widget-urile din dashboard cu datele curente"""
        if not dashboard_widgets or not dashboard_frame:
            print("Dashboard widgets sau frame nu sunt disponibile")
            return
            
        try:
            # Calculăm statistici derivate
            if dashboard_stats['start_time'] and dashboard_stats['processed_files'] > 0:
                elapsed_time = time.time() - dashboard_stats['start_time']
                dashboard_stats['processing_speed'] = (dashboard_stats['processed_files'] / elapsed_time) * 60  # fișiere/min
                
                if dashboard_stats['processing_speed'] > 0:
                    remaining_files = dashboard_stats['total_files'] - dashboard_stats['processed_files']
                    dashboard_stats['estimated_time_left'] = remaining_files / (dashboard_stats['processing_speed'] / 60)  # secunde
            
            # Actualizăm label-urile direct pe dashboard_frame
            dashboard_frame.itemconfig(
                dashboard_widgets['files_label'], 
                text=f"Fișiere: {dashboard_stats['processed_files']}/{dashboard_stats['total_files']}"
            )
            
            # Format pentru viteză
            speed_text = f"Viteză: {dashboard_stats['processing_speed']:.1f} fișiere/min"
            dashboard_frame.itemconfig(
                dashboard_widgets['speed_label'], 
                text=speed_text
            )
            
            # Format pentru timp rămas
            eta = dashboard_stats['estimated_time_left']
            if eta > 0:
                if eta > 3600:  # > 1 oră
                    eta_text = f"Timp rămas: {eta/3600:.1f}h"
                elif eta > 60:  # > 1 minut
                    eta_text = f"Timp rămas: {eta/60:.1f}min"
                else:
                    eta_text = f"Timp rămas: {eta:.0f}s"
            else:
                eta_text = "Timp rămas: --"
            
            dashboard_frame.itemconfig(
                dashboard_widgets['eta_label'], 
                text=eta_text
            )
            
            # Actualizăm validarea datelor
            dashboard_frame.itemconfig(
                dashboard_widgets['cnp_valid_label'], 
                text=f"CNP valide: {dashboard_stats['valid_cnp']}"
            )
            
            dashboard_frame.itemconfig(
                dashboard_widgets['cnp_invalid_label'], 
                text=f"CNP invalide: {dashboard_stats['invalid_cnp']}"
            )
            
            dashboard_frame.itemconfig(
                dashboard_widgets['duplicates_label'], 
                text=f"Duplicate: {dashboard_stats['duplicates_found']}"
            )
            
            # Actualizăm fișierul curent
            current_file = dashboard_stats['current_file']
            print(f"REFRESH DASHBOARD DEBUG - current_file din stats: '{current_file}'")
            if current_file:  # Verificăm dacă există un fișier curent
                if len(current_file) > 30:
                    current_file = "..." + current_file[-27:]
                print(f"REFRESH DASHBOARD DEBUG - Actualizez cu: '{current_file}'")
                dashboard_frame.itemconfig(
                    dashboard_widgets['current_file_label'], 
                    text=current_file
                )
            else:
                print("REFRESH DASHBOARD DEBUG - Nu există fișier curent, afișez 'În așteptare...'")
                dashboard_frame.itemconfig(
                    dashboard_widgets['current_file_label'], 
                    text="În așteptare..."
                )
            
            # Forțăm actualizarea interfeței
            root.update_idletasks()
            
            print(f"DASHBOARD ACTUALIZAT COMPLET: {dashboard_stats['processed_files']}/{dashboard_stats['total_files']}, "
                  f"CNP: {dashboard_stats['valid_cnp']}/{dashboard_stats['invalid_cnp']}, "
                  f"Fișier: {dashboard_stats['current_file']}")
            
        except Exception as e:
            print(f"EROARE la actualizarea dashboard-ului: {e}")
            import traceback
            traceback.print_exc()
    
    def reset_dashboard():
        """Resetează statisticile dashboard-ului"""
        dashboard_stats.update({
            'total_files': 0,
            'processed_files': 0,
            'valid_cnp': 0,
            'invalid_cnp': 0,
            'duplicates_found': 0,
            'current_file': '',
            'processing_speed': 0.0,
            'estimated_time_left': 0,
            'start_time': None
        })
        refresh_dashboard()
    
    def hide_dashboard():
        """Ascunde dashboard-ul"""
        if dashboard_frame:
            dashboard_frame.place_forget()
    
    def show_dashboard():
        """Afișează dashboard-ul"""
        if dashboard_frame:
            dashboard_frame.place(x=28, y=310)
    
    # Creăm dashboard-ul (inițial ascuns)
    dashboard_frame = create_live_dashboard(root)
    hide_dashboard()  # Ascundem inițial dashboard-ul

    root.withdraw()
    show_splash(root, create_main_window)
    root.mainloop()
