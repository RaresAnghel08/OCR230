
import os

def delete_config():
    appdata = os.environ.get("APPDATA")
    config_folder = os.path.join(appdata, "ocr230")
    config_file = os.path.join(config_folder, "config.ini")
    if os.path.exists(config_file):
        os.remove(config_file)
        print(f"✅ Sters: {config_file}")
    else:
        print(f"❌ Nu exista: {config_file}")

if __name__ == "__main__":
    delete_config()
