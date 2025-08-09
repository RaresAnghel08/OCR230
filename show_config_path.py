import os

def get_config_path():
    appdata = os.path.expanduser("~\\AppData\\Roaming")
    config_folder = os.path.join(appdata, "ocr230")
    config_file = os.path.join(config_folder, "config.ini")
    print("Calea completă:", config_file)
    if os.path.exists(config_file):
        print("✅ Fișierul există!")
    else:
        print("❌ Fișierul NU există!")

if __name__ == "__main__":
    get_config_path()