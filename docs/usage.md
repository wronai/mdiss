#!/usr/bin/env python3
"""
Podstawowe przykłady użycia mdiss API.
"""

import os
from pathlib import Path

from mdiss import MarkdownParser, GitHubClient, ErrorAnalyzer
from mdiss.models import GitHubConfig, FailedCommand


def example_1_basic_parsing():
    """Przykład 1: Podstawowe parsowanie pliku markdown."""
    print("🔍 Przykład 1: Parsowanie pliku markdown")
    print("=" * 50)
    
    # Tworzenie parsera
    parser = MarkdownParser()
    
    # Parsowanie pliku (przykładowy plik z fixtures)
    commands = parser.parse_file("../tests/fixtures/sample_markdown.md")
    
    print(f"Znaleziono {len(commands)} nieudanych poleceń:")
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n{i}. {cmd.title}")
        print(f"   Polecenie: {cmd.command}")
        print(f"   Typ: {cmd.command_type}")
        print(f"   Kod błędu: {cmd.return_code}")
        print(f"   Czas: {cmd.execution_time}s")


def example_2_error_analysis():
    """Przykład 2: Analiza błędów i kategoryzacja."""
    print("\n🧠 Przykład 2: Analiza błędów")
    print("=" * 50)
    
    # Przykładowe polecenie z błędem Poetry
    poetry_command = FailedCommand(
        title="Poetry Install Failed",
        command="poetry install",
        source="/home/user/project/pyproject.toml",
        command_type="poetry",
        status="Failed",
        return_code=1,
        execution_time=2.5,
        output="Installing dependencies from lock file",
        error_output="pyproject.toml changed significantly since poetry.lock was last generated. Run `poetry lock` to fix the lock file.",
        metadata={"project": "myproject"}
    )
    
    # Analiza błędu
    analyzer = ErrorAnalyzer()
    analysis = analyzer.analyze(poetry_command)
    
    print(f"Polecenie: {poetry_command.command}")
    print(f"Priorytet: {analysis.priority.value.upper()}")
    print(f"Kategoria: {analysis.category.value}")
    print(f"Pewność: {analysis.confidence:.0%}")
    print(f"\nPrzyczyna:")
    print(analysis.root_cause)
    print(f"\nSugerowane rozwiązanie:")
    print(analysis.suggested_solution[:200] + "...")


def example_3_github_integration():
    """Przykład 3: Integracja z GitHub (dry run)."""
    print("\n🔗 Przykład 3: Integracja z GitHub")
    print("=" * 50)
    
    # Sprawdź czy token jest dostępny
    token = os.environ.get('GITHUB_TOKEN') or input("Podaj GitHub token (lub Enter aby pominąć): ")
    
    if not token:
        print("⏭️  Pomijam przykład GitHub - brak tokenu")
        return
    
    # Konfiguracja GitHub
    config = GitHubConfig(
        token=token,
        owner="wronai",  # Zmień na swoje dane
        repo="mdiss"     # Zmień na swoje repo
    )
    
    # Tworzenie klienta
    client = GitHubClient(config)
    
    # Test połączenia
    if client.test_connection():
        print("✅ Połączenie z GitHub OK")
        
        # Przykładowe polecenie
        failed_command = FailedCommand(
            title="Test Command Failure",
            command="make test",
            source="/home/user/project/Makefile",
            command_type="make_target",
            status="Failed",
            return_code=2,
            execution_time=1.5,
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