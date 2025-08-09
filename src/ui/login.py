"""
Login Interface for OCR230
Manages user configuration through config.ini in AppData folder
Now uses API on Koyeb instead of direct PostgreSQL connection
"""

import os
import configparser
from pathlib import Path
from tkinter import Tk, Canvas, Button, Entry, messagebox
import requests  # pentru a apela API-ul
from tkinter import ttk

# URL-ul API-ului tău de pe Koyeb
API_URL = "https://database-f230-2d5a7df8.koyeb.app/"  # <-- schimbă cu URL-ul tău real

def check_ong_in_db(ong_name, admin_id):
    """Verifică ONG-ul folosind API-ul FastAPI de pe Koyeb"""
    try:
        response = requests.get(
            f"{API_URL}/check_ong",
            params={"ong_name": ong_name, "admin_id": admin_id},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("exists", False)
        else:
            print(f"Eroare API: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Eroare conexiune API: {e}")
        return False


# ---------------------- CONFIG & PATH HELPERS ----------------------

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / "assets"

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def get_config_folder():
    """Get or create the OCR230 config folder in AppData"""
    appdata_path = os.environ.get("APPDATA")
    config_folder = os.path.join(appdata_path, "ocr230")
    if not os.path.exists(config_folder):
        os.makedirs(config_folder)
        print(f"📁 Created config folder: {config_folder}")
    return config_folder

def get_config_file_path():
    """Get the full path to config.ini"""
    config_folder = get_config_folder()
    return os.path.join(config_folder, "config.ini")

def load_config():
    """Load configuration from config.ini"""
    config_path = get_config_file_path()
    config = configparser.ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path, encoding='utf-8')
        print(f"✅ Configuration loaded from: {config_path}")
        return config
    else:
        print(f"📝 No configuration found at: {config_path}")
        return None

def save_config(name, ong, email, telephone, admin_id):
    """Save configuration to config.ini"""
    config_path = get_config_file_path()
    config = configparser.ConfigParser()
    config['USER'] = {
        'name': name,
        'ong': ong,
        'email': email,
        'telephone': telephone,
        'admin_id': admin_id
    }
    with open(config_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    print(f"✅ Configuration saved to: {config_path}")
    return True

def validate_email(email):
    """Basic email validation"""
    return '@' in email and '.' in email.split('@')[1]

def validate_phone(phone):
    """Basic phone validation - Romanian format"""
    clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    return clean_phone.startswith('0') and len(clean_phone) == 10 and clean_phone.isdigit()

def check_existing_config():
    """Check if valid configuration exists"""
    config = load_config()
    if config and 'USER' in config:
        user_section = config['USER']
        required_fields = ['name', 'ong', 'email', 'telephone', 'admin_id']
        if all(field in user_section and user_section[field].strip() for field in required_fields):
            return dict(user_section)
    return None

# ---------------------- UI LOGIN WINDOW ----------------------

def show_login_window(on_success_callback):
    """Show login/configuration window"""

    existing_config = check_existing_config()
    if existing_config:
        print(f"🔐 User already configured: {existing_config['name']} ({existing_config['ong']})")
        on_success_callback(existing_config)
        return

    login_window = Tk()
    login_window.title("OCR230 - Configurare Utilizator")
    login_window.geometry("600x540")
    login_window.configure(bg="#D9D9D9")
    login_window.resizable(False, False)

    # Center
    login_window.update_idletasks()
    x = (login_window.winfo_screenwidth() // 2) - (600 // 2)
    y = (login_window.winfo_screenheight() // 2) - (540 // 2)
    login_window.geometry(f"600x540+{x}+{y}")

    canvas = Canvas(
        login_window, bg="#D9D9D9", height=540, width=600, bd=0,
        highlightthickness=0, relief="ridge"
    )
    canvas.place(x=0, y=0)

    canvas.create_text(300, 40, anchor="center", text="OCR230",
                       fill="#000", font=("Inter", 28, "bold"))
    canvas.create_text(300, 70, anchor="center", text="Configurare Utilizator",
                       fill="#000", font=("Inter", 16))

    # Form fields
    labels = [
        ("Nume complet:", 120),
        ("ONG/Organizație:", 190),
        ("ID Unic:", 260),
        ("Email:", 330),
        ("Telefon:", 400)
    ]
    entries = {}
    for text, y in labels:
        canvas.create_text(80, y, anchor="nw", text=text, fill="#000", font=("Inter", 12, "bold"))
        entry = Entry(login_window, font=("Inter", 11), bg="white", relief="solid", bd=1)
        entry.place(x=80, y=y+25, width=440, height=30)
        entries[text] = entry

    status_label = canvas.create_text(300, 470, anchor="center", text="", fill="#FF0000", font=("Inter", 10))

    def validate_and_save():
        name = entries["Nume complet:"].get().strip()
        ong = entries["ONG/Organizație:"].get().strip()
        admin_id = entries["ID Unic:"].get().strip()
        email = entries["Email:"].get().strip()
        phone = entries["Telefon:"].get().strip()

        if not name:
            canvas.itemconfig(status_label, text="❌ Introdu numele complet")
            return
        if not ong:
            canvas.itemconfig(status_label, text="❌ Introdu organizația")
            return
        if not email or not validate_email(email):
            canvas.itemconfig(status_label, text="❌ Email invalid")
            return
        if not phone or not validate_phone(phone):
            canvas.itemconfig(status_label, text="❌ Telefon invalid")
            return

        canvas.itemconfig(status_label, text="⏳ Verific ONG în baza de date...", fill="#0000AA")
        login_window.update_idletasks()

        if not check_ong_in_db(ong, admin_id):
            canvas.itemconfig(status_label, text="❌ ONG-ul sau ID-ul nu există!", fill="#FF0000")
            return

        save_config(name, ong, email, phone, admin_id)
        canvas.itemconfig(status_label, text="✅ Configurarea a fost salvată!", fill="#00AA00")
        login_window.after(1000, lambda: [
            login_window.destroy(),
            on_success_callback({
                'name': name, 'ong': ong, 'email': email,
                'telephone': phone, 'admin_id': admin_id
            })
        ])

    Button(
        login_window, text="Salvează și Continuă", command=validate_and_save,
        font=("Inter", 12, "bold"), bg="#4CAF50", fg="white",
        relief="raised", bd=2, padx=20, pady=8
    ).place(x=200, y=480, width=200, height=40)

    name_entry = list(entries.values())[0]
    name_entry.focus()

    def on_close():
        if messagebox.askquestion(
            "Confirmă ieșirea",
            "Dorești să ieși din aplicație?\nVa trebui să configurezi datele la următoarea pornire.",
            parent=login_window
        ) == 'yes':
            login_window.destroy()
            exit()

    login_window.protocol("WM_DELETE_WINDOW", on_close)
    login_window.mainloop()

def get_user_config():
    return check_existing_config()

def reset_config():
    config_path = get_config_file_path()
    if os.path.exists(config_path):
        os.remove(config_path)
        print(f"🗑️ Configuration deleted: {config_path}")
    else:
        print("❌ No configuration found to delete")

if __name__ == "__main__":
    def test_callback(config):
        print(f"✅ Login successful for: {config['name']} from {config['ong']}")
        print(f"📧 Email: {config['email']}")
        print(f"📞 Phone: {config['telephone']}")

    show_login_window(test_callback)
