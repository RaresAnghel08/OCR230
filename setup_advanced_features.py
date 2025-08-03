"""
OCR230 - Installer pentru funcționalități avansate
Script pentru instalarea dependențelor AI/ML și setup inițial
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package):
    """Instalează un pachet pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def download_spacy_model():
    """Descarcă modelul spaCy pentru română"""
    try:
        # Încearcă să descarce modelul românesc
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "ro_core_news_sm"])
        return True
    except subprocess.CalledProcessError:
        try:
            # Fallback la modelul englez
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            return True
        except subprocess.CalledProcessError:
            return False

def setup_directories():
    """Creează directoarele necesare pentru AI/ML"""
    base_path = Path(__file__).parent
    
    directories = [
        base_path / "data" / "analytics",
        base_path / "data" / "search_index",
        base_path / "data" / "ai_models",
        base_path / "data" / "saved_searches",
        base_path / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Creat director: {directory}")

def check_installation():
    """Verifică instalarea modulelor"""
    modules_to_check = [
        "plotly",
        "dash", 
        "spacy",
        "scikit-learn",
        "whoosh",
        "fuzzywuzzy"
    ]
    
    missing_modules = []
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"✅ {module}: Instalat")
        except ImportError:
            print(f"❌ {module}: Lipsește")
            missing_modules.append(module)
    
    return missing_modules

def main():
    """Funcția principală de setup"""
    print("🚀 OCR230 - Setup funcționalități avansate")
    print("=" * 50)
    
    # 1. Verifică modulele existente
    print("\n📋 Verificare module existente...")
    missing = check_installation()
    
    if missing:
        print(f"\n📦 Instalare {len(missing)} module lipsă...")
        for module in missing:
            print(f"   Instalare {module}...")
            if install_package(module):
                print(f"   ✅ {module} instalat cu succes")
            else:
                print(f"   ❌ Eroare la instalarea {module}")
    else:
        print("\n✅ Toate modulele sunt deja instalate!")
    
    # 2. Setup spaCy
    print("\n🧠 Setup spaCy pentru procesare text...")
    if download_spacy_model():
        print("✅ Model spaCy instalat cu succes")
    else:
        print("⚠️ Eroare la instalarea modelului spaCy")
    
    # 3. Creează directoarele
    print("\n📁 Creare directoare...")
    setup_directories()
    
    # 4. Verificare finală
    print("\n🔍 Verificare finală...")
    missing_final = check_installation()
    
    if not missing_final:
        print("\n🎉 Setup complet! Toate funcționalitățile avansate sunt disponibile.")
        print("\nFuncționalități activate:")
        print("📊 Dashboard Analytics Avansat")
        print("🤖 AI/ML Auto-corrections")
        print("🔍 Search Engine Avansat")
        print("👥 Management Duplicate")
    else:
        print(f"\n⚠️ Setup incomplet. Module lipsă: {missing_final}")
        print("Rulează manual: pip install -r requirements.txt")
    
    print("\n" + "=" * 50)
    input("Apasă Enter pentru a continua...")

if __name__ == "__main__":
    main()
