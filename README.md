# Olimpiada Matematyczna –– Skrypt do rozdzielania pliku ze skanami rozwiązań zadań

### Do czego służy skrypt:
- rozwiązania skanuje się łącznie do kilku plików PDF,
- następnie używa się skryptów, aby podzielić duże pliki na mniejsze – zawierające po 1 rozwiązaniu,
- pliki po przetworzeniu są automatyczne odpowiednio nazwane,
- następnie tak nazwane pliki można wrzucić bezpośrednio do systemu w zakładce "Wgraj prace"

### Jak uruchomić skrypt:
1. Najpierw należy sklonować repozytorium na swój komputer:
```git clone nazwa_repozytorium```, gdzie nazwa_repozytorium to adres repozytorium na GitHubie.
2. Następnie należy utworzyć pythonowe środowisko wirtualne – zakładam, że python3 i pip3 są zainstalowane. 
```
pip3 install venv
python3 -m venv nazwa_venv
source nazwa_venv/bin/activate
pip3 install -r requirements.txt
```
Przedstatnia linijka – aktywowanie – będzie konieczna do uruchomienia skryptu przy każdym kolejnym uruchomieniu terminala.
3. Najpierw należy uruchomić skrypt, który potnie pliki na strony:
```python3 cut.py plik <WA/WR/...>``` 
lub
```python3 cut.py plik final```.
Pocięte pliki będą w folderze "tmp_files".
Można napisać prostą pętlę w bashu, aby pociąć więcej plików naraz
```
for file in input_files/dirname/*; do                 
    python cut.py "$file" DISTRICT
done

```
4. Po pocięciu plików należy uruchomić skrypt
```python3 main.py <WA/WR/...> ```
lub
```python3 main.py final ```.
5. Wówczas otworzy się aplikacja okienkowa – należy
ustalić numery dla wszystkich plików, następnie zapisać gotowe pliki.
6. Jeśli jest chęć użycia ChatuGPT należy uzupełnić openai_secret_key w programie.
7. Do cięcia plików z finału nie należy używać chatugpt.
8. Gotowe pliki będą w folderze "ready_files". 
9. Należy wrzucić gotowe pliki do systemu w zakładce "Wgraj prace".