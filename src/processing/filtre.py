import re
import os
import sys

def filtru_cifre(text):
    return ''.join(re.findall(r'[0-9]', text))  # Păstrează doar cifrele

def replace_diacritics(text):
    text = text.replace('ă', 'a')
    text = text.replace('â', 'a')
    text = text.replace('î', 'i')
    text = text.replace('ș', 's')
    text = text.replace('ț', 't')
    text = text.replace('Ă', 'A')
    text = text.replace('Â', 'A')
    text = text.replace('Î', 'I')
    text = text.replace('Ș', 'S')
    text = text.replace('Ț', 'T')
    return text  # Add return statement

# Funcție pentru a păstra doar litere (fără spații și alte caractere)
def filtru_litere(text):
    text = text.replace('-', ' ')
    text = text.replace(',', ' ')
    #replace diacritics
    text = replace_diacritics(text)
    #return ''.join(re.findall(r'[a-zA-Z ]', text))  # Păstrează doar literele
    return text  # Add return statement

def filtru_nume(text):
    text = text.replace(" @", "@")  # Elimină spațiul din fața simbolului @
    text = text.replace('-', ' ')  # Înlocuiește cratimele cu spațiu
    text = text.replace(',', ' ')  # Înlocuiește virgulele cu spațiu
    #replace diacritics
    text = replace_diacritics(text)
    # Păstrează doar literele și spațiile
    #return ''.join(re.findall(r'[a-zA-Z ]', text))
    return text  # Add return statement

# Funcție pentru a capitaliza prima literă din fiecare cuvânt
def capitalize_words(text):
    return ' '.join([word.capitalize() for word in text.split()])

#print(filtru_nume("Popesăcu Ion"))