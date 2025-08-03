"""
Test pentru funcționalitățile avansate OCR230
Script pentru verificarea rapidă a implementării
"""

import sys
import os
from pathlib import Path

def test_file_structure():
    """Testează dacă toate fișierele sunt create"""
    print("🔍 Verificare structură fișiere...")
    
    required_files = [
        "src/analytics/dashboard_manager.py",
        "src/ai_ml/ai_manager.py", 
        "src/search/search_manager.py",
        "src/ui/analytics_ui.py",
        "src/ui/search_ai_ui.py",
        "setup_advanced_features.py",
        "ADVANCED_FEATURES.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"  ❌ Fișiere lipsă: {missing_files}")
        return False
    
    print("  🎉 Toate fișierele sunt prezente!")
    return True

def test_imports():
    """Testează importurile de bază (fără dependențe externe)"""
    print("\n🔍 Verificare imports de bază...")
    
    try:
        # Test analytics module
        sys.path.append('src')
        from analytics.dashboard_manager import DashboardManager
        print("  ✅ DashboardManager import OK")
        
        # Test AI/ML module  
        from ai_ml.ai_manager import AIMLManager
        print("  ✅ AIMLManager import OK")
        
        # Test search module
        from search.search_manager import SearchManager
        print("  ✅ SearchManager import OK")
        
        print("  🎉 Toate modulele se importă corect!")
        return True
        
    except ImportError as e:
        print(f"  ❌ Eroare import: {e}")
        return False

def test_ui_imports():
    """Testează importurile UI"""
    print("\n🔍 Verificare imports UI...")
    
    try:
        sys.path.append('src')
        from ui.search_ai_ui import SearchAIUI
        print("  ✅ SearchAIUI import OK")
        
        # Pentru analytics_ui trebuie să verificăm că e fișier valid
        with open('src/ui/analytics_ui.py', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class' in content and 'def' in content:
                print("  ✅ analytics_ui.py este valid")
            else:
                print("  ⚠️ analytics_ui.py pare să aibă probleme")
        
        print("  🎉 UI modules sunt OK!")
        return True
        
    except Exception as e:
        print(f"  ❌ Eroare UI import: {e}")
        return False

def test_dependencies():
    """Testează disponibilitatea dependențelor"""
    print("\n🔍 Verificare dependențe opționale...")
    
    dependencies = {
        'plotly': 'Dashboard Analytics',
        'dash': 'Dashboard Analytics', 
        'spacy': 'AI/ML Processing',
        'sklearn': 'Machine Learning',
        'whoosh': 'Search Engine',
        'fuzzywuzzy': 'Fuzzy Matching'
    }
    
    available = []
    missing = []
    
    for dep, feature in dependencies.items():
        try:
            __import__(dep)
            available.append(f"{dep} ({feature})")
            print(f"  ✅ {dep} - {feature}")
        except ImportError:
            missing.append(f"{dep} ({feature})")
            print(f"  ⚠️ {dep} - {feature} - Nu este instalat")
    
    print(f"\n  📊 Disponibile: {len(available)}/{len(dependencies)}")
    
    if missing:
        print("  💡 Pentru instalare: python setup_advanced_features.py")
    
    return len(available) > 0

def test_main_window_integration():
    """Testează integrarea în main window"""
    print("\n🔍 Verificare integrare main window...")
    
    try:
        with open('src/ui/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ('open_analytics_dashboard', 'Funcție Analytics'),
            ('open_search_ai', 'Funcție Search & AI'),
            ('📊 Analytics', 'Buton Analytics'),
            ('🔍 Search & AI', 'Buton Search & AI')
        ]
        
        all_good = True
        for check, desc in checks:
            if check in content:
                print(f"  ✅ {desc}")
            else:
                print(f"  ❌ {desc} - Lipsește")
                all_good = False
        
        if all_good:
            print("  🎉 Integrarea în main window este completă!")
        
        return all_good
        
    except Exception as e:
        print(f"  ❌ Eroare verificare main window: {e}")
        return False

def main():
    """Funcția principală de test"""
    print("🚀 OCR230 - Test Funcționalități Avansate")
    print("=" * 50)
    
    tests = [
        ("Structură Fișiere", test_file_structure),
        ("Module Imports", test_imports), 
        ("UI Imports", test_ui_imports),
        ("Dependențe", test_dependencies),
        ("Main Window Integration", test_main_window_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Eroare în {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 REZUMAT TESTE:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Rezultat final: {passed}/{len(results)} teste trecute")
    
    if passed == len(results):
        print("🎉 TOATE TESTELE AU TRECUT! Funcționalitățile avansate sunt gata!")
    elif passed >= len(results) // 2:
        print("⚠️ Majoritatea testelor au trecut. Verifică erorile de mai sus.")
    else:
        print("❌ Multe probleme detectate. Verifică implementarea.")
    
    print("\n💡 Pentru instalare dependențe: python setup_advanced_features.py")
    print("📖 Pentru documentație: vezi ADVANCED_FEATURES.md")
    
    input("\nApasă Enter pentru a continua...")

if __name__ == "__main__":
    main()
