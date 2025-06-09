# Makefile dla mdiss

.PHONY: help install dev test lint format clean build publish docs

help: ## Pokaż pomoc
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Zainstaluj podstawowe zależności
	poetry install

dev: ## Zainstaluj zależności deweloperskie
	poetry install --with dev,docs

test: ## Uruchom testy
	poetry run pytest

test-verbose: ## Uruchom testy z verbose output
	poetry run pytest -v

test-coverage: ## Uruchom testy z pokryciem kodu
	poetry run pytest --cov=mdiss --cov-report=html --cov-report=term

test-unit: ## Uruchom tylko testy jednostkowe
	poetry run pytest -m unit

test-integration: ## Uruchom tylko testy integracyjne
	poetry run pytest -m integration

lint: ## Sprawdź jakość kodu
	poetry run black --check mdiss/ tests/
	poetry run isort --check-only mdiss/ tests/
	poetry run flake8 mdiss/ tests/
	poetry run mypy mdiss/

format: ## Sformatuj kod
	poetry run black mdiss/ tests/
	poetry run isort mdiss/ tests/

format-check: ## Sprawdź formatowanie
	poetry run black --check mdiss/ tests/
	poetry run isort --check-only mdiss/ tests/

security: ## Sprawdź bezpieczeństwo
	poetry run bandit -r mdiss/

clean: ## Wyczyść pliki tymczasowe
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -name "*.pyc" -delete

build: clean ## Zbuduj pakiet
	poetry build

publish-test: build ## Opublikuj na TestPyPI
	poetry config repositories.testpypi https://test.pypi.org/legacy/
	poetry publish -r testpypi

publish: build ## Opublikuj na PyPI
	poetry publish

docs: ## Zbuduj dokumentację
	poetry run mkdocs build

docs-serve: ## Uruchom serwer dokumentacji
	poetry run mkdocs serve

docs-deploy: ## Wdróż dokumentację na GitHub Pages
	poetry run mkdocs gh-deploy

pre-commit: ## Uruchom pre-commit hooks
	poetry run pre-commit run --all-files

install-hooks: ## Zainstaluj git hooks
	poetry run pre-commit install

ci: format-check lint test ## Uruchom CI pipeline

qa: lint test ## Sprawdzenia jakości

version-patch: ## Zwiększ wersję patch
	poetry version patch

version-minor: ## Zwiększ wersję minor
	poetry version minor

version-major: ## Zwiększ wersję major
	poetry version major

demo: ## Uruchom demo z przykładowym plikiem
	poetry run mdiss analyze tests/fixtures/sample_markdown.md

demo-create: ## Demo tworzenia issues (dry run)
	poetry run mdiss create tests/fixtures/sample_markdown.md wronai mdiss --dry-run

install-local: ## Zainstaluj lokalnie w trybie deweloperskim
	pip install -e .

uninstall: ## Odinstaluj pakiet
	pip uninstall mdiss -y

check-deps: ## Sprawdź zależności
	poetry check
	poetry show --outdated

update-deps: ## Aktualizuj zależności
	poetry update

lock: ## Zaktualizuj poetry.lock
	poetry lock --no-update

env-info: ## Pokaż informacje o środowisku
	poetry env info
	poetry show

validate: ## Waliduj konfigurację projektu
	poetry check
	poetry run python -m mdiss --version

benchmark: ## Uruchom testy wydajności
	poetry run python -m pytest tests/ -m "slow" --benchmark-only

all: clean install dev lint test build ## Wykonaj pełny workflow

# Aliases
t: test
l: lint
f: format
b: build
h: help