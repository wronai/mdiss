"""
Analizator błędów dla określania priorytetów, kategorii i sugestii rozwiązań.
"""

from typing import Dict, List
import re

from .models import FailedCommand, Priority, Category, AnalysisResult


class ErrorAnalyzer:
    """Analizator błędów w poleceniach."""

    def __init__(self):
        self.priority_rules = self._build_priority_rules()
        self.category_rules = self._build_category_rules()
        self.solution_templates = self._build_solution_templates()

    def analyze(self, command: FailedCommand) -> AnalysisResult:
        """
        Analizuje nieudane polecenie i zwraca wynik analizy.

        Args:
            command: Obiekt FailedCommand do analizy

        Returns:
            AnalysisResult z priorytetem, kategorią i sugestiami
        """
        priority = self._determine_priority(command)
        category = self._determine_category(command)
        root_cause = self._analyze_root_cause(command)
        solution = self._suggest_solution(command, category)
        confidence = self._calculate_confidence(command, category)

        return AnalysisResult(
            priority=priority,
            category=category,
            root_cause=root_cause,
            suggested_solution=solution,
            confidence=confidence,
        )

    def _build_priority_rules(self) -> List[Dict]:
        """Buduje reguły określania priorytetu."""
        return [
            {
                "condition": lambda cmd: cmd.is_timeout,
                "priority": Priority.HIGH,
                "reason": "Command timeout"
            },
            {
                "condition": lambda cmd: cmd.is_critical,
                "priority": Priority.CRITICAL,
                "reason": "Critical system error"
            },
            {
                "condition": lambda cmd: "poetry.lock" in cmd.error_output.lower(),
                "priority": Priority.HIGH,
                "reason": "Dependency lock file issue"
            },
            {
                "condition": lambda cmd: "segmentation fault" in cmd.error_output.lower(),
                "priority": Priority.CRITICAL,
                "reason": "Segmentation fault"
            },
            {
                "condition": lambda cmd: cmd.return_code in [2, 1],
                "priority": Priority.MEDIUM,
                "reason": "Standard error code"
            },
            {
                "condition": lambda cmd: "not found" in cmd.error_output.lower(),
                "priority": Priority.MEDIUM,
                "reason": "Missing dependency or file"
            },
        ]

    def _build_category_rules(self) -> List[Dict]:
        """Buduje reguły kategoryzacji błędów."""
        return [
            {
                "patterns": [r"poetry\.lock", r"pyproject\.toml", r"requirements\.txt"],
                "category": Category.DEPENDENCIES,
            },
            {
                "patterns": [r"not found", r"enoent", r"no such file"],
                "category": Category.MISSING_FILES,
            },
            {
                "patterns": [r"permission denied", r"cannot.*--user", r"not visible in.*virtualenv"],
                "category": Category.PERMISSIONS,
            },
            {
                "patterns": [r"timeout", r"timed out", r"killed"],
                "category": Category.TIMEOUT,
            },
            {
                "patterns": [r"syntax error", r"parse.*error", r"yaml.*constructor", r"invalid.*syntax"],
                "category": Category.SYNTAX,
            },
            {
                "patterns": [r"config", r"settings", r"\.cfg", r"\.ini"],
                "category": Category.CONFIGURATION,
            },
        ]

    def _build_solution_templates(self) -> Dict[Category, str]:
        """Buduje szablony rozwiązań dla kategorii."""
        return {
            Category.DEPENDENCIES: """
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

3. **Sprawdź konflikty:**
   ```bash
   poetry show --outdated
   poetry update
   ```
""",
            Category.MISSING_FILES: """
**Rozwiązanie problemu z brakującymi plikami:**

1. **Sprawdź ścieżkę:**
   - Upewnij się, że jesteś w odpowiednim katalogu
   - Sprawdź czy plik rzeczywiście istnieje

2. **Dla package.json:**
   ```bash
   npm init -y  # Jeśli brak package.json
   ```

3. **Sprawdź .gitignore:**
   - Możliwe że plik jest ignorowany przez git
""",
            Category.PERMISSIONS: """
**Rozwiązanie problemu z uprawnieniami:**

1. **W środowisku wirtualnym:**
   ```bash
   # Usuń --user flag
   pip install package_name
   # lub
   poetry add package_name
   ```

2. **Poza środowiskiem wirtualnym:**
   ```bash
   pip install --user package_name
   ```

3. **Sprawdź uprawnienia:**
   ```bash
   ls -la /path/to/file
   chmod +x file_name
   ```
""",
            Category.TIMEOUT: """
**Rozwiązanie problemów z timeout:**

1. **Zwiększ timeout:**
   - Dodaj parametr timeout do polecenia
   - Sprawdź konfigurację CI/CD

2. **Sprawdź procesy:**
   ```bash
   ps aux | grep process_name
   kill -9 PID
   ```

3. **Optymalizacja:**
   - Podziel długie zadania na mniejsze
   - Użyj cache dla zależności
""",
            Category.SYNTAX: """
**Rozwiązanie błędów składni:**

1. **Walidacja YAML:**
   ```bash
   python -c "import yaml; yaml.safe_load(open('file.yml'))"
   ```

2. **Sprawdź encoding:**
   - Upewnij się że pliki są w UTF-8
   - Sprawdź znaki specjalne

3. **Użyj linterów:**
   ```bash
   yamllint file.yml
   ```
""",
            Category.CONFIGURATION: """
**Rozwiązanie problemów konfiguracji:**

1. **Sprawdź pliki config:**
   - Porównaj z przykładową konfiguracją
   - Sprawdź ścieżki i nazwy

2. **Walidacja:**
   ```bash
   # Sprawdź składnię
   config_tool --validate config.cfg
   ```

3. **Reset do defaults:**
   - Skopiuj domyślną konfigurację
   - Stopniowo dodawaj customowe ustawienia
""",
            Category.BUILD_FAILURE: """
**Rozwiązanie błędów budowania:**

1. **Clean build:**
   ```bash
   make clean
   make all
   ```

2. **Sprawdź zależności:**
   - Upewnij się że wszystkie narzędzia są zainstalowane
   - Sprawdź wersje

3. **Verbose output:**
   ```bash
   make VERBOSE=1
   ```
""",
        }

    def _determine_priority(self, command: FailedCommand) -> Priority:
        """Określa priorytet błędu."""
        for command in commands:
            analysis = self.analyze(command)
            category = analysis.category
            stats[category] = stats.get(category, 0) + 1

        return stats
        rule in self.priority_rules:
        if rule["condition"](command):
            return rule["priority"]

    return Priority.LOW


def _determine_category(self, command: FailedCommand) -> Category:
    """Określa kategorię błędu."""
    error_text = command.error_output.lower()

    for rule in self.category_rules:
        for pattern in rule["patterns"]:
            if re.search(pattern, error_text, re.IGNORECASE):
                return rule["category"]

    return Category.BUILD_FAILURE


def _analyze_root_cause(self, command: FailedCommand) -> str:
    """Analizuje główną przyczynę błędu."""
    error_text = command.error_output.lower()

    if "poetry.lock" in error_text:
        return "🔍 **Główna przyczyna**: Plik poetry.lock jest niezsynchronizowany z pyproject.toml. To zwykle dzieje się gdy zależności zostały zmodyfikowane bez aktualizacji lock file."

    elif "not found" in error_text and "package.json" in error_text:
        return "🔍 **Główna przyczyna**: Polecenie NPM wykonane z niewłaściwego katalogu. Package.json nie został znaleziony w bieżącej ścieżce."

    elif "virtualenv" in error_text and "--user" in error_text:
        return "🔍 **Główna przyczyna**: Próba instalacji pakietów z flagą --user wewnątrz środowiska wirtualnego, co nie jest dozwolone."

    elif command.is_timeout:
        return "🔍 **Główna przyczyna**: Przekroczenie limitu czasu wykonania. Proces został zakończony po przekroczeniu dozwolonego czasu."

    elif "yaml" in error_text and "constructor" in error_text:
        return "🔍 **Główna przyczyna**: Błąd parsowania YAML z powodu nieznanego tagu lub nieprawidłowej struktury."

    else:
        return "🔍 **Główna przyczyna**: Ogólny błąd wykonania polecenia. Sprawdź szczegóły w error output."


def _suggest_solution(self, command: FailedCommand, category: Category) -> str:
    """Sugeruje rozwiązanie na podstawie kategorii błędu."""
    return self.solution_templates.get(category, self.solution_templates[Category.BUILD_FAILURE])


def _calculate_confidence(self, command: FailedCommand, category: Category) -> float:
    """Oblicza poziom pewności analizy (0.0 - 1.0)."""
    confidence = 0.5  # Bazowa pewność
    error_text = command.error_output.lower()

    # Zwiększ pewność dla jasnych wzorców
    clear_patterns = {
        Category.DEPENDENCIES: ["poetry.lock", "pyproject.toml"],
        Category.MISSING_FILES: ["not found", "enoent"],
        Category.PERMISSIONS: ["permission denied", "--user"],
        Category.TIMEOUT: ["timeout", "timed out"],
        Category.SYNTAX: ["syntax error", "parse error"],
    }

    if category in clear_patterns:
        pattern_matches = sum(1 for pattern in clear_patterns[category]
                              if pattern in error_text)
        confidence += pattern_matches * 0.2

    # Ogranicz do zakresu 0.0-1.0
    return min(1.0, max(0.0, confidence))


def get_category_statistics(self, commands: List[FailedCommand]) -> Dict[Category, int]:
    """Zwraca statystyki kategorii błędów."""
    stats = {category: 0 for category in Category}

    for