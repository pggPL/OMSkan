import os
import sys
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from PyPDF2 import PdfMerger
# Zakładam, że `gpt` to lokalny moduł, którego tutaj nie definiujemy, ale jest wymagany.
from gpt import get_response

# Ścieżki do katalogów z plikami wejściowymi i wyjściowymi
input_directory = './tmp_files'
output_directory = './ready_files'
districts = ['GD', 'KA', 'KR', 'LO', 'LU', 'PO', 'RZ', 'SZ', 'TO', 'WA', 'WR', 'final']

# Sprawdzenie, czy podano wymagane argumenty
if len(sys.argv) != 2:
    print('Usage: python main.py <district/final>')
    sys.exit(1)

district = sys.argv[1]
if district not in districts:
    print('District not found')
    sys.exit(1)


# Tworzenie katalogu wyjściowego, jeśli nie istnieje
os.makedirs(os.path.join(output_directory, district), exist_ok=True)

# Tworzenie pliku z adnotacjami, jeśli nie istnieje
annotations_path = os.path.join(input_directory, district, 'annotations.csv')
if not os.path.exists(annotations_path):
    with open(annotations_path, 'w') as file:
        file.write(f'ścieżka,okręg,zadanie,numer ucznia\n')

# Blokada dla bezpiecznego dostępu do pliku z adnotacjami
annotations_lock = threading.Lock()

def update_annotations_csv(image_path, zadanie, numer_ucznia):
    """Aktualizuje plik CSV z adnotacjami."""
    annotations_lock.acquire()
    try:
        with open(annotations_path, 'r') as file:
            lines = file.readlines()

        # Usuwanie linii z aktualnym obrazem
        lines = [line for line in lines if image_path not in line]

        with open(annotations_path, 'w') as file:
            file.writelines(lines)

        # Dodawanie nowej linii z aktualizacją
        with open(annotations_path, 'a') as file:
            image_path_safe = image_path.replace(',', '')  # Usuwanie przecinków z nazwy pliku
            file.write(f'{image_path_safe},{district},{zadanie},{numer_ucznia}\n')
    finally:
        annotations_lock.release()
    create_files(image_path)

def update_table():
    # Słownik do przechowywania informacji o plikach i ich danych
    dic = {}
    
    # Sczytaj obecny stan tabeli do słownika
    existing_rows = {tabela.item(row)['values'][0]: row for row in tabela.get_children()}
    files = os.listdir(input_directory + '/' + district)

    files = [file for file in files if file.endswith('.png') or file.endswith('.pdf')]
    sorted_files = sorted(files, key=lambda x: (x[:-10], int(x.split('_')[-1][:-4])))
    
    for img in sorted_files:
        if img.endswith('.png'):
            # Jeśli plik nie istnieje w tabeli, dodaj go z pustymi wartościami
            if img not in existing_rows:
                tabela.insert("", "end", values=(img, "", "", ""))
            dic[img] = ("", "", "")
    
    # Sczytaj annotations.csv i zaktualizuj słownik
    with open(input_directory + '/' + district + '/annotations.csv', 'r') as file:
        lines = file.readlines()
        for line in lines[1:]:
            sciezka, okreg, zadanie, numer_ucznia = line.strip().split(',')
            dic[sciezka] = (okreg, zadanie, numer_ucznia)
            # Aktualizuj istniejące wiersze w tabeli
            if sciezka in existing_rows:
                tabela.item(existing_rows[sciezka], values=(sciezka, okreg, zadanie, numer_ucznia))
            else:
                # Jeśli plik nie istnieje w tabeli, dodaj go
                tabela.insert("", "end", values=(sciezka, okreg, zadanie, numer_ucznia))
    
    # Usuń wiersze, których nie ma w aktualnych danych
    for img in existing_rows:
        if img not in dic:
            tabela.delete(existing_rows[img])
        

def gpt_one():
    global district
    # read current image
    selected_item = tabela.focus()
    item = tabela.item(selected_item)
    image_path = item['values'][0]
    district, number, problem = get_response(input_directory, district, image_path)
    problem, number = int(problem), int(number)
    
    tabela.item(selected_item, values=(image_path, district, problem, number))
    update_annotations_csv(image_path, problem, number)

def gpt_all():
    image_paths = [tabela.item(row)['values'][0] for row in tabela.get_children() if tabela.item(row)['values'][1] == '']
    def gpt_one_wrapper(image_path):
        global district
        district, number, problem = get_response(input_directory, district, image_path)
        print(district, number, problem)
        problem = int(problem)
        number = int(number)
        update_annotations_csv(image_path,  problem, number)
        # update table
    
    threads = [threading.Thread(target=gpt_one_wrapper, args=(image_path,)) for image_path in image_paths]
    for thread in threads:
        thread.start()
        thread.join()
        update_table()
    

def show_image(_, elem=None):
    selected_item = tabela.focus()
    item = tabela.item(selected_item)
    image_path = input_directory + '/' + district + '/' + item['values'][0]
    if elem is not None:
        image_path = input_directory + '/' + district + '/' + elem
        # set focus on next item
        next_item = tabela.next(selected_item)
        if next_item:
            tabela.selection_set(next_item)
            tabela.focus(next_item)
            tabela.see(next_item)
    
    # Wczytaj i przeskaluj obrazek
    image = Image.open(image_path)
    image = image.resize((600, 800))
    photo = ImageTk.PhotoImage(image)
    
    right_label.config(image=photo)
    right_label.image = photo
    
    if item['values'][2] != '':
        entry_zadanie.delete(0, tk.END)
        entry_zadanie.insert(0, item['values'][2])
    entry_numer_ucznia.delete(0, tk.END)
    entry_numer_ucznia.insert(0, item['values'][3])
    
    

def create_files(filename):
    annotations_lock.acquire()
    lines = []
    
    with open(input_directory + '/' + district + '/annotations.csv', 'r') as file:
        lines = file.readlines()
    
    lines = lines[1:]
    lines.sort(key=lambda x: (x.split(',')[0][:-4], int(x.split(',')[0].split('_')[-1][:-4])))
    
    # get line with current image
    sciezka, okreg, zadanie, numer_ucznia = '', '', '', ''
    for line in lines:
        if filename in line:
            sciezka, okreg, zadanie, numer_ucznia = line.strip().split(',')
            break
    files = []
    for line in lines:
        fname, okreg1, zadanie1, numer_ucznia1 = '', '', '', ''
        fname = fname[:-4] + '.pdf'
        if okreg1 == okreg and zadanie1 == zadanie and numer_ucznia1 == numer_ucznia:
            files.append(input_directory + '/' + district + '/' + fname)
    stage_str = "3" if district == "final" else "2"
    final_filename = stage_str + "_" + (okreg + "_" if (district != "final") else "")+ numer_ucznia + '_' + zadanie + '.pdf'
    # merge pdf from files
    merger = PdfMerger()
    for file in files:
        merger.append(file)
    merger.write(output_directory + '/' + district + '/' + final_filename)
    merger.close()
    
    # create file
    annotations_lock.release()

def create_all_files():
    image_paths = [tabela.item(row)['values'][0] for row in tabela.get_children()]
    def create_files_wrapper(image_path):
        create_files(image_path)
    
    threads = [threading.Thread(target=create_files_wrapper, args=(image_path,)) for image_path in image_paths]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    update_table()


# Utwórz główne okno
root = tk.Tk()
root.title("Olimpiada Matematyczna – aplikacja do sortowania prac")
# size
root.geometry("1400x800")

# Utwórz ramkę dla tabeli i szczegółów obrazka
frame = tk.Frame(root)

# Utwórz tabelę
tabela = ttk.Treeview(frame, columns=("ścieżka", "okręg", "zadanie", "numer ucznia"), show="headings")
tabela.heading("ścieżka", text="ścieżka")
tabela.heading("okręg", text="okręg")
tabela.heading("zadanie", text="zadanie")
tabela.heading("numer ucznia", text="numer ucznia")
tabela.column("ścieżka", width=200)
tabela.column("okręg", width=80)
tabela.column("zadanie", width=80)
tabela.column("numer ucznia", width=80)

tabela.bind("<Double-1>", show_image)

dic = {}

# ustal wszystko na ("" , "" , "")

for img in os.listdir(input_directory + '/' + district):
    if img.endswith('.png'):
        dic[img] = ("", "", "")

# sczytaj annotations.csv
with open(input_directory + '/' + district + '/annotations.csv', 'r') as file:
    lines = file.readlines()
    for line in lines[1:]:
        sciezka, okreg, zadanie, numer_ucznia = line.split(',')
        dic[sciezka] = (okreg, zadanie, numer_ucznia)

files = os.listdir(input_directory + '/' + district)
# exclude files that are not images
files = [file for file in files if file.endswith('.png') or file.endswith('.pdf')]
sorted_files = sorted(files, key=lambda x: (x[:-10], int(x.split('_')[-1][:-4])))
obrazki = [ ( img, dic[img][0], dic[img][1], dic[img][2]) for img in sorted_files if img.endswith('.png') ]


# Wypełnij tabelę danymi
for obrazek in obrazki:
    tabela.insert('', tk.END, values=obrazek)

# przycisk do startu sczytywania
start_button = tk.Button(root, text="Rozpocznij szczytywanie chatemGPT", command=lambda: gpt_all())
start_button.pack(side=tk.TOP)

start_button = tk.Button(root, text="Sczytaj obecne", command=lambda: gpt_one())
start_button.pack(side=tk.TOP)


files_button = tk.Button(root, text="Stwórz pliki wyjściowe", command=lambda: create_all_files())
files_button.pack(side=tk.TOP)


# formularz z wyborem okręgu, zadania i numeru ucznia
# Ramka na formularz
form_frame = tk.Frame(root)

# Umieść tabelę w ramce
tabela.pack(side=tk.LEFT, fill=tk.BOTH)
form_frame.pack(side=tk.LEFT, fill=tk.BOTH)


# Etykieta i pole tekstowe dla zadania
label_zadanie = tk.Label(form_frame, text="Zadanie:")
label_zadanie.pack(side=tk.TOP)
entry_zadanie = tk.Entry(form_frame, width=5)
entry_zadanie.pack(side=tk.TOP, padx=5)

# Etykieta i pole tekstowe dla numeru ucznia
label_numer_ucznia = tk.Label(form_frame, text="Numer ucznia:")
label_numer_ucznia.pack(side=tk.TOP)
entry_numer_ucznia = tk.Entry(form_frame, width=5)
entry_numer_ucznia.pack(side=tk.TOP, padx=5)

def process_selection():
    problem_number = entry_zadanie.get()
    student_number = entry_numer_ucznia.get()
    
    selected_item = tabela.focus()
    item = tabela.item(selected_item)
    image_path = item['values'][0]
    
    update_annotations_csv(image_path, problem_number, student_number)
    
    update_table()
    
    next_item = tabela.next(selected_item)
    image_path = tabela.item(next_item)['values'][0]
    show_image(None, image_path)
    

confirm_button = tk.Button(form_frame, text="Zatwierdź", command=process_selection)
confirm_button.pack(side=tk.TOP)

# if enter
root.bind('<Return>', lambda event: process_selection())

frame.pack(fill=tk.BOTH, expand=True)

right_label = tk.Label(frame)
right_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Main loop
root.mainloop()
