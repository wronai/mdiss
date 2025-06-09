# 📥 Instalacja i konfiguracja

## Wymagania wstępne

- Python 3.8 lub nowszy
- [Poetry](https://python-poetry.org/) (zalecany do rozwoju)
- Git
- Konto GitHub z dostępem do repozytorium, do którego chcesz dodawać zgłoszenia

## Sposoby instalacji

### 1. Instalacja z PyPI (zalecane dla użytkowników)

```bash
pip install mdiss
```

### 2. Instalacja z kodu źródłowego (dla programistów)

```bash
# Sklonuj repozytorium
git clone https://github.com/wronai/mdiss.git
cd mdiss

# Zainstaluj zależności
make install
```

## Konfiguracja środowiska

### Konfiguracja tokenu GitHub

1. Wygeneruj nowy token dostępu w ustawieniach konta GitHub:
   - Przejdź do [Ustawienia konta GitHub](https://github.com/settings/tokens)
   - Kliknij "Generate new token (classic)"
   - Nadaj odpowiednie uprawnienia (minimum `repo`)
   - Skopiuj wygenerowany token

2. Skonfiguruj narzędzie:
   ```bash
   mdiss setup
   ```

   Wprowadź token, gdy zostaniesz o to poproszony.

## Weryfikacja instalacji

Sprawdź, czy narzędzie zostało poprawnie zainstalowane:

```bash
mdiss --version
```

## Rozwój projektu

### Konfiguracja środowiska deweloperskiego

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/wronai/mdiss.git
   cd mdiss
   ```

2. Zainstaluj zależności deweloperskie:
   ```bash
   make dev
   ```

3. Zainstaluj pre-commit hooks:
   ```bash
   make install-hooks
   ```

### Dostępne polecenia Makefile

```bash
# Instalacja i konfiguracja
make install           # Zainstaluj podstawowe zależności
make dev               # Zainstaluj zależności deweloperskie
make install-hooks     # Zainstaluj git hooks
make update            # Zaktualizuj zależności

# Testowanie i jakość kodu
make test              # Uruchom testy jednostkowe
make lint              # Sprawdź jakość kodu
make format            # Sformatuj kod automatycznie
make check-format      # Sprawdź formatowanie kodu

# Budowa i publikacja
make build             # Zbuduj pakiet
make publish           # Opublikuj nową wersję (wymaga uprawnień)

make clean             # Wyczyść środowisko
```

## Aktualizacja

### Aktualizacja z PyPI

```bash
pip install --upgrade mdiss
```

### Aktualizacja z kodu źródłowego

```bash
git pull origin main
make update
```

## Odinstalowanie

```bash
pip uninstall mdiss
```

## Rozwiązywanie problemów

### Błąd braku uprawnień

Jeśli podczas instalacji pojawią się błędy związane z uprawnieniami, spróbuj użyć flagi `--user`:

```bash
pip install --user mdiss
```

lub uruchom polecenie z uprawnieniami administratora:

```bash
sudo pip install mdiss
```

### Problem z zależnościami

Jeśli występują problemy z zależnościami, spróbuj:

1. Zaktualizować pip:
   ```bash
   pip install --upgrade pip
   ```

2. Zainstalować zależności ręcznie:
   ```bash
   pip install -r requirements.txt
   ```

## Pomoc i wsparcie

Jeśli napotkasz problemy podczas instalacji:

1. Sprawdź [sekcję Issues](https://github.com/wronai/mdiss/issues) czy problem nie został już zgłoszony
2. Jeśli nie, [stwórz nowe zgłoszenie](https://github.com/wronai/mdiss/issues/new/choose) z opisem problemu
make test           # Uruchom testy
make test-verbose   # Testy z pełnym wyjściem
make test-coverage  # Testy z pokryciem kodu
make test-unit      # Tylko testy jednostkowe
make test-integration # Tylko testy integracyjne

# Jakość kodu
make lint     # Sprawdź jakość kodu
make format   # Sformatuj kod automatycznie
make security # Sprawdź bezpieczeństwo
make qa       # Uruchom pełne sprawdzenie jakości (lint + test)

# Dokumentacja
make docs          # Zbuduj dokumentację
make docs-serve    # Uruchom lokalny serwer z dokumentacją
make docs-deploy   # Wdróż dokumentację na GitHub Pages

# Budowanie i publikacja
make build     # Zbuduj pakiet
make publish   # Opublikuj na PyPI
make clean     # Wyczyść pliki budowania

# Wersjonowanie
make version-patch  # Zwiększ wersję patch (0.0.X)
make version-minor  # Zwiększ wersję minor (0.X.0)
make version-major  # Zwiększ wersję major (X.0.0)
```

## Weryfikacja instalacji

Sprawdź, czy instalacja się powiodła:

```bash
mdiss --version
```

Oczekiwane wyjście:
```
mdiss, wersja 1.0.60
```

## Konfiguracja tokenu GitHub

mdiss wymaga tokenu GitHub do tworzenia zgłoszeń. Użyj polecenia konfiguracyjnego:

```bash
mdiss setup
```

To polecenie:
1. Otworzy stronę generowania tokenu GitHub
2. Zaznaczy wymagane uprawnienia (`repo`, `write:issues`)
3. Poprowadzi przez proces tworzenia tokenu
4. Opcjonalnie zapisze token lokalnie

### Ręczne tworzenie tokenu

1. Przejdź do [Ustawienia GitHub > Tokeny dostępu osobistego](https://github.com/settings/tokens)
2. Kliknij "Generate new token"
3. Wybierz uprawnienia:
   - `repo` - Pełna kontrola nad prywatnymi repozytoriami
   - `write:issues` - Uprawnienia do zapisu zgłoszeń
4. Skopiuj wygenerowany token
5. Zapisz go w bezpiecznym miejscu

### Opcje przechowywania tokenu

#### Opcja 1: Plik (zalecane)
```bash
echo "twój_token_tutaj" > .mdiss_token
echo ".mdiss_token" >> .gitignore
```

#### Opcja 2: Zmienna środowiskowa
```bash
export GITHUB_TOKEN="twój_token_tutaj"
```

#### Opcja 3: Parametr wiersza poleceń
```bash
mdiss create plik.md właściciel repozytorium --token twój_token_tutaj
```

## Konfiguracja

### Konfiguracja globalna

Stwórz plik konfiguracyjny w `~/.mdiss/config.toml`:

```toml
[github]
default_owner = "myorg"
default_assignees = ["dev1", "dev2"]

[analysis]
confidence_threshold = 0.8
auto_assign_by_type = true

[output]
default_format = "table"
use_colors = true
```

### Project Configuration

Create a local config file at `.mdiss.toml`:

```toml
[github]
owner = "myorg"
repo = "myproject"
milestone = 5

[labels]
priority_prefix = "priority:"
category_prefix = "type:"
```

## Troubleshooting

### Common Issues

#### 1. Command not found
```bash
# Check if mdiss is in PATH
which mdiss

# If not found, try:
python -m mdiss --version
```

#### 2. Import errors
```bash
# Reinstall with dependencies
pip install --force-reinstall mdiss
```

#### 3. Token issues
```bash
# Test token validity
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

#### 4. Permission errors
```bash
# Check token scopes
curl -H "Authorization: token YOUR_TOKEN" -I https://api.github.com/user
# Look for X-OAuth-Scopes header
```

### Platform-Specific Notes

#### Windows
```powershell
# Use PowerShell or Command Prompt
pip install mdiss

# If PATH issues:
python -m pip install mdiss
python -m mdiss --version
```

#### macOS
```bash
# May need to use pip3
pip3 install mdiss

# Or with Homebrew Python
/usr/local/bin/pip3 install mdiss
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3-pip
pip3 install mdiss

# CentOS/RHEL
sudo yum install python3-pip
pip3 install mdiss
```

### Virtual Environments

#### venv
```bash
python -m venv mdiss-env
source mdiss-env/bin/activate  # Linux/Mac
# mdiss-env\Scripts\activate  # Windows
pip install mdiss
```

#### conda
```bash
conda create -n mdiss python=3.11
conda activate mdiss
pip install mdiss
```

#### Poetry
```bash
mkdir my-project && cd my-project
poetry init
poetry add mdiss
poetry shell
```

## Uninstallation

```bash
pip uninstall mdiss
```

For development installations:
```bash
# If installed with -e
pip uninstall mdiss

# Clean Poetry environment
poetry env remove python
```

## Next Steps

After installation:

1. [Quick Start Guide](quickstart.md) - Get started quickly
2. [CLI Reference](cli.md) - Learn all commands
3. [Configuration](configuration.md) - Customize behavior
4. [Examples](examples/basic.md) - See practical examples
