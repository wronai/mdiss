# Użycie mdiss

## Spis treści
- [Podstawowe użycie](#podstawowe-użycie)
- [Analiza plików markdown](#analiza-plików-markdown)
- [Tworzenie zgłoszeń na GitHubie](#tworzenie-zgłoszeń-na-githubie)
- [Konfiguracja](#konfiguracja)
- [Przykłady użycia](#przykłady-użycia)
- [Integracja z CI/CD](#integracja-z-cicd)

## Podstawowe użycie

### Instalacja

```bash
# Instalacja z PyPI
pip install mdiss

# Wersja deweloperska
pip install git+https://github.com/wronai/mdiss.git
```

### Sprawdzenie wersji

```bash
mdiss --version
```

## Analiza plików markdown

### Podstawowa analiza

```bash
# Analiza pojedynczego pliku
mdiss analyze sciezka/do/pliku.md

# Analiza wielu plików
mdiss analyze "sciezka/do/pliki/*.md"

# Wyświetl szczegółowe informacje
mdiss analyze plik.md --verbose
```

### Opcje analizy

```bash
# Zapis wyników do pliku JSON
mdiss analyze plik.md --output wyniki.json

# Filtrowanie po typie błędu
mdiss analyze plik.md --filter "category=dependencies"

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