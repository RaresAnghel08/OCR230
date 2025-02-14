import tkinter as tk
from tkinter import filedialog

def select_folder_input(entry_input):
    global folder_input
    folder_input = filedialog.askdirectory(title="Selectează folderul de input")
    if folder_input:
        entry_input.delete(0, tk.END)  # Șterge textul existent
        entry_input.insert(0, folder_input)  # Introduce calea selectată în entry

def select_folder_output(entry_output):
    global folder_output
    folder_output = filedialog.askdirectory(title="Selectează folderul de output")
    if folder_output:
        entry_output.delete(0, tk.END)  # Șterge textul existent
        entry_output.insert(0, folder_output)  # Introduce calea selectată în entry
'''
def update_progress(progress_bar, current, total):
    progress_bar["value"] = current
    progress_bar["maximum"] = total
    progress_bar.update_idletasks()
'''

def update_progress(progress_bar, current, total, root):
    # Calculăm procentajul de progres
    percentage = (current / total) * 100
    # Setăm progresul pe bara
    progress_bar['value'] = percentage
    root.update_idletasks()  # Asigurăm că actualizăm interfața
