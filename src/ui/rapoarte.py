from pathlib import Path
import os
from tkinter import Canvas, Button, PhotoImage, Toplevel
import webbrowser

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("assets")
PDF_PATH = OUTPUT_PATH / "assets"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def show_rapoarte_window(output_folder=None, continue_callback=None):
    # Permite transmiterea root pentru închidere corectă
    import tkinter as tk
    parent_root = None
    if hasattr(show_rapoarte_window, "_root"):
        parent_root = show_rapoarte_window._root
    window = Toplevel()
    window.geometry("800x600")
    window.configure(bg = "#D9D9D9")
    window.title("OCR230 - Rapoarte")
    window.resizable(False, False)
    # window logo
    icon_path = Path(__file__).parent.parent.parent / "Assets" / "favicon.ico"
    try:
        window.iconbitmap(str(icon_path))
    except Exception:
        pass
    # Facem fereastra modală
    window.transient()
    window.grab_set()
    window.focus_set()
    # Centrăm fereastra
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (800 // 2)
    y = (window.winfo_screenheight() // 2) - (600 // 2)
    window.geometry(f"800x600+{x}+{y}")

    def send_report_via_email():
        """Trimite rapoartele pe email (PDF/Excel/CSV)"""
        from tkinter import simpledialog, messagebox
        from src.utils.email_report import send_report_email
        sender = simpledialog.askstring("Email Expeditor", "Adresa ta de email (Gmail):", parent=window)
        password = simpledialog.askstring("Parola/APP Password Gmail", "Parola sau App Password Gmail:", parent=window, show='*')
        recipient = simpledialog.askstring("Email Destinatar", "Adresa destinatarului:", parent=window)
        if not sender or not password or not recipient:
            messagebox.showwarning("Info", "Completează toate câmpurile pentru trimitere email.", parent=window)
            return
        subject = "Raport automat OCR230"
        body = "Găsiți atașat raportul generat automat."
        attachments = []
        # Caută fișierele PDF/Excel/CSV din output_folder
        for ext in ["pdf", "xlsx", "csv"]:
            for fname in os.listdir(output_folder):
                if fname.lower().endswith(ext):
                    attachments.append(os.path.join(output_folder, fname))
        if not attachments:
            messagebox.showwarning("Info", "Nu s-au găsit fișiere PDF/Excel/CSV pentru atașare.", parent=window)
            return
        ok = send_report_email(sender, password, recipient, subject, body, attachments)
        if ok:
            messagebox.showinfo("Succes", f"Email trimis către {recipient}", parent=window)
        else:
            messagebox.showerror("Eroare", "Trimiterea emailului a eșuat.", parent=window)

    # Calculăm statisticile din Excel dacă avem folderul
    stats = calculate_stats_from_excel(output_folder) if output_folder else None

    def on_close():
        window.destroy()
        if parent_root:
            parent_root.quit()
    def close_window():
        on_close()

    def continue_to_results():
        """Închide fereastra de rapoarte și continuă cu deschiderea folderului și Excel-ului"""
        close_window()
        # Apelăm callback-ul pentru a continua cu deschiderea folderului și Excel-ului
        if continue_callback:
            continue_callback()

    canvas = Canvas(
        window,
        bg = "#D9D9D9",
        height = 600,
        width = 800,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )

    canvas.place(x = 0, y = 0)
    canvas.create_rectangle(
        0.0,
        0.0,
        800.0,
        600.0,
        fill="#D9D9D9",
        outline="")

    try:
        image_image_1 = PhotoImage(
            file=relative_to_assets("image_2.png"))
        image_1 = canvas.create_image(
            400.0,
            300.0,
            image=image_image_1
        )
    except:
        # Dacă imaginea nu există, creăm un placeholder
        pass

    canvas.create_rectangle(
        -4.0,
        558.0,
        800.0,
        562.0,
        fill="#C4C4C4",
        outline="")

    canvas.create_text(
        251.0,
        572.0,
        anchor="nw",
        text="™ OCR230",
        fill="#000000",
        font=("Inter", 14 * -1)
    )
    canvas.create_text(
        487.0,
        572.0,
        anchor="nw",
        text="ver. 2.6",
        fill="#000000",
        font=("Inter", 14 * -1)
    )

    canvas.create_text(
        15.0,
        572.0,
        anchor="nw",
        text="©2025 Rareș Anghel",
        fill="#000000",
        font=("Inter", 14 * -1)
    )

    canvas.create_text(
        336.0,
        17.0,
        anchor="nw",
        text="OCR230",
        fill="#000000",
        font=("Inter", 32 * -1)
    )

    canvas.create_text(
        330.0,
        59.0,
        anchor="nw",
        text="Rapoarte",
        fill="#000000",
        font=("Inter", 32 * -1)
    )

    # Afișăm statisticile calculate
    if stats:
        # Perioada de distribuire
        canvas.create_text(
            44.0,
            101.0,
            anchor="nw",
            text="Perioada de distribuire",
            fill="#000000",
            font=("Inter", 24 * -1)
        )
        
        canvas.create_text(
            56.0,
            139.0,
            anchor="nw",
            text=f"1 an\n2 ani",
            fill="#000000",
            font=("Inter", 24 * -1)
        )
        
        canvas.create_text(
            121.0,
            139.0,
            anchor="nw",
            text="-\n-",
            fill="#000000",
            font=("Inter", 24 * -1)
        )
        
        canvas.create_text(
            138.0,
            139.0,
            anchor="nw",
            text=f"{stats['one_year']} formulare\n{stats['two_years']} formulare",
            fill="#000000",
            font=("Inter", 24 * -1)
        )

        # Total formulare
        canvas.create_text(
            44.0,
            215.0,
            anchor="nw",
            text=f"Total - {stats['total']} formulare",
            fill="#000000",
            font=("Inter", 24 * -1)
        )

        # Top județe
        canvas.create_text(
            44.0,
            271.0,
            anchor="nw",
            text="Cele mai multe formulare sunt în:",
            fill="#000000",
            font=("Inter", 24 * -1)
        )

        top_text = ""
        for i, (judet, count) in enumerate(stats['top_judete'][:3], 1):
            top_text += f"{i}. {judet} - {count} \n"
        
        canvas.create_text(
            56.0,
            301.0,
            anchor="nw",
            text=top_text.strip(),
            fill="#000000",
            font=("Inter", 24 * -1)
        )
    else:
        # Afișare implicită dacă nu avem statistici
        canvas.create_text(
            44.0,
            101.0,
            anchor="nw",
            text="Perioada de distribuire",
            fill="#000000",
            font=("Inter", 24 * -1)
        )
        
        canvas.create_text(
            56.0,
            139.0,
            anchor="nw",
            text="1 an   \n2 ani",
            fill="#000000",
            font=("Inter", 24 * -1)
        )

        canvas.create_text(
            138.0,
            139.0,
            anchor="nw",
            text="0 formulare\n0 formulare",
            fill="#000000",
            font=("Inter", 24 * -1)
        )

        canvas.create_text(
            121.0,
            139.0,
            anchor="nw",
            text="-\n-",
            fill="#000000",
            font=("Inter", 24 * -1)
        )

        canvas.create_text(
            44.0,
            215.0,
            anchor="nw",
            text="Total - 0 formulare",
            fill="#000000",
            font=("Inter", 24 * -1)
        )

        canvas.create_text(
            44.0,
            271.0,
            anchor="nw",
            text="Cele mai multe formulare sunt în:",
            fill="#000000",
            font=("Inter", 24 * -1)
        )

        canvas.create_text(
            56.0,
            301.0,
            anchor="nw",
            text="1. Judetul A - 0 \n2. Judetul B - 0 \n3. Judetul C - 0 ",
            fill="#000000",
            font=("Inter", 24 * -1)
        )
    
    # === BUTOANE NOOILE FUNCȚIONALITĂȚI ===
    # Frame pentru butoanele de funcționalități avansate
    
    def open_analytics_dashboard():
        """Deschide dashboard-ul de analiză avansată"""
        try:
            from src.ui.analytics_ui import show_analytics_dashboard
            show_analytics_dashboard(window, output_folder)
        except ImportError:
            from tkinter import messagebox
            messagebox.showinfo("Info", "Modulele de analiză nu sunt disponibile. Rulează 'pip install -r requirements.txt'")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Eroare", f"Eroare la deschiderea analytics: {e}")
    
    def open_search_ai():
        """Deschide interfața de căutare și AI/ML"""
        try:
            from src.ui.search_ai_ui import show_search_ai_window
            show_search_ai_window(window, output_folder)
        except ImportError:
            from tkinter import messagebox
            messagebox.showinfo("Info", "Modulele AI/ML nu sunt disponibile. Rulează 'pip install -r requirements.txt'")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Eroare", f"Eroare la deschiderea Search & AI: {e}")
    
    # Butoane pentru funcționalități avansate - în linie (mai lungi)
    analytics_button = Button(
        window,
        text="📊 Analytics Dashboard",
        command=open_analytics_dashboard,
        font=("Inter", 11, "bold"),
        bg="#4CAF50",
        fg="white",
        relief="raised",
        bd=2,
        padx=20,
        pady=8
    )
    analytics_button.place(x=180, y=380, width=200, height=40)
    
    search_ai_button = Button(
        window,
        text="🔍 Search & AI/ML",
        command=open_search_ai,
        font=("Inter", 11, "bold"),
        bg="#2196F3",
        fg="white",
        relief="raised",
        bd=2,
        padx=20,
        pady=8
    )
    search_ai_button.place(x=420, y=380, width=200, height=40)
    
    # === BUTOANE PRINCIPALE ===
    # Butoanele Continuă și Închide - în linie
    continue_button = Button(
        window,
        text="Continuă la rezultate",
        command=continue_to_results,
        font=("Inter", 14, "bold"),
        bg="#3DA5D9",
        fg="white",
        relief="raised",
        bd=2,
        padx=20,
        pady=10
    )
    continue_button.place(x=250, y=440, width=200, height=40)
    
    close_button = Button(
        window,
        text="Închide",
        command=close_window,
        font=("Inter", 14, "bold"),
        bg="#CC4444",
        fg="white",
        relief="raised",
        bd=2,
        padx=20,
        pady=8
    )
    close_button.place(x=450, y=440, width=100, height=40)
    
    # Buton pentru trimitere email raport
    email_button = Button(
        window,
        text="✉️ Trimite Raport pe Email",
        command=send_report_via_email,
        font=("Inter", 11, "bold"),
        bg="#F9A825",
        fg="white",
        relief="raised",
        bd=2,
        padx=20,
        pady=8
    )
    email_button.place(x=320, y=500, width=220, height=40)
    """Afișează fereastra de rapoarte cu date din fișierul Excel"""
    # Buton Ajutor cu fallback la text dacă imaginea nu se încarcă
    def open_guide():
        guide_path = PDF_PATH / "guide.pdf"
        if not guide_path.exists():
            from tkinter import messagebox
            messagebox.showerror("Eroare", f"Fișierul ghid nu există: {guide_path}", parent=window)
            print(f"[DEBUG] Ghidul nu există: {guide_path}")
            return
        print(f"[DEBUG] Deschid ghidul: {guide_path}")
        webbrowser.open(guide_path.as_uri())

    button_ajutor = None
    try:
        print("[DEBUG] Încerc să încarc imaginea Ajutor")
        button_image_ajutor = PhotoImage(file=relative_to_assets("button_ajutor_2.png"))
        window.button_image_ajutor = button_image_ajutor  # Previne garbage collection
        print("[DEBUG] Imagine Ajutor încărcată cu succes")
        Button_ajutor = Button(
            window,
            image=button_image_ajutor,
            borderwidth=0,
            highlightthickness=0,
            command=open_guide,
            relief="flat",
            activebackground="#D9D9D9",
            background="#D9D9D9"
        )
        canvas.create_window(723, 581, window=Button_ajutor, width=61, height=28)
        print("[DEBUG] Buton Ajutor plasat cu succes")
    except Exception as e:
        print(f"[DEBUG] Eroare la încărcarea imaginii Ajutor: {e}")
        button_ajutor = Button(
            window,
            text="Ajutor",
            command=open_guide,
            font=("Inter", 12, "bold"),
            bg="#F9A825",
            fg="white",
            relief="solid",
            bd=3
        )
        canvas.create_window(723, 580, window=button_ajutor, width=85, height=34)
    window.protocol("WM_DELETE_WINDOW", on_close)
    return window


def calculate_stats_from_excel(output_folder):
    """Calculează statisticile din fișierul Excel"""
    if not output_folder:
        return None
        
    excel_path = os.path.join(output_folder, "Date_Persoane_OCR.xlsx")
    if not os.path.exists(excel_path):
        return None
    
    try:
        import pandas as pd
        df = pd.read_excel(excel_path, sheet_name='Date_Persoane')
        
        total = len(df)
        
        # Calculăm distribuția pe perioade (1 an vs 2 ani)
        # 2 ani = cei care au "da" în coloana 2_Ani
        # 1 an = cei care au "nu" în coloana 2_Ani
        if '2_Ani' in df.columns:
            two_years = len(df[df['2_Ani'].astype(str).str.strip().str.lower() == 'da'])
            one_year = total - two_years
        else:
            two_years = 0
            one_year = total
        
        # Calculăm top județe pe baza ANAF_Apartin
        judete_count = {}
        if 'ANAF_Apartin' in df.columns:
            for anaf in df['ANAF_Apartin'].dropna():
                anaf_str = str(anaf).strip()
                if anaf_str and anaf_str != 'NEDETERMINAT':
                    if anaf_str in judete_count:
                        judete_count[anaf_str] += 1
                    else:
                        judete_count[anaf_str] = 1
        
        # Sortăm județele după numărul de formulare
        top_judete = sorted(judete_count.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total': total,
            'one_year': one_year,
            'two_years': two_years,
            'top_judete': top_judete
        }
        
    except Exception as e:
        print(f"Eroare la calcularea statisticilor: {e}")
        return None


# === Permite rularea directă a fișierului pentru testare ===
if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Ascunde fereastra principală
    # Setează root ca atribut pentru închidere corectă
    show_rapoarte_window._root = root
    show_rapoarte_window(output_folder=None)
    root.mainloop()
