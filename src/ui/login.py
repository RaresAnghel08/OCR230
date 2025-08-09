"""
Login Interface for OCR230
Manages user configuration through config.ini in AppData folder
"""

import os
import configparser
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage, Entry, messagebox
from tkinter import ttk
import psycopg2
from dotenv import load_dotenv

# Load .env for PostgreSQL connection
load_dotenv(dotenv_path=os.path.join(Path(__file__).parent.parent.parent, '.env'))

def check_ong_in_db(ong_name, admin_id):
    host = os.environ.get('DATABASE_HOST')
    user = os.environ.get('DATABASE_USER')
    password = os.environ.get('DATABASE_PASSWORD')
    dbname = os.environ.get('DATABASE_NAME')
    try:
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=dbname
        )
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM ong WHERE nume = %s AND admin_id = %s LIMIT 1", (ong_name, admin_id))
        result = cur.fetchone()
        cur.close()
        conn.close()
        return bool(result)
    except Exception as e:
        print(f"Eroare conexiune PostgreSQL: {e}")
        return False

# Get the assets path
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

def save_config(name, ong, email, telephone):
    """Save configuration to config.ini"""
    config_path = get_config_file_path()
    config = configparser.ConfigParser()
    
    # Create USER section
    config['USER'] = {
        'name': name,
        'ong': ong,
        'email': email,
        'telephone': telephone
    }
    
    # Save to file
    with open(config_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    
    print(f"✅ Configuration saved to: {config_path}")
    return True

def validate_email(email):
    """Basic email validation"""
    return '@' in email and '.' in email.split('@')[1]

def validate_phone(phone):
    """Basic phone validation - Romanian format"""
    # Remove spaces and common separators
    clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    # Check if it's a valid Romanian phone number (starts with 0 and has 10 digits)
    return clean_phone.startswith('0') and len(clean_phone) == 10 and clean_phone.isdigit()

def check_existing_config():
    """Check if valid configuration exists"""
    config = load_config()
    if config and 'USER' in config:
        user_section = config['USER']
        required_fields = ['name', 'ong', 'email', 'telephone']
        
        # Check if all required fields exist and are not empty
        if all(field in user_section and user_section[field].strip() for field in required_fields):
            return {
                'name': user_section['name'],
                'ong': user_section['ong'],
                'email': user_section['email'],
                'telephone': user_section['telephone']
            }
    
    return None

def show_login_window(on_success_callback):
    """Show login/configuration window"""
    
    # Check if configuration already exists
    existing_config = check_existing_config()
    if existing_config:
        print(f"🔐 User already configured: {existing_config['name']} ({existing_config['ong']})")
        on_success_callback(existing_config)
        return
    
    # Create login window
    login_window = Tk()
    login_window.title("OCR230 - Configurare Utilizator")
    login_window.geometry("600x540")
    login_window.configure(bg="#D9D9D9")
    login_window.resizable(False, False)

    # Center the window
    login_window.update_idletasks()
    x = (login_window.winfo_screenwidth() // 2) - (600 // 2)
    y = (login_window.winfo_screenheight() // 2) - (540 // 2)
    login_window.geometry(f"600x540+{x}+{y}")
    
    # Set window icon
    icon_path = Path(__file__).parent.parent.parent / "Assets" / "favicon.ico"
    try:
        login_window.iconbitmap(str(icon_path))
    except Exception:
        pass
    
    # Create canvas
    canvas = Canvas(
        login_window,
        bg="#D9D9D9",
        height=540,
        width=600,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)
    
    # Title
    canvas.create_text(
        300.0,
        40.0,
        anchor="center",
        text="OCR230",
        fill="#000000",
        font=("Inter", 28, "bold")
    )
    
    canvas.create_text(
        300.0,
        70.0,
        anchor="center",
        text="Configurare Utilizator",
        fill="#000000",
        font=("Inter", 16)
    )
    
    # Create form fields
    canvas.create_text(
        80.0,
        120.0,
        anchor="nw",
        text="Nume complet:",
        fill="#000000",
        font=("Inter", 12, "bold")
    )

    name_entry = Entry(
        login_window,
        font=("Inter", 11),
        bg="white",
        relief="solid",
        bd=1
    )
    name_entry.place(x=80, y=145, width=440, height=30)

    canvas.create_text(
        80.0,
        190.0,
        anchor="nw",
        text="ONG/Organizație:",
        fill="#000000",
        font=("Inter", 12, "bold")
    )

    ong_entry = Entry(
        login_window,
        font=("Inter", 11),
        bg="white",
        relief="solid",
        bd=1
    )
    ong_entry.place(x=80, y=215, width=440, height=30)

    canvas.create_text(
        80.0,
        260.0,
        anchor="nw",
        text="ID Unic:",
        fill="#000000",
        font=("Inter", 12, "bold")
    )

    admin_id_entry = Entry(
        login_window,
        font=("Inter", 11),
        bg="white",
        relief="solid",
        bd=1
    )
    admin_id_entry.place(x=80, y=285, width=440, height=30)
    
    canvas.create_text(
        80.0,
        330.0,
        anchor="nw",
        text="Email:",
        fill="#000000",
        font=("Inter", 12, "bold")
    )

    email_entry = Entry(
        login_window,
        font=("Inter", 11),
        bg="white",
        relief="solid",
        bd=1
    )
    email_entry.place(x=80, y=355, width=440, height=30)

    canvas.create_text(
        80.0,
        400.0,
        anchor="nw",
        text="Telefon:",
        fill="#000000",
        font=("Inter", 12, "bold")
    )

    phone_entry = Entry(
        login_window,
        font=("Inter", 11),
        bg="white",
        relief="solid",
        bd=1
    )
    phone_entry.place(x=80, y=425, width=440, height=30)
    
    # Status label
    status_label = canvas.create_text(
        300.0,
        470.0,
        anchor="center",
        text="",
        fill="#FF0000",
        font=("Inter", 10)
    )
    
    def validate_and_save():
        """Validate input and save configuration, apoi verifică ONG în PostgreSQL"""
        name = name_entry.get().strip()
        ong = ong_entry.get().strip()
        admin_id = admin_id_entry.get().strip()
        email = email_entry.get().strip()
        phone = phone_entry.get().strip()

        # Validation
        if not name:
            canvas.itemconfig(status_label, text="❌ Te rugăm să introduci numele complet")
            return
        if not ong:
            canvas.itemconfig(status_label, text="❌ Te rugăm să introduci organizația")
            return
        if not email or not validate_email(email):
            canvas.itemconfig(status_label, text="❌ Te rugăm să introduci un email valid")
            return
        if not phone or not validate_phone(phone):
            canvas.itemconfig(status_label, text="❌ Te rugăm să introduci un număr de telefon valid (format: 0XXXXXXXXX)")
            return

        # Verifică ONG în PostgreSQL
        canvas.itemconfig(status_label, text="⏳ Se verifică existența ONG-ului în baza de date...", fill="#0000AA")
        login_window.update_idletasks()
        if not check_ong_in_db(ong, admin_id):
            canvas.itemconfig(status_label, text="❌ ONG-ul sau ID-ul nu există în baza de date!", fill="#FF0000")
            return

        # Save configuration
        try:
            save_config(name, ong, email, phone)
            # Save admin_id in config.ini
            config_path = get_config_file_path()
            config = configparser.ConfigParser()
            config['USER'] = {
                'name': name,
                'ong': ong,
                'email': email,
                'telephone': phone,
                'admin_id': admin_id
            }
            with open(config_path, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            canvas.itemconfig(status_label, text="✅ Configurarea a fost salvată cu succes!", fill="#00AA00")
            login_window.after(1000, lambda: [
                login_window.destroy(),
                on_success_callback({
                    'name': name,
                    'ong': ong,
                    'email': email,
                    'telephone': phone,
                    'admin_id': admin_id
                })
            ])
        except Exception as e:
            canvas.itemconfig(status_label, text=f"❌ Eroare la salvarea configurației: {e}")
    
    # Save button
    save_button = Button(
        login_window,
        text="Salvează și Continuă",
        command=validate_and_save,
        font=("Inter", 12, "bold"),
        bg="#4CAF50",
        fg="white",
        relief="raised",
        bd=2,
        padx=20,
        pady=8
    )
    save_button.place(x=200, y=480, width=200, height=40)
    
    # Info text
    canvas.create_text(
        300.0,
        100.0,
        anchor="center",
        text="Prima configurare - te rugăm să completezi datele:",
        fill="#666666",
        font=("Inter", 10)
    )
    
    # Focus on first field
    name_entry.focus()
    
    # Handle window close
    def on_close():
        """Handle window close event"""
        if messagebox.askquestion(
            "Confirmă ieșirea", 
            "Dorești să ieși din aplicație?\nVa trebui să configurezi datele la următoarea pornire.",
            parent=login_window
        ) == 'yes':
            login_window.destroy()
            exit()
    
    login_window.protocol("WM_DELETE_WINDOW", on_close)
    
    # Run the login window
    login_window.mainloop()

def get_user_config():
    """Get user configuration (for use in other modules)"""
    return check_existing_config()

def reset_config():
    """Reset configuration for testing purposes"""
    import os
    config_path = get_config_file_path()
    if os.path.exists(config_path):
        os.remove(config_path)
        print(f"🗑️ Configuration deleted: {config_path}")
    else:
        print("❌ No configuration found to delete")

# Test function
if __name__ == "__main__":
    def test_callback(config):
        print(f"✅ Login successful for: {config['name']} from {config['ong']}")
        print(f"📧 Email: {config['email']}")
        print(f"📞 Phone: {config['telephone']}")
    
    show_login_window(test_callback)
