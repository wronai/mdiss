# mdiss - Markdown Issues

[![PyPI version](https://img.shields.io/pypi/v/mdiss.svg?style=for-the-badge&color=blue)](https://pypi.org/project/mdiss/)
[![Python Version](https://img.shields.io/pypi/pyversions/mdiss.svg?style=for-the-badge)](https://pypi.org/project/mdiss/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://img.shields.io/github/actions/workflow/status/wronai/mdiss/ci.yml?branch=main&label=Tests&style=for-the-badge)](https://github.com/wronai/mdiss/actions)
[![Documentation](https://img.shields.io/readthedocs/mdiss/latest?style=for-the-badge)](https://mdiss.readthedocs.io/)
[![Ollama](https://img.shields.io/badge/Ollama-Enabled-7c3aed?style=for-the-badge)](https://ollama.ai/)
[![GitLab](https://img.shields.io/badge/GitLab-Integrated-FC6D26?style=for-the-badge&logo=gitlab&logoColor=white)](https://gitlab.com/)

[![PyPI version](https://img.shields.io/pypi/v/mdiss.svg?style=for-the-badge&color=blue)](https://pypi.org/project/mdiss/)
[![Python Version](https://img.shields.io/pypi/pyversions/mdiss.svg?style=for-the-badge)](https://pypi.org/project/mdiss/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://img.shields.io/github/actions/workflow/status/wronai/mdiss/ci.yml?branch=main&label=Tests&style=for-the-badge)](https://github.com/wronai/mdiss/actions)
[![Documentation](https://img.shields.io/readthedocs/mdiss/latest?style=for-the-badge)](https://mdiss.readthedocs.io/)

> Advanced markdown processing and issue management with GitHub/GitLab integration and AI-powered ticket generation.

## 🚀 Features

- **Local LLM Integration** - Generate tickets using local models via Ollama
- **Dual Platform Support** - Native integration with both GitHub and GitLab
- **Advanced Markdown Processing** - Parse and manipulate markdown content with ease
- **AI-Powered Ticket Generation** - Automatically generate well-structured tickets
- **Comprehensive API** - Programmatic access to all features
- **Flexible Configuration** - Customize behavior to fit your workflow
- **Safe Operations** - Dry-run mode to preview changes before applying them

## 📖 About the Project

**mdiss** is a powerful tool for processing markdown files and managing issues across multiple platforms. It provides advanced markdown parsing, seamless integration with GitHub and GitLab, and AI-powered ticket generation for better issue management.

### Key Features:

- **Advanced Markdown Processing** - Parse and manipulate markdown content with ease
- **Dual Platform Support** - Native integration with both GitHub and GitLab
- **AI-Powered Ticket Generation** - Automatically generate well-structured tickets using AI
- **Comprehensive API** - Programmatic access to all features
- **Flexible Configuration** - Customize behavior to fit your workflow
- **Safe Operations** - Dry-run mode to preview changes before applying them

## 🤖 Local LLM Integration

mdiss now supports local Large Language Models (LLMs) via Ollama, allowing you to generate tickets without relying on external APIs. This feature uses the Mistral 7B model by default but can be configured to use other models.

### Prerequisites

1. Install [Ollama](https://ollama.ai/) on your system
2. Pull the desired model (e.g., `ollama pull mistral:7b`)

### Quick Start with Local LLM

```bash
# Start Ollama server (in a separate terminal)
make llm-serve

# Pull the default model (Mistral 7B)
make llm-pull

# Test the LLM integration
make llm-test
```

### Available Make Commands

| Command | Description |
|---------|-------------|
| `make llm-serve` | Start Ollama server in the background |
| `make llm-pull` | Download the default Mistral 7B model |
| `make llm-list` | List available Ollama models |
| `make llm-test` | Test the LLM integration with sample ticket generation |

### Using Custom Models

You can use any model available in Ollama by specifying it when initializing the ticket generator:

```python
from mdiss.ai.ticket_generator import AITicketGenerator

# Initialize with a custom model
generator = AITicketGenerator(model="llama2")

# Generate a ticket
ticket = generator.generate_ticket(
    title="Fix login issues",
    description="Users are experiencing problems with the login form"
)
```

## 🔧 Prerequisites

- Python 3.9+
- [Ollama](https://ollama.ai/) installed and running
- GitLab API token (for GitLab integration)
- GitHub token (for GitHub integration)

## 🚀 Quick Start

### 🛠 Installation

1. Install the package with AI support:
   ```bash
   pip install mdiss[ai] ollama
   ```

2. Install Ollama and pull the desired model (e.g., Mistral 7B):
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull mistral:7b
   ```

3. Start the Ollama server (if not already running):
   ```bash
   make llm-serve
   ```

### 🔌 GitLab Integration

1. Create a GitLab Personal Access Token with `api` scope
2. Configure your environment:
   ```bash
   export GITLAB_TOKEN="your-gitlab-token"
   export GITLAB_URL="https://gitlab.com"  # or your self-hosted GitLab URL
   ```

3. Test the integration:
   ```python
   from mdiss.integrations.gitlab_integration import GitLabIntegration

   gitlab = GitLabIntegration(token="your-gitlab-token")
   projects = gitlab.list_projects()
   print(f"Available projects: {[p.name for p in projects]}")
   ```

### 🤖 Local LLM Usage

```python
from mdiss.ai.ticket_generator import AITicketGenerator

# Initialize with default model (mistral:7b)
generator = AITicketGenerator()

# Generate a ticket
ticket = generator.generate_ticket(
    title="Fix login issues",
    description="Users cannot log in on mobile devices"
)

print(ticket)
```

### 📝 Makefile Commands

| Command | Description |
|---------|-------------|
| `make llm-serve` | Start Ollama server if not running |
| `make llm-pull` | Download Mistral 7B model |
| `make llm-list` | List available Ollama models |
| `make llm-test` | Test LLM integration |

## 📚 Documentation

For detailed documentation, see:

- [LLM Integration Guide](docs/llm_integration.md)
- [GitLab Integration Guide](docs/gitlab_integration.md)
- [API Reference](docs/api.md)

## 🚀 Quick Start

### Installation

```bash
# Install the package
pip install mdiss

# Install with optional dependencies for AI features
pip install mdiss[ai]

# Or install from source
git clone https://github.com/wronai/mdiss.git
cd mdiss
pip install -e .[dev,ai]
pip install mdiss[ai] ollama
```

### Podstawowe użycie

1. **Skonfiguruj dostęp do GitHub**
   ```bash
   mdiss setup
   ```

2. **Przeanalizuj plik z błędami**
   ```bash
   mdiss analyze errors.md
   ```

3. **Utwórz zgłoszenia (w trybie testowym)**
   ```bash
   mdiss create errors.md twój-uzytkownik/twoje-repo --dry-run
   ```

4. **Gdy wszystko wygląda dobrze, wyślij zgłoszenia**
   ```bash
   mdiss create errors.md twój-uzytkownik/twoje-repo
   ```

## 📚 Documentation

### Local LLM Configuration

1. **Environment Variables**
   ```bash
   # Set Ollama base URL (default: http://localhost:11434)
   export OLLAMA_BASE_URL="http://localhost:11434"

   # Set default model (default: mistral:7b)
   export DEFAULT_LLM_MODEL="mistral:7b"
   ```

2. **Using with GitHub/GitLab**
   ```python
   from mdiss.ticket_manager import TicketManager

   # Initialize with local LLM
   manager = TicketManager(
       markdown_path="todos.md",
       provider="github",
       llm_model="mistral:7b",  # Optional: specify model
       ollama_host="http://localhost:11434"  # Optional: specify Ollama host
   )

   # Generate and create tickets
   tickets = manager.extract_tickets()
   for ticket in tickets:
       manager.create_ticket(ticket)
   ```

## 📚 Dokumentacja

Pełna dokumentacja dostępna jest w katalogu [docs/](docs/):

- [Instalacja](docs/installation.md) - szczegółowe instrukcje instalacji
- [Użycie](docs/usage.md) - pełny przewodnik po funkcjach
- [API](docs/api.md) - dokumentacja interfejsu programistycznego
- [Wkład w rozwój](CONTRIBUTING.md) - jak współtworzyć projekt

## 👥 Autorzy

Projekt jest rozwijany przez zespół [wronai](https://github.com/wronai).

## 📄 Licencja

Projekt jest dostępny na licencji [Apache 2.0](LICENSE).

### Z kodu źródłowego
```bash
git clone https://github.com/wronai/mdiss.git
cd mdiss
poetry install
```

### Rozwój i wkład

#### Konfiguracja środowiska deweloperskiego

```bash
# Sklonuj repozytorium
git clone https://github.com/wronai/mdiss.git
cd mdiss

# Zainstaluj zależności deweloperskie
make dev

# Zainstaluj pre-commit hooks
make install-hooks
```

#### Dostępne polecenia Makefile

```bash
# Instalacja i konfiguracja
make install      # Zainstaluj podstawowe zależności
make dev          # Zainstaluj zależności deweloperskie
make install-hooks # Zainstaluj git hooks

# Testowanie
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

# Demo
make demo          # Uruchom demo z przykładowym plikiem
make demo-create   # Demo tworzenia issues (dry run)
```

#### Workflow deweloperski

1. Zainstaluj zależności:
   ```bash
   make dev
   make install-hooks
   ```

2. Pracuj nad nową funkcjonalnością w osobnym branchu:
   ```bash
   git checkout -b feature/nazwa-funkcjonalnosci
   ```

3. Przed commitem uruchom testy i sprawdzenia jakości:
   ```bash
   make qa
   ```
   Lub ręcznie:
   ```bash
   make format
   make lint
   make test
   ```

4. Zatwierdź zmiany i wyślij do repozytorium

5. Stwórz Pull Request na GitHubie

6. Po zaakceptowaniu PR, zaktualizuj wersję i opublikuj zmiany:
   ```bash
   make version-patch  # lub version-minor/version-major
   make publish
   make docs-deploy
   ```

## 🚀 Szybki start

### Analiza pliku markdown

```bash
# Analiza pliku
mdiss analyze TODO.md

# Zapis wyników do pliku JSON
mdiss analyze TODO.md --output wyniki.json

# Analiza z dodatkowymi informacjami debugowymi
mdiss analyze TODO.md --verbose
```

### Tworzenie zgłoszeń na GitHubie

```bash
# Podgląd zgłoszeń (bez tworzenia)
mdiss create TODO.md wronai mdiss --dry-run

# Rzeczywiste utworzenie zgłoszeń
mdiss create plik.md wronai mdiss

# Z określonymi przypisaniami i etykietami
mdiss create plik.md wronai mdiss --assignees "user1,user2" --labels "bug,high"
```

### Zarządzanie konfiguracją

```bash
# Konfiguracja tokenu GitHub
mdiss setup

# Wyświetl aktualną konfigurację
mdiss config show
```

## 📖 Szczegółowe użycie

### 1. Konfiguracja

```bash
# Interaktywna konfiguracja tokenu GitHub
mdiss setup
```

Automatycznie otworzy stronę GitHub z formularzem generowania tokenu z odpowiednimi uprawnieniami:
- `repo` - dostęp do repozytoriów
- `write:issues` - tworzenie issues

### 2. Analiza pliku markdown

```bash
# Podstawowa analiza
mdiss analyze paste.txt

# Eksport do różnych formatów
mdiss export paste.txt --format json --output data.json
mdiss export paste.txt --format csv --output data.csv
```

### 3. Tworzenie issues

```bash
# Dry run (tylko podgląd)
mdiss create TODO.md wronai mdiss --dry-run

# Tworzenie z tokenem z pliku
mdiss create paste.txt wronai mdiss --token-file .mdiss_token

# Z dodatkowymi opcjami
mdiss create paste.txt wronai mdiss \
    --assignees "user1,user2" \
    --milestone 5 \
    --skip-existing
```

### 4. Zarządzanie issues

```bash
# Lista issues w repozytorium
mdiss list-issues wronai mdiss

# Z filtrami
mdiss list-issues owner repo --state closed --labels "bug,high"
```

## 📊 Analiza błędów

mdiss automatycznie kategoryzuje błędy i określa priorytety:

### Kategorie błędów

| Kategoria | Opis | Przykład |
|-----------|------|----------|
| `dependencies` | Problemy z zależnościami | Poetry lock file issues |
| `missing-files` | Brakujące pliki | package.json not found |
| `permissions` | Problemy z uprawnieniami | Cannot install --user in venv |
| `timeout` | Przekroczenie czasu | Command timed out |
| `syntax` | Błędy składni | YAML parsing errors |
| `configuration` | Problemy konfiguracji | Invalid config files |

### Priorytety
- **CRITICAL** - Segmentation faults, krytyczne błędy systemu
- **HIGH** - Timeouts, problemy z dependencies
- **MEDIUM** - Standardowe błędy, brakujące pliki
- **LOW** - Drobne problemy

### Sugestie rozwiązań

Dla każdej kategorii mdiss generuje konkretne kroki naprawy:

```markdown
**Rozwiązanie problemu z zależnościami:**

1. **Aktualizacja lock file:**
   ```bash
   poetry lock --no-update
   poetry install
   ```

2. **Jeśli nadal problemy:**
   ```bash
   poetry lock
   poetry install --sync
   ```
```

## 🔧 Format pliku markdown

mdiss rozpoznaje pliki w formacie:

```markdown
## X. Nazwa polecenia

**Command:** `polecenie`
**Source:** ścieżka/do/pliku
**Type:** typ_polecenia
**Status:** ❌ Failed
**Return Code:** kod_błędu
**Execution Time:** czas_w_sekundach

**Output:**
```
standardowy output
```

**Error Output:**
```
komunikaty błędów
```

**Metadata:**
- **klucz1:** wartość1
- **klucz2:** wartość2

---
```

## 🏷️ Przykład wygenerowanego issue

**Tytuł:** `Fix failed command: Make target: install`

**Treść:**
```markdown
## Problem Description
Command `make install` is failing consistently.

**Priority**: HIGH
**Category**: dependencies
**Confidence**: 90%

### Error Analysis
🔍 **Root Cause**: Poetry lock file is out of sync with pyproject.toml...

### Suggested Solution
1. Run `poetry lock` to regenerate the lock file
2. Run `poetry install` to install dependencies
3. Commit the updated poetry.lock file

### Labels
- bug
- high
- dependencies
- make_target
```

## 🛡️ Bezpieczeństwo

- Token GitHub przechowywany lokalnie w pliku `.mdiss_token`
- Automatyczna walidacja uprawnień
- Opcja dry-run do bezpiecznego testowania
- Nie przesyła wrażliwych danych

## 🔄 Workflow CI/CD

mdiss doskonale integruje się z CI/CD:

```yaml
# .github/workflows/issues.yml
name: Auto Issues
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]

jobs:
  create-issues:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install mdiss
        run: pip install mdiss
      - name: Create issues from failures
        run: |
          mdiss create failure_report.md ${{ github.repository_owner }} ${{ github.event.repository.name }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 🤝 Programowy API

```python
from mdiss import MarkdownParser, GitHubClient, ErrorAnalyzer
from mdiss.models import GitHubConfig

# Parsowanie pliku
parser = MarkdownParser()
commands = parser.parse_file("paste.txt")

# Analiza błędów
analyzer = ErrorAnalyzer()
for cmd in commands:
    analysis = analyzer.analyze(cmd)
    print(f"Priority: {analysis.priority.value}")
    print(f"Category: {analysis.category.value}")

# Tworzenie issues
config = GitHubConfig(token="...", owner="...", repo="...")
client = GitHubClient(config)

for cmd in commands:
    issue = client.create_issue_from_command(cmd)
    print(f"Created: {issue['html_url']}")
```

## 📁 Struktura projektu

```
mdiss/
├── mdiss/              # Kod źródłowy
│   ├── __init__.py
│   ├── cli.py         # CLI interface
│   ├── parser.py      # Markdown parser
│   ├── github_client.py  # GitHub API
│   ├── analyzer.py    # Error analyzer
│   └── models.py      # Data models
├── tests/             # Testy
├── docs/              # Dokumentacja
└── examples/          # Przykłady
```

## 🧪 Development

```bash
# Klonowanie
git clone https://github.com/wronai/mdiss.git
cd mdiss

# Instalacja zależności deweloperskich
make dev

# Uruchomienie testów
make test

# Sprawdzenie jakości kodu
make lint

# Formatowanie kodu
make format

# Pełny CI pipeline
make ci
```

### Dostępne komendy make

```bash
make help           # Pokaż wszystkie dostępne komendy
make test           # Uruchom testy
make test-coverage  # Testy z pokryciem kodu
make lint           # Sprawdź jakość kodu
make format         # Sformatuj kod
make build          # Zbuduj pakiet
make docs           # Zbuduj dokumentację
make demo           # Uruchom demo
```

## 📄 Licencja

Apache-2.0 License - zobacz [LICENSE](LICENSE)

## 🤝 Współpraca

1. Fork projektu
2. Stwórz branch dla swojej funkcji (`git checkout -b feature/amazing-feature`)
3. Commit zmian (`git commit -m 'Add amazing feature'`)
4. Push do brancha (`git push origin feature/amazing-feature`)
5. Otwórz Pull Request

### Guidelines

- Dodaj testy dla nowych funkcji
- Zachowaj 100% pokrycie kodu testami
- Używaj konwencjonalnych commitów
- Aktualizuj dokumentację

## 📈 Statystyki

- 🐍 Python 3.8+
- 📦 Zbudowany z Poetry
- 🧪 100% pokrycie testami
- 📖 Kompletna dokumentacja
- 🚀 Rich CLI interface

## 🔗 Linki

- [Dokumentacja](https://wronai.github.io/mdiss)
- [PyPI](https://pypi.org/project/mdiss/)
- [GitHub](https://github.com/wronai/mdiss)
- [Issues](https://github.com/wronai/mdiss/issues)

---

**Stworzone przez [WRONAI Team](https://github.com/wronai)** ❤️
