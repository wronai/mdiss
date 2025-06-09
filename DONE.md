# Successfully Executed Commands

## 1. Make target: help

**Command:** `make help`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.01s

**Output:**
```
[36mall                 [0m Wykonaj pełny workflow
[36mbenchmark           [0m Uruchom testy wydajności
[36mbuild               [0m Zbuduj pakiet
[36mcheck-deps          [0m Sprawdź zależności
[36mci                  [0m Uruchom CI pipeline
[36mclean               [0m Wyczyść pliki tymczasowe
[36mdemo-create         [0m Demo tworzenia issues (dry run)
[36mdemo                [0m Uruchom demo z przykładowym plikiem
[36mdev                 [0m Zainstaluj zależności deweloperskie
...
```

**Metadata:**
- **target:** help
- **original_command:** make help

---

## 2. Make target: install

**Command:** `make install`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.10s

**Output:**
```
poetry install
Installing dependencies from lock file

No dependencies to install or update

Installing the current project: mdiss (1.0.63)

```

**Metadata:**
- **target:** install
- **original_command:** make install

---

## 3. Make target: dev

**Command:** `make dev`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.09s

**Output:**
```
poetry install --with dev,docs
Installing dependencies from lock file

No dependencies to install or update

Installing the current project: mdiss (1.0.63)

```

**Metadata:**
- **target:** dev
- **original_command:** make dev

---

## 4. Make target: format

**Command:** `make format`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.95s

**Output:**
```
poetry run black mdiss/ tests/
poetry run isort mdiss/ tests/
Fixing /home/tom/github/wronai/mdiss/mdiss/__init__.py
Fixing /home/tom/github/wronai/mdiss/mdiss/analyzer.py
Fixing /home/tom/github/wronai/mdiss/mdiss/cli.py
Fixing /home/tom/github/wronai/mdiss/mdiss/github_client.py
Fixing /home/tom/github/wronai/mdiss/mdiss/models.py
Fixing /home/tom/github/wronai/mdiss/mdiss/parser.py
Fixing /home/tom/github/wronai/mdiss/mdiss/parsers/__init__.py
Fixing /home/tom/github/wronai/mdiss/mdiss/parser...
```

**Error Output:**
```
reformatted /home/tom/github/wronai/mdiss/mdiss/clients/__init__.py
reformatted /home/tom/github/wronai/mdiss/tests/__init__.py
reformatted /home/tom/github/wronai/mdiss/mdiss/__init__.py
reformatted /home/tom/github/wronai/mdiss/mdiss/parsers/__init__.py
reformatted /home/tom/github/wronai/mdiss/tests/test_parser.py
reformatted /home/tom/github/wronai/mdiss/mdiss/models.py
reformatted /home/tom/github/wronai/mdiss/mdiss/parsers/xml_parser.py
reformatted /home/tom/github/wronai/mdiss/tests/conft...
```

**Metadata:**
- **target:** format
- **original_command:** make format

---

## 5. Make target: format-check

**Command:** `make format-check`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.56s

**Output:**
```
poetry run black --check mdiss/ tests/
poetry run isort --check-only mdiss/ tests/

```

**Error Output:**
```
All done! ✨ 🍰 ✨
18 files would be left unchanged.

```

**Metadata:**
- **target:** format-check
- **original_command:** make format-check

---

## 6. Make target: install-hooks

**Command:** `make install-hooks`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.87s

**Output:**
```
poetry run pre-commit install
pre-commit installed at .git/hooks/pre-commit

```

**Metadata:**
- **target:** install-hooks
- **original_command:** make install-hooks

---

## 7. Make target: version-patch

**Command:** `make version-patch`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.51s

**Output:**
```
poetry version patch
Bumping version from 1.0.63 to 1.0.64

```

**Metadata:**
- **target:** version-patch
- **original_command:** make version-patch

---

## 8. Make target: version-minor

**Command:** `make version-minor`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.57s

**Output:**
```
poetry version minor
Bumping version from 1.0.64 to 1.1.0

```

**Metadata:**
- **target:** version-minor
- **original_command:** make version-minor

---

## 9. Make target: version-major

**Command:** `make version-major`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.46s

**Output:**
```
poetry version major
Bumping version from 1.1.0 to 2.0.0

```

**Metadata:**
- **target:** version-major
- **original_command:** make version-major

---

## 10. Make target: demo

**Command:** `make demo`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 2.55s

**Output:**
```
poetry run mdiss analyze tests/fixtures/sample_markdown.md
📊 Analiza pliku: tests/fixtures/sample_markdown.md
============================================================

📈 Statystyki:
  • Całkowita liczba poleceń: 5
  • Średni czas wykonania: 0.0s
  • Timeout'y: 0
  • Krytyczne błędy: 0

🔧 Typy poleceń:
  • unknown: 5

🔍 Analiza błędów:
                Analiza błędów
┏━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┓
┃ Kategoria     ┃ Liczba ┃ Priorytet ┃ Liczba ┃
┡━━━━━━━━━━━━━━...
```

**Metadata:**
- **target:** demo
- **original_command:** make demo

---

## 11. Make target: install-local

**Command:** `make install-local`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.38s

**Output:**
```
pip install -e .
Obtaining file:///home/tom/github/wronai/mdiss
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Checking if build backend supports build_editable: started
  Checking if build backend supports build_editable: finished with status 'done'
  Getting requirements to build editable: started
  Getting requirements to build editable: finished with status 'done'
  Preparing editable metadata (pyproject.toml): started
  Preparing edit...
```

**Metadata:**
- **target:** install-local
- **original_command:** make install-local

---

## 12. Make target: uninstall

**Command:** `make uninstall`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 0.31s

**Output:**
```
pip uninstall mdiss -y
Found existing installation: mdiss 2.0.0
Uninstalling mdiss-2.0.0:
  Successfully uninstalled mdiss-2.0.0

```

**Metadata:**
- **target:** uninstall
- **original_command:** make uninstall

---

## 13. Make target: check-deps

**Command:** `make check-deps`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 7.19s

**Output:**
```
poetry check
poetry show --outdated
black         23.12.1 25.1.0 The uncompromising code formatter.
click         8.1.8   8.2.1  Composable command line interface toolkit
configparser  5.3.0   7.2.0  Updated configparser from stdlib for earlier Py...
flake8        6.1.0   7.2.0  the modular source code checker: pep8 pyflakes ...
isort         5.13.2  6.0.1  A Python utility / library to sort Python imports.
mkdocstrings  0.20.0  0.29.1 Automatic documentation from sources, for MkDocs.
pre-commit...
```

**Error Output:**
```
Warning: [tool.poetry.name] is deprecated. Use [project.name] instead.
Warning: [tool.poetry.version] is set but 'version' is not in [project.dynamic]. If it is static use [project.version]. If it is dynamic, add 'version' to [project.dynamic].
If you want to set the version dynamically via `poetry build --local-version` or you are using a plugin, which sets the version dynamically, you should define the version in [tool.poetry] and add 'version' to [project.dynamic].
Warning: [tool.poetry.descr...
```

**Metadata:**
- **target:** check-deps
- **original_command:** make check-deps

---

## 14. Make target: update-deps

**Command:** `make update-deps`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 11.71s

**Output:**
```
poetry update
Updating dependencies
Resolving dependencies...

No dependencies to install or update

```

**Metadata:**
- **target:** update-deps
- **original_command:** make update-deps

---

## 15. Make target: env-info

**Command:** `make env-info`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 3.47s

**Output:**
```
poetry env info

Virtualenv
Python:         3.12.9
Implementation: CPython
Path:           /home/tom/.cache/pypoetry/virtualenvs/mdiss-VgxEfGFg-py3.12
Executable:     /home/tom/.cache/pypoetry/virtualenvs/mdiss-VgxEfGFg-py3.12/bin/python
Valid:          True

Base
Platform:   linux
OS:         posix
Python:     3.12.9
Path:       /home/tom/miniconda3
Executable: /home/tom/miniconda3/bin/python3.12
poetry show
annotated-types            0.7.0           Reusable constraint types to use...
babel   ...
```

**Metadata:**
- **target:** env-info
- **original_command:** make env-info

---

## 16. Make target: f

**Command:** `make f`
**Source:** /home/tom/github/wronai/mdiss/Makefile
**Type:** make_target
**Status:** ✅ Success
**Return Code:** 0
**Execution Time:** 1.42s

**Output:**
```
poetry run black mdiss/ tests/
poetry run isort mdiss/ tests/

```

**Error Output:**
```
All done! ✨ 🍰 ✨
18 files left unchanged.

```

**Metadata:**
- **target:** f
- **original_command:** make f

---
