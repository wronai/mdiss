# 📚 Dokumentacja API

Ten dokument zawiera szczegółowy opis interfejsu programistycznego (API) biblioteki `mdiss`.

## Spis treści

- [MarkdownParser](#markdownparser) - Parser plików markdown
- [ErrorAnalyzer](#erroranalyzer) - Analiza błędów i sugestie rozwiązań
- [GitHubClient](#githubclient) - Integracja z GitHub API
- [Modele danych](#modele-danych) - Opis struktur danych
- [Wyjątki](#wyjątki) - Dokumentacja wyjątków

## MarkdownParser

Klasa odpowiedzialna za parsowanie plików markdown i wyodrębnianie nieudanych poleceń.

```python
from mdiss.parser import MarkdownParser

# Inicjalizacja parsera
parser = MarkdownParser()
```

### Metody

#### `parse_file(file_path: str) -> List[CommandData]`

Parsuje plik markdown i zwraca listę znalezionych poleceń.

**Parametry:**
- `file_path` (str) - Ścieżka do pliku markdown

**Zwraca:**
- `List[CommandData]` - Lista obiektów reprezentujących znalezione polecenia

**Przykład:**
```python
commands = parser.parse_file("failures.md")
for cmd in commands:
    print(f"Komenda: {cmd.command}")
    print(f"Status: {cmd.status}")
    print(f"Kod błędu: {cmd.return_code}")
```

#### `parse_content(content: str) -> List[Dict[str, str]]`

Parsuje zawartość markdown przekazaną jako ciąg znaków.

**Parametry:**
- `content` (str) - Zawartość markdown do przeanalizowania

**Zwraca:**
- `List[Dict[str, str]]` - Lista słowników zawierających znalezione bloki kodu

**Przykład:**
```python
content = """
```bash
echo "Test"
```
"""
blocks = parser.parse_content(content)
```

## ErrorAnalyzer

Klasa analizująca błędy w nieudanych poleceniach i sugerująca rozwiązania.

```python
from mdiss.analyzer import ErrorAnalyzer

# Inicjalizacja analizatora
analyzer = ErrorAnalyzer()
```

### Metody

#### `analyze(command: CommandData) -> ErrorAnalysis`

Analizuje pojedyncze nieudane polecenie.

**Parametry:**
- `command` (CommandData) - Obiekt polecenia do analizy

**Zwraca:**
- `ErrorAnalysis` - Obiekt zawierający szczegóły analizy błędu

**Przykład:**
```python
analysis = analyzer.analyze(failed_command)
print(f"Kategoria błędu: {analysis.category}")
print(f"Prawdopodobieństwo: {analysis.confidence}")
print(f"Sugerowane rozwiązanie: {analysis.suggested_solution}")
```

#### `get_statistics(commands: List[CommandData]) -> Dict[str, Any]`

Generuje statystyki na podstawie listy poleceń.

**Parametry:**
- `commands` (List[CommandData]) - Lista poleceń do analizy

**Zwraca:**
- `Dict[str, Any]` - Słownik ze statystykami

**Przykład:**
```python
stats = analyzer.get_statistics(commands)
print(f"Liczba błędów: {stats['failed_commands']}")
print(f"Wskaźnik powodzenia: {stats['success_rate']:.1%}")
```

## GitHubClient

Klasa do komunikacji z API GitHub w celu tworzenia i zarządzania zgłoszeniami.

```python
from mdiss.github import GitHubClient, GitHubConfig

# Konfiguracja klienta
config = GitHubConfig(
    token="your_github_token",
    owner="repo_owner",
    repo="repo_name"
)
client = GitHubClient(config)
```

### Metody

#### `create_issue(title: str, body: str, labels: List[str] = None) -> Dict`

Tworzy nowe zgłoszenie (issue) na GitHubie.

**Parametry:**
- `title` (str) - Tytuł zgłoszenia
- `body` (str) - Treść zgłoszenia
- `labels` (List[str], opcjonalne) - Etykiety do przypisania do zgłoszenia

**Zwraca:**
- `Dict` - Odpowiedź z API GitHub

**Przykład:**
```python
issue = client.create_issue(
    title="Naprawić błąd w module X",
    body="Opis błędu...",
    labels=["bug", "high-priority"]
)
```

## Modele danych

### CommandData

Klasa reprezentująca pojedyncze polecenie wyodrębnione z pliku markdown.

**Atrybuty:**
- `command` (str) - Treść polecenia
- `status` (str) - Status wykonania (np. "Failed", "Success")
- `return_code` (int) - Kod zwracany przez polecenie
- `output` (str) - Standardowe wyjście polecenia
- `error_output` (str) - Wyjście błędów polecenia
- `metadata` (Dict[str, Any]) - Dodatkowe metadane

### ErrorAnalysis

Wynik analizy błędu.

**Atrybuty:**
- `category` (str) - Kategoria błędu
- `confidence` (float) - Pewność analizy (0.0 - 1.0)
- `suggested_solution` (str) - Sugerowane rozwiązanie
- `priority` (str) - Sugerowany priorytet ("low", "medium", "high", "critical")

## Wyjątki

### ParserError

Wyjątek zgłaszany w przypadku błędu podczas parsowania pliku markdown.

**Atrybuty:**
- `message` (str) - Komunikat błędu
- `file_path` (str, opcjonalnie) - Ścieżka do pliku, który spowodował błąd

### GitHubAPIError

Wyjątek zgłaszany w przypadku błędu podczas komunikacji z API GitHub.

**Atrybuty:**
- `status_code` (int) - Kod odpowiedzi HTTP
- `response` (Dict) - Pełna odpowiedź z API
- `message` (str) - Komunikat błędu
print(f"Priorytet: {analysis.priority}")
print(f"Sugerowane rozwiązanie: {analysis.suggested_solution}")
```

---

## GitHubClient

Klasa do integracji z API GitHub do zarządzania zgłoszeniami.

### Metody

#### `__init__(self, config: GitHubConfig)`

Inicjalizuje klienta GitHub.

**Parametry:**
- `config` - Obiekt konfiguracyjny `GitHubConfig`

#### `create_issue(self, command: FailedCommand) -> Optional[Dict]`

Tworzy nowe zgłoszenie na GitHubie na podstawie nieudanego polecenia.

**Parametry:**
- `command` - Obiekt `FailedCommand`

**Zwraca:**
- Słownik z odpowiedzią z API GitHub lub None w przypadku błędu

**Przykład:**
```python
from mdiss import GitHubClient, GitHubConfig

config = GitHubConfig(
    token="your_github_token",
    owner="wronai",
    repo="mdiss"
)
client = GitHubClient(config)
issue = client.create_issue(failed_command)
```

#### `test_connection(self) -> bool`

Testuje połączenie z GitHub API.

**Zwraca:**
- `True` jeśli połączenie powiodło się, w przeciwnym razie `False`

---

## Modele danych

### `FailedCommand`

Reprezentuje nieudane polecenie wyodrębnione z pliku markdown.

**Atrybuty:**
- `title` - Tytuł błędu
- `command` - Treść polecenia
- `source` - Źródło (ścieżka do pliku)
- `command_type` - Typ polecenia
- `status` - Status wykonania
- `return_code` - Kod powrotu
- `execution_time` - Czas wykonania w sekundach
- `output` - Standardowe wyjście
- `error_output` - Wyjście błędów
- `metadata` - Dodatkowe metadane

### `ErrorAnalysis`

Wynik analizy błędu.

**Atrybuty:**
- `category` - Kategoria błędu
- `priority` - Priorytet (CRITICAL, HIGH, MEDIUM, LOW)
- `confidence` - Pewność analizy (0-1)
- `root_cause` - Zidentyfikowana przyczyna błędu
- `suggested_solution` - Sugerowane rozwiązanie

### `GitHubConfig`

Konfiguracja połączenia z GitHub.

**Atrybuty:**
- `token` - Token dostępu GitHub
- `owner` - Właściciel repozytorium
- `repo` - Nazwa repozytorium
- `labels` - Lista etykiet do przypisania do zgłoszeń
- `assignees` - Lista osób do przypisania zgłoszeń
