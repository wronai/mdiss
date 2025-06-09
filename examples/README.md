# 📚 Przykłady użycia

Ten katalog zawiera przykłady pokazujące, jak korzystać z narzędzia `mdiss` w różnych scenariuszach.

## Spis treści

1. [Podstawowe przykłady](#podstawowe-przykłady)
2. [Zaawansowane zastosowania](#zaawansowane-zastosowania)
3. [Integracja z CI/CD](#integracja-z-cicd)
4. [Przykładowe pliki wejściowe](#przykładowe-pliki-wejściowe)

## Podstawowe przykłady

### 1. Analiza prostego pliku z błędami

```bash
# Przeanalizuj plik z błędami
mdiss analyze examples/errors/simple_error.md

# Wyświetl szczegółowe informacje
mdiss analyze examples/errors/simple_error.md --verbose

# Zapisz wyniki do pliku JSON
mdiss analyze examples/errors/simple_error.md --output results.json
```

### 2. Tworzenie zgłoszeń na GitHubie

```bash
# Podgląd zgłoszeń (bez tworzenia)
mdiss create examples/errors/build_error.md twoj-uzytkownik/twoje-repo --dry-run

# Rzeczywiste utworzenie zgłoszeń
mdiss create examples/errors/build_error.md twoj-uzytkownik/twoje-repo \
  --labels "bug,build" \
  --title-template "[BUILD] {command}"
```

## Zaawansowane zastosowania

### 1. Filtrowanie wyników

```bash
# Tylko błędy o wysokim priorytecie
mdiss analyze examples/errors/multiple_errors.md --filter "priority in ['high', 'critical']"

# Błędy związane z zależnościami
mdiss analyze examples/errors/multiple_errors.md --filter "category == 'dependencies'"

# Złożone warunki
mdiss analyze examples/errors/multiple_errors.md \
  --filter "category == 'dependencies' and priority in ['high', 'critical']"
```

### 2. Dostosowywanie formatu wyjściowego

```bash
# Format JSON
mdiss analyze examples/errors/simple_error.md --format json

# Format tabeli z wybranymi kolumnami
mdiss analyze examples/errors/multiple_errors.md \
  --format table \
  --columns "Command,Status,Priority,Category"

# Eksport do CSV
mdiss analyze examples/errors/multiple_errors.md --format csv --output errors_report.csv
```

## Integracja z CI/CD

### GitHub Actions

Przykładowy plik `.github/workflows/analyze-errors.yml`:

```yaml
name: Analiza błędów

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

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
          # Utwórz katalog na wyniki
          mkdir -p error-reports

          # Przeanalizuj błędy i zapisz wyniki
          mdiss analyze "**/error_logs/*.md" --output error-reports/analysis.json

          # Utwórz zgłoszenia na GitHubie
          mdiss create error-reports/analysis.json ${{ github.repository }} \
            --token ${{ secrets.GITHUB_TOKEN }} \
            --labels "bug,automated" \
            --title-template "[AUTO] {category}: {command}" \
            --dry-run
```

### GitLab CI

Przykładowy plik `.gitlab-ci.yml`:

```yaml
analyze_errors:
  image: python:3.10
  script:
    - pip install mdiss
    - |
      # Przeanalizuj błędy i wygeneruj raport
      mdiss analyze test_results/*.md --output analysis.json

      # Podgląd zgłoszeń przed utworzeniem
      mdiss create analysis.json $CI_PROJECT_PATH \
        --token $GITLAB_TOKEN \
        --dry-run
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Przykładowe pliki wejściowe

### 1. Prosty błąd budowania

`examples/errors/build_error.md`:

````markdown
## Błąd budowania

**Polecenie:** `npm run build`
**Status:** ❌ Niepowodzenie
**Kod wyjścia:** 1

**Wyjście błędu:**
```
> build
> webpack --mode production

ERROR in ./src/index.js
Module not found: Error: Can't resolve './missing-module' in '/project/src'
```

**Sugerowane rozwiązanie:**
Sprawdź, czy plik `missing-module` istnieje w katalogu `src/`.
Jeśli to zewnętrzna zależność, uruchom `npm install`.
````

### 2. Wiele błędów w jednym pliku

`examples/errors/multiple_errors.md`:

````markdown
# Raport błędów testowych

## 1. Błąd kompilacji TypeScript

**Polecenie:** `tsc --noEmit`
**Status:** ❌ Niepowodzenie
**Kod wyjścia:** 2
**Kategoria:** compilation
**Priorytet:** high

**Wyjście błędu:**
```
src/utils/helpers.ts(12,7): error TS2322: Type 'string' is not assignable to type 'number'.
```

## 2. Błąd testów jednostkowych

**Polecenie:** `npm test`
**Status:** ❌ Niepowodzenie
**Kod wyjścia:** 1
**Kategoria:** tests
**Priorytet:** medium

**Wyjście błędu:**
```
FAIL  src/__tests__/calculator.test.js
  ● Calculator › add › should correctly add two numbers

    expect(received).toBe(expected)

    Expected: 5
    Received: 4
```

## 3. Ostrzeżenie o przestarzałej zależności

**Polecenie:** `npm audit`
**Status:** ⚠ Ostrzeżenie
**Kategoria:** dependencies
**Priorytet:** low

**Wyjście:**
```
# npm audit report

axios  <=0.21.1
Severity: high
Server-Side Request Forgery - https://npmjs.com/advisories/1594
```

**Sugerowane rozwiązanie:**
Zaktualizuj zależność axios do wersji 0.21.2 lub nowszej.
````

## Dodatkowe zasoby

- [Dokumentacja](https://github.com/wronai/mdiss/docs) - pełna dokumentacja narzędzia
- [Przykłady kodu](https://github.com/wronai/mdiss/examples) - więcej przykładów użycia
- [Zgłaszanie problemów](https://github.com/wronai/mdiss/issues) - zgłoś błąd lub sugestię

---

💡 **Wskazówka:** Użyj `mdiss --help`, aby wyświetlić dostępne polecenia i opcje.
