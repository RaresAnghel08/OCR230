import re

# Funcție pentru a păstra doar cifre (fără spații)
def filtru_cifre(text):
    return ''.join(re.findall(r'[0-9]', text))  # Păstrează doar cifrele

# Funcție pentru a păstra doar litere (fără spații și alte caractere)
def filtru_litere(text):
    text = text.replace('-', ' ')
    text = text.replace(',', ' ')
    return ''.join(re.findall(r'[a-zA-ZăâîșțĂÂÎȘȚ ]', text))  # Păstrează doar literele

def filtru_nume(text):
    text = text.replace('-', ' ')  # Înlocuiește cratimele cu spațiu
    text = text.replace(',', ' ')  # Înlocuiește virgulele cu spațiu
    # Adaugă un spațiu înainte de literele mari care sunt urmate de litere mici
    text = re.sub(r'(?<=[a-zA-ZăâîșțĂÂÎȘȚ])(?=[A-ZĂÂÎȘȚ])', ' ', text)
    # Păstrează doar literele și spațiile
    return ''.join(re.findall(r'[a-zA-ZăâîșțĂÂÎȘȚ ]', text))

# Funcție pentru a capitaliza prima literă din fiecare cuvânt
def capitalize_words(text):
    return ' '.join([word.capitalize() for word in text.split()])