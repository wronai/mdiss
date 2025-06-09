# 🚀 Użycie mdiss

Ten dokument zawiera szczegółowe informacje na temat korzystania z narzędzia `mdiss`.

## Spis treści

- [Szybki start](#-szybki-start)
- [Podstawowe użycie](#-podstawowe-użycie)
  - [Analiza plików markdown](#analiza-plików-markdown)
  - [Tworzenie zgłoszeń na GitHubie](#tworzenie-zgłoszeń-na-githubie)
  - [Konfiguracja](#konfiguracja)
- [Zaawansowane użycie](#-zaawansowane-użycie)
  - [Filtrowanie wyników](#filtrowanie-wyników)
  - [Dostosowywanie formatu wyjścia](#dostosowywanie-formatu-wyjścia)
  - [Integracja z CI/CD](#integracja-z-cicd)
- [Przykłady użycia](#-przykłady-użycia)
- [Rozwiązywanie problemów](#-rozwiązywanie-problemów)

## 🚀 Szybki start

1. **Zainstaluj** narzędzie:
   ```bash
   pip install mdiss
   ```

2. **Skonfiguruj** dostęp do GitHub:
   ```bash
   mdiss setup
   ```

3. **Przeanalizuj** plik z błędami:
   ```bash
   mdiss analyze errors.md
   ```

4. **Utwórz** zgłoszenia (w trybie testowym):
   ```bash
   mdiss create errors.md twój-uzytkownik/twoje-repo --dry-run
   ```

5. **Wyślij** zgłoszenia na GitHub:
   ```bash
   mdiss create errors.md twój-uzytkownik/twoje-repo
   ```

## 📋 Podstawowe użycie

### Analiza plików markdown

#### Podstawowa analiza

```bash
# Analiza pojedynczego pliku
mdiss analyze sciezka/do/pliku.md

# Analiza wielu plików
mdiss analyze "sciezka/do/pliki/*.md"

# Analiza z wyjściem szczegółowym
mdiss analyze plik.md --verbose

# Wyświetl podsumowanie
mdiss analyze plik.md --summary
```

#### Opcje analizy

```bash
# Zapis wyników do pliku JSON
mdiss analyze plik.md --output wyniki.json

# Filtrowanie wyników (więcej w sekcji Zaawansowane)
mdiss analyze plik.md --filter "status=failed"

# Ograniczenie liczby analizowanych błędów
mdiss analyze plik.md --limit 10
```

### Tworzenie zgłoszeń na GitHubie

#### Podstawowe tworzenie zgłoszeń

```bash
# Tworzenie zgłoszeń (wymaga konfiguracji tokenu)
mdiss create plik.md wlasciciel/rep

# Podgląd zgłoszeń bez ich tworzenia
mdiss create plik.md wlasciciel/rep --dry-run

# Określ etykiety dla zgłoszeń
mdiss create plik.md wlasciciel/rep --labels "bug,high-priority"
```

#### Opcje tworzenia zgłoszeń

```bash
# Użyj szablonu dla tytułu zgłoszenia
mdiss create plik.md wlasciciel/rep --title-template "[BUG] {category}: {command}"

# Użyj szablonu dla treści zgłoszenia
mdiss create plik.md wlasciciel/rep --body-template @szablon.md

# Otwórz przeglądarkę z podglądem zgłoszenia
mdiss create plik.md wlasciciel/rep --browser
```

### Konfiguracja

#### Plik konfiguracyjny

`mdiss` używa pliku konfiguracyjnego `~/.config/mdiss/config.toml` do przechowywania ustawień. Możesz go edytować ręcznie lub użyć interaktywnej konfiguracji:

```bash
# Interaktywna konfiguracja
mdiss config

# Wyświetl aktualną konfigurację
mdiss config --show
```

#### Przykładowa konfiguracja

```toml[general]
default_owner = "twoj-uzytkownik"
default_repo = "twoje-repo"

[github]
token = "twój-token-dostępu"

[create]
labels = ["bug", "automated"]
title_template = "[BUG] {category}: {command}"

[analyze]
output_format = "json"
verbose = false
```

## 🛠️ Zaawansowane użycie

### Filtrowanie wyników

Możesz filtrować wyniki analizy używając wyrażeń logicznych:

```bash
# Tylko błędy związane z zależnościami
mdiss analyze plik.md --filter "category == 'dependencies'"

# Błędy o wysokim priorytecie
mdiss analyze plik.md --filter "priority in ['high', 'critical']"

# Złożone warunki
mdiss analyze plik.md --filter "category == 'dependencies' and priority == 'high'"
```

### Dostosowywanie formatu wyjścia

#### Format JSON

```bash
# Pełne dane wyjściowe w formacie JSON
mdiss analyze plik.md --format json

# Wybierz konkretne pola do wyświetlenia
mdiss analyze plik.md --format json --fields command,status,priority
```

#### Format tabeli

```bash
# Domyślny widok tabeli
mdiss analyze plik.md --format table

# Dostosuj wyświetlane kolumny
mdiss analyze plik.md --format table --columns "Command,Status,Priority"
```

#### Format CSV

```bash
# Eksport do formatu CSV
mdiss analyze plik.md --format csv --output wyniki.csv
```

### Integracja z CI/CD

#### GitHub Actions

```yaml
name: Analiza błędów

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  analyze-errors:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install mdiss

      - name: Analyze errors
        run: |
          # Analizuj błędy i zapisz wyniki
          mdiss analyze errors/*.md --output analysis.json

          # Utwórz zgłoszenia na GitHubie
          mdiss create analysis.json ${{ github.repository }} \
            --token ${{ secrets.GITHUB_TOKEN }} \
            --labels "bug,automated"
```

## 🎯 Przykłady użycia

### Przykład 1: Analiza i raportowanie błędów

```bash
# Przeanalizuj błędy i wyświetl podsumowanie
mdiss analyze build_errors.md --summary

# Utwórz zgłoszenia dla błędów o wysokim priorytecie
mdiss create build_errors.md wronai/mdiss \
  --filter "priority in ['high', 'critical']" \
  --labels "bug,high-priority"
```

### Przykład 2: Integracja z potokiem CI

```bash
# W pliku .gitlab-ci.yml
analyze_errors:
  image: python:3.10
  script:
    - pip install mdiss
    - mdiss analyze test_results/*.md --output analysis.json
    - mdiss create analysis.json $CI_PROJECT_PATH \
        --token $GITLAB_TOKEN \
        --dry-run
```

## 🛠 Rozwiązywanie problemów

### Częste problemy i rozwiązania

#### Brak uprawnień do repozytorium

**Objawy:**
```
GitHubAPIError: 404 Not Found - Not Found
```

**Rozwiązanie:**
- Upewnij się, że token ma odpowiednie uprawnienia (`repo`)
- Sprawdź, czy nazwa właściciela i repozytorium są poprawne

#### Nieprawidłowy format pliku wejściowego

**Objawy:**
```
ParserError: Invalid markdown format
```

**Rozwiązanie:**
- Sprawdź, czy plik jest poprawnie sformatowany
- Użyj opcji `--verbose` aby uzyskać więcej szczegółów

#### Przekroczono limit zapytań do API GitHub

**Objawy:**
```
GitHubAPIError: 403 API rate limit exceeded
```

**Rozwiązanie:**
- Poczekaj chwilę i spróbuj ponownie
- Użyj osobistego tokenu dostępu z wyższym limitem
- Rozważ użycie opóźnienia między żądaniami: `--delay 2`

### Debugowanie

Aby uzyskać więcej informacji o błędach, użyj flagi `--debug`:

```bash
mdiss analyze plik.md --debug
```

## 📚 Dodatkowe zasoby

- [Dokumentacja API](api.md) - szczegółowy opis interfejsu programistycznego
- [Przykłady użycia](examples/) - gotowe przykłady i przypadki użycia
- [Wkład w rozwój](CONTRIBUTING.md) - jak przyczynić się do rozwoju projektu

---

💡 **Wskazówka:** Użyj `mdiss --help`, aby wyświetlić dostępne polecenia i opcje.

# Minimalny poziom pewności (0-1)
mdiss analyze plik.md --min-confidence 0.8
```

## Tworzenie zgłoszeń na GitHubie

### Konfiguracja tokenu

```bash
# Interaktywna konfiguracja
mdiss setup

# Ręczne ustawienie tokenu
export GITHUB_TOKEN="twój_token_github"
```

### Tworzenie zgłoszeń

```bash
# Podgląd zgłoszeń (bez tworzenia)
mdiss create plik.md wronai mdiss --dry-run

# Rzeczywiste utworzenie zgłoszeń
mdiss create plik.md wronai mdiss

# Z dodatkowymi opcjami
mdiss create plik.md wronai mdiss \
    --assignees "user1,user2" \
    --labels "bug,high" \
    --milestone "Sprint 1"
```

## Konfiguracja

### Plik konfiguracyjny

Stwórz plik `~/.mdiss/config.toml`:

```toml[github]
token = "twój_token_github"
log_level = "INFO"

github:
  default_owner = "wronai"
  default_repo = "mdiss"
  labels = ["bug", "enhancement"]
  assignees = ["twój_github_username"]
```

### Zmienne środowiskowe

```bash
# Wymagane
GITHUB_TOKEN=twój_token_github

# Opcjonalne
MDISS_LOG_LEVEL=INFO
MDISS_CONFIG=ścieżka/do/konfiguracji.toml
```

## Przykłady użycia

### Przykład 1: Analiza pojedynczego pliku

```bash
# Analiza pliku z błędami
mdiss analyze testy/bledy.md --output raport.json

# Podgląd raportu
cat raport.json | jq .
```

### Przykład 2: Automatyczne zgłaszanie błędów

```bash
# Znajdź pliki z błędami i stwórz zgłoszenia
find . -name "*.md" -type f -exec mdiss create {} wronai mdiss \;
```

### Przykład 3: Integracja z CI

```yaml
# .github/workflows/analyze.yml
name: Analiza błędów

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Ustaw Pythona
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Zainstaluj zależności
      run: |
        python -m pip install --upgrade pip
        pip install mdiss

    - name: Uruchom analizę
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        # Analizuj i twórz zgłoszenia
        mdiss create "**/failures/*.md" wronai mdiss \
          --assignees "${{ github.actor }}" \
          --labels "ci,automated"
```

## Integracja z CI/CD

### GitHub Actions

Dodaj następujący plik do `.github/workflows/analyze.yml`:

```yaml
name: Analiza błędów

on:
  workflow_run:
    workflows: ["Testy"]
    types: [completed]

jobs:
  analyze-failures:
    runs-on: ubuntu-latest
    if: >
      github.event.workflow_run.conclusion == 'failure' &&
      contains(github.event.workflow_run.head_commit.message, '[analyze]')

    steps:
    - uses: actions/checkout@v3

    - name: Uruchom analizę błędów
      uses: wronai/mdiss/action@v1
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        owner: wronai
        repo: mdiss
        path: '**/failures/*.md'
        assignees: ${{ github.actor }}
        labels: 'ci,automated'
```

### GitLab CI

```yaml
analyze:
  stage: test
  image: python:3.10
  script:
    - pip install mdiss
    - mdiss analyze "**/*.md" --output gl-dependency-scanning-report.json
  artifacts:
    reports:
      dependency_scanning: gl-dependency-scanning-report.json
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes:
        - "**/*.md"
        - ".gitlab-ci.yml"
```

## Rozwiązywanie problemów

### Błąd: Brak uprawnień

```
Error: 403 Forbidden - Missing or insufficient permissions.
```

Rozwiązanie:
1. Upewnij się, że token ma odpowiednie uprawnienia (`repo` i `write:issues`)
2. Sprawdź, czy token nie wygasł
3. Upewnij się, że masz uprawnienia do repozytorium

### Błąd: Nieprawidłowy format pliku

```
Error: Invalid markdown format
```

Rozwiązanie:
1. Sprawdź, czy plik istnieje i ma rozszerzenie .md
2. Upewnij się, że plik zawiera poprawne znaczniki markdown
3. Sprawdź kodowanie pliku (powinno być UTF-8)

## Pomoc

```bash
# Wyświetl pomoc
mdiss --help

# Pomoc dla konkretnej komendy
mdiss analyze --help
mdiss create --help
mdiss setup --help
```
            output="Running tests...",
            error_output="Test failed: assertion error in test_example.py",
            metadata={"target": "test"}
        )

        # Tworzenie issue (dry run)
        print(f"\n📝 Przykład issue dla: {failed_command.title}")

        # Analiza polecenia
        analyzer = ErrorAnalyzer()
        analysis = analyzer.analyze(failed_command)

        # Generowanie treści issue
        title = client._create_title(failed_command)
        body = client._create_body(failed_command, analysis)
        labels = client._create_labels(failed_command, analysis)

        print(f"Tytuł: {title}")
        print(f"Labele: {', '.join(labels)}")
        print(f"Treść (pierwsze 300 znaków):")
        print(body[:300] + "...")

    else:
        print("❌ Błąd połączenia z GitHub")


def example_4_statistics():
    """Przykład 4: Generowanie statystyk."""
    print("\n📊 Przykład 4: Statystyki")
    print("=" * 50)

    # Przykładowa lista poleceń
    commands = [
        FailedCommand(
            title="Make Install", command="make install", source="/test/Makefile",
            command_type="make_target", status="Failed", return_code=2,
            execution_time=1.5, output="", error_output="poetry.lock error", metadata={}
        ),
        FailedCommand(
            title="NPM Test", command="npm test", source="/test/package.json",
            command_type="npm_script", status="Failed", return_code=1,
            execution_time=3.2, output="", error_output="test failed", metadata={}
        ),
        FailedCommand(
            title="Timeout Command", command="long_process", source="/test/script.sh",
            command_type="shell", status="Failed", return_code=-1,
            execution_time=60.0, output="", error_output="timeout", metadata={}
        ),
    ]

    # Generowanie statystyk
    parser = MarkdownParser()
    stats = parser.get_statistics(commands)

    print("Statystyki poleceń:")
    print(f"  • Całkowita liczba: {stats['total_commands']}")
    print(f"  • Średni czas wykonania: {stats['average_execution_time']}s")
    print(f"  • Timeout'y: {stats['timeout_count']}")
    print(f"  • Krytyczne błędy: {stats['critical_count']}")

    print("\nTypy poleceń:")
    for cmd_type, count in stats['command_types'].items():
        print(f"  • {cmd_type}: {count}")

    print("\nKody błędów:")
    for code, count in stats['return_codes'].items():
        print(f"  • {code}: {count}")


def example_5_batch_processing():
    """Przykład 5: Przetwarzanie wsadowe."""
    print("\n⚡ Przykład 5: Przetwarzanie wsadowe")
    print("=" * 50)

    # Symulacja wielu plików
    markdown_files = [
        "../tests/fixtures/sample_markdown.md",
        # Można dodać więcej plików
    ]

    all_commands = []
    parser = MarkdownParser()

    for file_path in markdown_files:
        if Path(file_path).exists():
            try:
                commands = parser.parse_file(file_path)
                all_commands.extend(commands)
                print(f"✅ {file_path}: {len(commands)} poleceń")
            except Exception as e:
                print(f"❌ {file_path}: {e}")
        else:
            print(f"⏭️  Pomijam nieistniejący plik: {file_path}")

    print(f"\nŁącznie znaleziono: {len(all_commands)} poleceń")

    # Grupowanie według typu
    by_type = {}
    for cmd in all_commands:
        cmd_type = cmd.command_type
        if cmd_type not in by_type:
            by_type[cmd_type] = []
        by_type[cmd_type].append(cmd)

    print("\nGrupowanie według typu:")
    for cmd_type, commands in by_type.items():
        print(f"  • {cmd_type}: {len(commands)} poleceń")


def example_6_custom_analysis():
    """Przykład 6: Własna analiza błędów."""
    print("\n🔧 Przykład 6: Własna analiza błędów")
    print("=" * 50)

    # Własna funkcja analizy
    def custom_analyze_command(command: FailedCommand) -> str:
        """Własna logika analizy polecenia."""
        if "poetry" in command.error_output.lower():
            return "🐍 Problem z Poetry - sprawdź pyproject.toml i poetry.lock"
        elif "npm" in command.error_output.lower():
            return "📦 Problem z NPM - sprawdź package.json i node_modules"
        elif command.return_code == -1:
            return "⏰ Timeout - polecenie się zawiesiło"
        elif "permission" in command.error_output.lower():
            return "🔒 Problem z uprawnieniami"
        else:
            return "❓ Nieznany błąd - wymagana ręczna analiza"

    # Przykładowe polecenia
    test_commands = [
        FailedCommand(
            title="Poetry Error", command="poetry install", source="/test",
            command_type="poetry", status="Failed", return_code=1,
            execution_time=1.0, output="", error_output="poetry.lock is outdated", metadata={}
        ),
        FailedCommand(
            title="NPM Error", command="npm run build", source="/test",
            command_type="npm", status="Failed", return_code=1,
            execution_time=2.0, output="", error_output="npm ERR! Cannot find module", metadata={}
        ),
    ]

    # Analiza z własną funkcją
    for cmd in test_commands:
        analysis = custom_analyze_command(cmd)
        print(f"• {cmd.title}: {analysis}")


def main():
    """Uruchamia wszystkie przykłady."""
    print("🚀 mdiss - Przykłady użycia API")
    print("=" * 60)

    try:
        example_1_basic_parsing()
        example_2_error_analysis()
        example_3_github_integration()
        example_4_statistics()
        example_5_batch_processing()
        example_6_custom_analysis()

        print("\n✅ Wszystkie przykłady zakończone!")
        print("\n📚 Zobacz więcej przykładów w dokumentacji:")
        print("   https://wronai.github.io/mdiss")

    except Exception as e:
        print(f"\n❌ Błąd podczas wykonywania przykładów: {e}")
        print("Upewnij się, że:")
        print("- mdiss jest zainstalowany: pip install mdiss")
        print("- Pliki testowe istnieją")
        print("- GitHub token jest poprawny (dla przykładu 3)")


if __name__ == "__main__":
    main()
