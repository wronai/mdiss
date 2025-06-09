# Makefile for mdiss (Markdown Issues)
#
# Available commands:
#   make help       - Show this help
#   make install    - Install main dependencies
#   make dev        - Install development dependencies
#   make test       - Run tests
#   make lint       - Run linters
#   make format     - Format code
#   make build      - Build package
#   make publish    - Publish to PyPI

# Configuration
PYTHON := python
POETRY := poetry
PACKAGE := mdiss
TEST_PATH := tests/

# Colors
NO_COLOR=\033[0m
OK_COLOR=\033[32;01m
ERROR_COLOR=\033[31;01m
WARN_COLOR=\033[33;01m

# Help target
.PHONY: help
help: ## Show this help message
	@echo "\n$(OK_COLOR)Available targets:$(NO_COLOR)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(OK_COLOR)%-25s$(NO_COLOR) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort
	@echo ""

# Installation
.PHONY: install
install:  ## Install main dependencies
	@echo "$(OK_COLOR)Installing main dependencies...$(NO_COLOR)"
	$(POETRY) install --no-dev

.PHONY: dev
install-dev:  ## Install development dependencies
	@echo "$(OK_COLOR)Installing development dependencies...$(NO_COLOR)"
	$(POETRY) install --with dev,docs

# Testing
.PHONY: test test-verbose test-coverage test-unit test-integration

test:  ## Run all tests
	@echo "$(OK_COLOR)Running tests...$(NO_COLOR)"
	$(POETRY) run pytest $(TEST_PATH)

test-verbose:  ## Run tests with verbose output
	@echo "$(OK_COLOR)Running tests with verbose output...$(NO_COLOR)"
	$(POETRY) run pytest -v $(TEST_PATH)

test-coverage:  ## Run tests with coverage report
	@echo "$(OK_COLOR)Running tests with coverage...$(NO_COLOR)"
	$(POETRY) run pytest --cov=$(PACKAGE) --cov-report=html --cov-report=term $(TEST_PATH)

test-unit:  ## Run only unit tests
	@echo "$(OK_COLOR)Running unit tests...$(NO_COLOR)"
	$(POETRY) run pytest -m unit $(TEST_PATH)

test-integration:  ## Run only integration tests
	@echo "$(OK_COLOR)Running integration tests...$(NO_COLOR)"
	$(POETRY) run pytest -m integration $(TEST_PATH)

# Code Quality
.PHONY: lint format format-check security

lint:  ## Run all linters
	@echo "$(OK_COLOR)Running linters...$(NO_COLOR)"
	$(POETRY) run black --check $(PACKAGE)/ $(TEST_PATH)
	$(POETRY) run isort --check-only $(PACKAGE)/ $(TEST_PATH)
	$(POETRY) run flake8 $(PACKAGE)/ $(TEST_PATH)
	$(POETRY) run mypy $(PACKAGE)/

format:  ## Format code
	@echo "$(OK_COLOR)Formatting code...$(NO_COLOR)"
	$(POETRY) run black $(PACKAGE)/ $(TEST_PATH)
	$(POETRY) run isort $(PACKAGE)/ $(TEST_PATH)

format-check:  ## Check code formatting
	@echo "$(OK_COLOR)Checking code formatting...$(NO_COLOR)"
	$(POETRY) run black --check $(PACKAGE)/ $(TEST_PATH)
	$(POETRY) run isort --check-only $(PACKAGE)/ $(TEST_PATH)

security:  ## Check for security issues
	@echo "$(OK_COLOR)Running security checks...$(NO_COLOR)"
	$(POETRY) run bandit -r $(PACKAGE)/


# Build and Publish
.PHONY: build publish publish-test

build: clean  ## Build package
	@echo "$(OK_COLOR)Building package...$(NO_COLOR)"
	$(POETRY) version patch
	$(POETRY) build

publish-test: build  ## Publish to TestPyPI
	@echo "$(WARN_COLOR)Publishing to TestPyPI...$(NO_COLOR)"
	$(POETRY) config repositories.testpypi https://test.pypi.org/legacy/
	$(POETRY) publish -r testpypi

publish: build  ## Publish to PyPI
	@echo "$(WARN_COLOR)Publishing to PyPI...$(NO_COLOR)"
	@read -p "Are you sure you want to publish to PyPI? [y/N] " -n 1 -r; \
	echo; \
	$(POETRY) publish; \

# Documentation
.PHONY: docs docs-serve docs-deploy

docs:  ## Build documentation
	@echo "$(OK_COLOR)Building documentation...$(NO_COLOR)"
	$(POETRY) run mkdocs build

docs-serve:  ## Serve documentation locally
	@echo "$(OK_COLOR)Serving documentation at http://localhost:8000$(NO_COLOR)"
	$(POETRY) run mkdocs serve

docs-deploy:  ## Deploy documentation to GitHub Pages
	@echo "$(WARN_COLOR)Deploying documentation to GitHub Pages...$(NO_COLOR)"
	$(POETRY) run mkdocs gh-deploy

# Code Quality and CI
.PHONY: pre-commit install-hooks ci qa

pre-commit:  ## Run pre-commit hooks
	@echo "$(OK_COLOR)Running pre-commit hooks...$(NO_COLOR)"
	$(POETRY) run pre-commit run --all-files

install-hooks:  ## Install git hooks
	@echo "$(OK_COLOR)Installing git hooks...$(NO_COLOR)"
	$(POETRY) run pre-commit install

ci: format-check lint test  ## Run CI pipeline

qa: lint test  ## Run quality assurance checks

# Version Management
.PHONY: version-patch version-minor version-major

version-patch:  ## Bump patch version
	@echo "$(OK_COLOR)Bumping patch version...$(NO_COLOR)"
	$(POETRY) version patch

version-minor:  ## Bump minor version
	@echo "$(OK_COLOR)Bumping minor version...$(NO_COLOR)"
	$(POETRY) version minor

version-major:  ## Bump major version
	@echo "$(OK_COLOR)Bumping major version...$(NO_COLOR)"
	$(POETRY) version major

# LLM and AI
.PHONY: llm-serve llm-pull llm-list llm-test

llm-serve:	## Start Ollama server in the background if not already running
	@if ! pgrep -f "ollama serve" > /dev/null; then \
		echo "$(OK_COLOR)Starting Ollama server...$(NO_COLOR)"; \
		ollama serve & \
	else \
		echo "$(OK_COLOR)Ollama server is already running$(NO_COLOR)"; \
	fi

llm-pull:	## Pull the default Mistral 7B model
	@echo "$(OK_COLOR)Pulling Mistral 7B model...$(NO_COLOR)"
	ollama pull mistral:7b

llm-list:	## List available Ollama models
	@echo "$(OK_COLOR)Available models:$(NO_COLOR)"
	ollama list

llm-test:	## Test local LLM integration
	@echo "$(OK_COLOR)Testing local LLM integration...$(NO_COLOR)"
	@echo "$(WARN_COLOR)Make sure Ollama server is running (make llm-serve)$(NO_COLOR)"
	$(POETRY) run python examples/local_llm_ticket_generation.py

# Demo and Examples
.PHONY: demo demo-create

demo:  ## Run demo with sample file
	@echo "$(OK_COLOR)Running demo...$(NO_COLOR)"
	$(POETRY) run $(PACKAGE) analyze tests/fixtures/sample_markdown.md

demo-create:  ## Demo issue creation (dry run)
	@echo "$(OK_COLOR)Running demo issue creation (dry run)...$(NO_COLOR)"
	$(POETRY) run $(PACKAGE) create tests/fixtures/sample_markdown.md wronai mdiss --dry-run

# Development
.PHONY: install-local uninstall check-deps update-deps lock env-info validate benchmark clean

install-local:  ## Install in development mode
	@echo "$(OK_COLOR)Installing in development mode...$(NO_COLOR)"
	pip install -e .

uninstall:  ## Uninstall package
	@echo "$(WARN_COLOR)Uninstalling package...$(NO_COLOR)"
	pip uninstall $(PACKAGE) -y

check-deps:  ## Check dependencies
	@echo "$(OK_COLOR)Checking dependencies...$(NO_COLOR)"
	$(POETRY) check
	$(POETRY) show --outdated

update-deps:  ## Update dependencies
	@echo "$(OK_COLOR)Updating dependencies...$(NO_COLOR)"
	$(POETRY) update

lock:  ## Update poetry.lock
	@echo "$(OK_COLOR)Updating poetry.lock...$(NO_COLOR)"
	$(POETRY) lock --no-update

env-info:  ## Show environment information
	@echo "$(OK_COLOR)Environment information:$(NO_COLOR)"
	$(POETRY) env info
	@echo "\n$(OK_COLOR)Installed packages:$(NO_COLOR)"
	$(POETRY) show

validate:  ## Validate project configuration
	@echo "$(OK_COLOR)Validating project configuration...$(NO_COLOR)"
	$(POETRY) check
	$(POETRY) run python -m $(PACKAGE) --version

benchmark:  ## Run performance benchmarks
	@echo "$(OK_COLOR)Running benchmarks...$(NO_COLOR)"
	$(POETRY) run python -m pytest $(TEST_PATH) -m "slow" --benchmark-only

# Cleanup
.PHONY: clean

clean:  ## Clean build artifacts
	@echo "$(OK_COLOR)Cleaning build artifacts...$(NO_COLOR)"
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .coverage htmlcov/ site/ .benchmarks/
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*~' -delete

# Help section updates
help: ## Show this help message
	@echo "\n$(OK_COLOR)Available targets:$(NO_COLOR)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(OK_COLOR)%-25s$(NO_COLOR) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort
	@echo "\n$(OK_COLOR)LLM Commands:$(NO_COLOR)"
	@echo "  make llm-serve     Start Ollama server"
	@echo "  make llm-pull      Download Mistral 7B model"
	@echo "  make llm-list      List available models"
	@echo "  make llm-test      Test LLM integration"

# Aliases
.PHONY: t l f b p h

t: test
l: lint
f: format
b: build
p: publish
h: help
