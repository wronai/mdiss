#!/bin/bash
# Skrypt instalacyjny dla mdiss

set -e

echo "🚀 Instalacja mdiss - Markdown Issues"
echo "====================================="

# Sprawdź czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nie jest zainstalowany!"
    echo "Zainstaluj Python 3.8+ i spróbuj ponownie."
    exit 1
fi

# Sprawdź wersję Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
MIN_VERSION="3.8"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✅ Python $PYTHON_VERSION - OK"
else
    echo "❌ Python $PYTHON_VERSION jest za stary!"
    echo "Wymagany Python $MIN_VERSION lub nowszy."
    exit 1
fi

# Sprawdź czy pip jest zainstalowany
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 nie jest zainstalowany!"
    echo "Zainstaluj pip3 i spróbuj ponownie."
    exit 1
fi

echo "📦 Instalowanie mdiss..."

# Instalacja z PyPI
if pip3 install mdiss; then
    echo "✅ mdiss został pomyślnie zainstalowany!"
else
    echo "❌ Błąd podczas instalacji!"
    echo "Spróbuj ręcznie: pip3 install mdiss"
    exit 1
fi

# Sprawdź instalację
if command -v mdiss &> /dev/null; then
    VERSION=$(mdiss --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+' || echo "unknown")
    echo "✅ mdiss $VERSION jest gotowy do użycia!"
else
    echo "⚠️  mdiss został zainstalowany, ale nie jest dostępny w PATH"
    echo "Może być potrzebne ponowne zalogowanie lub aktualizacja PATH"
fi

echo ""
echo "🎯 Następne kroki:"
echo "1. Skonfiguruj token GitHub:"
echo "   mdiss setup"
echo ""
echo "2. Przeanalizuj plik markdown:"
echo "   mdiss analyze your_file.md"
echo ""
echo "3. Utwórz issues (dry run):"
echo "   mdiss create your_file.md owner repo --dry-run"
echo ""
echo "📚 Dokumentacja: https://wronai.github.io/mdiss"
echo "🐛 Issues: https://github.com/wronai/mdiss/issues"
echo ""
echo "Dziękujemy za używanie mdiss! 🎉"