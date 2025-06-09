# Dokumentacja API

## MarkdownParser

Klasa odpowiedzialna za parsowanie plików markdown i wyodrębnianie nieudanych poleceń.

### Metody

#### `parse_file(file_path: str) -> List[FailedCommand]`

Parsuje plik markdown i zwraca listę nieudanych poleceń.

**Parametry:**
- `file_path` - Ścieżka do pliku markdown

**Zwraca:**
- Lista obiektów `FailedCommand`

**Przykład:**
```python
from mdiss import MarkdownParser

parser = MarkdownParser()
commands = parser.parse_file("failures.md")
```

---

## ErrorAnalyzer

Klasa analizująca błędy w nieudanych poleceniach i sugerująca rozwiązania.

### Metody

#### `analyze(command: FailedCommand) -> ErrorAnalysis`

Analizuje pojedyncze nieudane polecenie.

**Parametry:**
- `command` - Obiekt `FailedCommand` do analizy

**Zwraca:**
- Obiekt `ErrorAnalysis` zawierający szczegóły analizy

**Przykład:**
```python
from mdiss import ErrorAnalyzer, FailedCommand

analyzer = ErrorAnalyzer()
analysis = analyzer.analyze(failed_command)
print(f"Kategoria: {analysis.category}")
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