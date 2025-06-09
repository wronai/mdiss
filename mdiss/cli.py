"""
Command Line Interface dla mdiss.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from . import __version__
from .parser import MarkdownParser
from .github_client import GitHubClient
from .models import GitHubConfig

console = Console()


@click.group()
@click.version_option(__version__, prog_name="mdiss")
def cli():
    """
    mdiss - Markdown Issues

    Automatyczne generowanie ticketów GitHub na podstawie plików markdown z błędami poleceń.
    """
    pass


@cli.command()
@click.argument('markdown_file', type=click.Path(exists=True, path_type=Path))
@click.argument('repo_owner')
@click.argument('repo_name')
@click.option('--token', help='GitHub token')
@click.option('--token-file', type=click.Path(path_type=Path), help='Plik z tokenem')
@click.option('--save-token', type=click.Path(path_type=Path), help='Zapisz token do pliku')
@click.option('--dry-run', is_flag=True, help='Tylko podgląd, bez tworzenia issues')
@click.option('--skip-existing', is_flag=True, default=True, help='Pomijaj istniejące issues')
@click.option('--assignees', help='Użytkownicy do przypisania (oddzieleni przecinkami)')
@click.option('--milestone', type=int, help='ID milestone')
def create(
        markdown_file: Path,
        repo_owner: str,
        repo_name: str,
        token: Optional[str],
        token_file: Optional[Path],
        save_token: Optional[Path],
        dry_run: bool,
        skip_existing: bool,
        assignees: Optional[str],
        milestone: Optional[int]
):
    """Tworzy issues na GitHub z pliku markdown."""

    console.print(f"🚀 [bold blue]mdiss v{__version__}[/bold blue] - Markdown Issues")
    console.print("=" * 60)

    # Obsługa tokenu
    github_token = _get_token(token, token_file)
    if not github_token:
        github_token = GitHubClient.setup_token()

    if save_token:
        save_token.write_text(github_token)
        console.print(f"💾 Token zapisany do: {save_token}")

    # Konfiguracja GitHub
    config = GitHubConfig(
        token=github_token,
        owner=repo_owner,
        repo=repo_name
    )

    client = GitHubClient(config)

    # Test połączenia
    if not dry_run:
        console.print("🔍 Testowanie połączenia z GitHub...")
        if not client.test_connection():
            console.print("❌ [red]Błąd połączenia z GitHub. Sprawdź token i repozytorium.[/red]")
            sys.exit(1)
        console.print("✅ [green]Połączenie z GitHub OK[/green]")

    # Parsowanie pliku
    console.print(f"📖 Parsowanie pliku: {markdown_file}")
    parser = MarkdownParser()

    try:
        commands = parser.parse_file(str(markdown_file))
    except Exception as e:
        console.print(f"❌ [red]Błąd parsowania: {e}[/red]")
        sys.exit(1)

    console.print(f"✅ Znaleziono {len(commands)} nieudanych poleceń")

    # Przygotowanie assignees
    assignee_list = None
    if assignees:
        assignee_list = [name.strip() for name in assignees.split(',')]

    # Tworzenie issues
    if dry_run:
        console.print("\n🧪 [yellow]DRY RUN MODE[/yellow] - Podgląd issues:")
        _show_dry_run_preview(commands, client)
    else:
        console.print(f"\n🎯 Tworzenie issues w repozytorium {repo_owner}/{repo_name}...")
        created = client.bulk_create_issues(
            commands,
            skip_existing=skip_existing,
            dry_run=False
        )
        console.print(f"\n✅ [green]Pomyślnie utworzono {len(created)} issues[/green]")


@cli.command()
@click.argument('markdown_file', type=click.Path(exists=True, path_type=Path))
def analyze(markdown_file: Path):
    """Analizuje plik markdown i pokazuje statystyki."""

    console.print(f"📊 [bold blue]Analiza pliku:[/bold blue] {markdown_file}")
    console.print("=" * 60)

    parser = MarkdownParser()

    try:
        commands = parser.parse_file(str(markdown_file))
    except Exception as e:
        console.print(f"❌ [red]Błąd parsowania: {e}[/red]")
        sys.exit(1)

    if not commands:
        console.print("❌ [red]Nie znaleziono żadnych poleceń[/red]")
        sys.exit(1)

    # Statystyki podstawowe
    stats = parser.get_statistics(commands)
    _show_statistics(stats)

    # Analiza błędów
    console.print("\n🔍 [bold]Analiza błędów:[/bold]")
    from .analyzer import ErrorAnalyzer
    analyzer = ErrorAnalyzer()

    category_stats = {}
    priority_stats = {}

    for command in commands:
        analysis = analyzer.analyze(command)

        # Kategorie
        cat = analysis.category.value
        category_stats[cat] = category_stats.get(cat, 0) + 1

        # Priorytety
        pri = analysis.priority.value
        priority_stats[pri] = priority_stats.get(pri, 0) + 1

    _show_analysis_stats(category_stats, priority_stats)


@cli.command()
@click.argument('repo_owner')
@click.argument('repo_name')
@click.option('--token', help='GitHub token')
@click.option('--token-file', type=click.Path(path_type=Path), help='Plik z tokenem')
@click.option('--state', default='open', help='Stan issues (open/closed/all)')
@click.option('--labels', help='Labele do filtrowania')
def list_issues(
        repo_owner: str,
        repo_name: str,
        token: Optional[str],
        token_file: Optional[Path],
        state: str,
        labels: Optional[str]
):
    """Listuje issues w repozytorium."""

    # Obsługa tokenu
    github_token = _get_token(token, token_file)
    if not github_token:
        github_token = GitHubClient.setup_token()

    config = GitHubConfig(
        token=github_token,
        owner=repo_owner,
        repo=repo_name
    )

    client = GitHubClient(config)

    console.print(f"📋 Issues w repozytorium {repo_owner}/{repo_name}")
    console.print("=" * 60)

    try:
        issues = client.list_issues(state=state, labels=labels or "")
        _show_issues_table(issues)
    except Exception as e:
        console.print(f"❌ [red]Błąd: {e}[/red]")
        sys.exit(1)


def _load_env() -> None:
    """Load environment variables from .env file if it exists."""
    env_path = Path.cwd() / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)


def _get_token(token: Optional[str], token_file: Optional[Path]) -> Optional[str]:
    """Get GitHub token from multiple sources in order of priority:
    1. Direct token parameter
    2. Token file
    3. GITHUB_TOKEN environment variable
    4. .env file with GITHUB_TOKEN
    """
    # Check direct token parameter first
    if token:
        return token

    # Check token file
    if token_file and token_file.exists():
        return token_file.read_text().strip()

    # Load environment from .env file if it exists
    _load_env()

    # Check environment variables
    return os.environ.get('GITHUB_TOKEN')


def _show_dry_run_preview(commands, client):
    """Pokazuje podgląd w trybie dry run."""
    console.print("\n🧪 [yellow]DRY RUN MODE[/yellow] - Podgląd issues:")
    
    from rich.table import Table
    from .analyzer import ErrorAnalyzer
    from .models import FailedCommand
    
    analyzer = ErrorAnalyzer()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Nr", style="cyan", width=4)
    table.add_column("Tytuł", style="white")
    table.add_column("Komenda", style="magenta")
    table.add_column("Priorytet", style="yellow")
    table.add_column("Kategoria", style="green")

    for i, cmd_data in enumerate(commands[:10], 1):  # Pokażemy pierwsze 10
        # Create a FailedCommand object from the command data
        if isinstance(cmd_data, dict):
            command = FailedCommand(
                title=cmd_data.get('command', 'Unknown Command'),
                command=cmd_data.get('command', ''),
                source=cmd_data.get('file', 'unknown'),
                command_type=cmd_data.get('command_type', 'shell'),
                status='Failed',
                return_code=cmd_data.get('return_code', 1),
                execution_time=0.0,
                output='',
                error_output=cmd_data.get('error_output', ''),
                metadata=cmd_data.get('metadata', {})
            )
        else:
            command = cmd_data
            
        analysis = analyzer.analyze(command)
        title = cmd_data.get('command', 'Unknown Command') if isinstance(cmd_data, dict) else command.title
        
        table.add_row(
            str(i),
            title[:50] + "..." if len(title) > 50 else title,
            command.command[:30] + "..." if len(command.command) > 30 else command.command,
            analysis.priority.value.upper(),
            analysis.category.value
        )

    console.print(table)

    if len(commands) > 10:
        console.print(f"\nℹ️  Pokazano 10 z {len(commands)} poleceń. Reszta została pominięta.")
    console.print("\nℹ️  [yellow]To jest podgląd. Żadne dane nie zostały wysłane na GitHub.[/yellow]")
    if len(commands) > 10:
        console.print(f"... i {len(commands) - 10} więcej")


def _show_statistics(stats):
    """Pokazuje statystyki parsowania."""
    console.print(f"\n📈 [bold]Statystyki:[/bold]")
    console.print(f"  • Całkowita liczba poleceń: {stats['total_commands']}")
    console.print(f"  • Średni czas wykonania: {stats['average_execution_time']}s")
    console.print(f"  • Timeout'y: {stats['timeout_count']}")
    console.print(f"  • Krytyczne błędy: {stats['critical_count']}")

    if stats['command_types']:
        console.print(f"\n🔧 [bold]Typy poleceń:[/bold]")
        for cmd_type, count in sorted(stats['command_types'].items(), key=lambda x: x[1], reverse=True):
            console.print(f"  • {cmd_type}: {count}")

    if stats['return_codes']:
        console.print(f"\n🚨 [bold]Kody błędów:[/bold]")
        for code, count in sorted(stats['return_codes'].items(), key=lambda x: x[1], reverse=True):
            console.print(f"  • {code}: {count}")


def _show_analysis_stats(category_stats, priority_stats):
    """Pokazuje statystyki analizy błędów."""
    table = Table(title="Analiza błędów")
    table.add_column("Kategoria", style="cyan")
    table.add_column("Liczba", style="white", justify="right")
    table.add_column("Priorytet", style="yellow")
    table.add_column("Liczba", style="white", justify="right")

    # Konwertowanie do list i sortowanie
    categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
    priorities = sorted(priority_stats.items(), key=lambda x: x[1], reverse=True)

    # Wypełnianie tabeli
    max_rows = max(len(categories), len(priorities))
    for i in range(max_rows):
        cat_name = categories[i][0] if i < len(categories) else ""
        cat_count = str(categories[i][1]) if i < len(categories) else ""
        pri_name = priorities[i][0] if i < len(priorities) else ""
        pri_count = str(priorities[i][1]) if i < len(priorities) else ""

        table.add_row(cat_name, cat_count, pri_name, pri_count)

    console.print(table)


def _show_issues_table(issues):
    """Pokazuje tabelę issues."""
    if not issues:
        console.print("📭 [yellow]Brak issues[/yellow]")
        return

    table = Table(title=f"Issues ({len(issues)})")
    table.add_column("Nr", style="cyan", width=6)
    table.add_column("Tytuł", style="white")
    table.add_column("Stan", style="green")
    table.add_column("Labele", style="blue")
    table.add_column("Utworzono", style="dim")

    for issue in issues:
        labels = ", ".join([label["name"] for label in issue.get("labels", [])])
        created = issue["created_at"][:10]  # Tylko data
        state_color = "green" if issue["state"] == "open" else "red"

        table.add_row(
            f"#{issue['number']}",
            issue["title"][:60] + ("..." if len(issue["title"]) > 60 else ""),
            f"[{state_color}]{issue['state']}[/{state_color}]",
            labels[:30] + ("..." if len(labels) > 30 else ""),
            created
        )

    console.print(table)


@cli.command()
def setup():
    """Interaktywna konfiguracja mdiss."""
    console.print("🛠️  [bold blue]Konfiguracja mdiss[/bold blue]")
    console.print("=" * 60)

    # Konfiguracja tokenu
    token = GitHubClient.setup_token()

    # Zapisanie tokenu do .env
    env_file = Path(".env")
    if not env_file.exists():
        env_file.write_text(f"GITHUB_TOKEN={token}\n")
        console.print(f"💾 Utworzono plik .env z tokenem w: {env_file.absolute()}")
        
        # Dodaj .env do .gitignore jeśli nie istnieje
        gitignore = Path(".gitignore")
        if gitignore.exists():
            gitignore_content = gitignore.read_text()
            if ".env" not in gitignore_content:
                with gitignore.open("a") as f:
                    f.write("\n# Local environment variables\n.env\n")
                console.print("✅ Dodano .env do .gitignore")
        else:
            gitignore.write_text("# Local environment variables\n.env\n")
            console.print("✅ Utworzono plik .gitignore z wpisem .env")
    else:
        # Aktualizacja istniejącego .env
        env_content = env_file.read_text()
        if "GITHUB_TOKEN" in env_content:
            # Zastąp istniejący token
            import re
            env_content = re.sub(r'GITHUB_TOKEN=.*', f'GITHUB_TOKEN={token}', env_content)
            env_file.write_text(env_content)
            console.print(f"🔄 Zaktualizowano istniejący token w pliku .env")
        else:
            # Dodaj nowy token
            with env_file.open("a") as f:
                f.write(f"\nGITHUB_TOKEN={token}\n")
            console.print(f"✅ Dodano token do istniejącego pliku .env")

    console.print("\n✅ [green]Konfiguracja zakończona![/green]")
    console.print("\nPrzykład użycia:")
    console.print("  mdiss list-issues wronai mdiss")


@cli.command()
@click.argument('markdown_file', type=click.Path(exists=True, path_type=Path))
@click.option('--format', 'output_format', default='table',
              type=click.Choice(['table', 'json', 'csv']),
              help='Format wyjścia')
@click.option('--output', type=click.Path(path_type=Path), help='Plik wyjściowy')
def export(markdown_file: Path, output_format: str, output: Optional[Path]):
    """Eksportuje dane z pliku markdown do różnych formatów."""

    console.print(f"📤 [bold blue]Eksport danych[/bold blue] z {markdown_file}")
    console.print("=" * 60)

    parser = MarkdownParser()

    try:
        commands = parser.parse_file(str(markdown_file))
    except Exception as e:
        console.print(f"❌ [red]Błąd parsowania: {e}[/red]")
        sys.exit(1)

    if not commands:
        console.print("❌ [red]Nie znaleziono żadnych poleceń[/red]")
        sys.exit(1)

    # Eksport w wybranym formacie
    if output_format == 'json':
        _export_json(commands, output)
    elif output_format == 'csv':
        _export_csv(commands, output)
    else:  # table
        _export_table(commands, output)

    console.print(f"✅ [green]Eksport zakończony[/green]")


def _export_json(commands, output_file):
    """Eksportuje do JSON."""
    import json

    data = []
    for cmd in commands:
        data.append({
            "title": cmd.title,
            "command": cmd.command,
            "source": cmd.source,
            "type": cmd.command_type,
            "return_code": cmd.return_code,
            "execution_time": cmd.execution_time,
            "error_output": cmd.error_output,
            "metadata": cmd.metadata
        })

    if output_file:
        output_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        console.print(f"📄 JSON zapisany do: {output_file}")
    else:
        console.print(json.dumps(data, indent=2, ensure_ascii=False))


def _export_csv(commands, output_file):
    """Eksportuje do CSV."""
    import csv
    import io

    output_buffer = io.StringIO()
    writer = csv.writer(output_buffer)

    # Nagłówki
    writer.writerow([
        "Title", "Command", "Source", "Type", "Return Code",
        "Execution Time", "Error Output", "Metadata"
    ])

    # Dane
    for cmd in commands:
        metadata_str = "; ".join([f"{k}={v}" for k, v in cmd.metadata.items()])
        writer.writerow([
            cmd.title, cmd.command, cmd.source, cmd.command_type,
            cmd.return_code, cmd.execution_time, cmd.error_output, metadata_str
        ])

    csv_content = output_buffer.getvalue()

    if output_file:
        output_file.write_text(csv_content)
        console.print(f"📊 CSV zapisany do: {output_file}")
    else:
        console.print(csv_content)


def _export_table(commands, output_file):
    """Eksportuje do tabeli tekstowej."""
    table = Table(title="Failed Commands Export")
    table.add_column("Title", style="white")
    table.add_column("Command", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Return Code", style="red")
    table.add_column("Time", style="green")

    for cmd in commands:
        table.add_row(
            cmd.title[:30] + ("..." if len(cmd.title) > 30 else ""),
            cmd.command[:20] + ("..." if len(cmd.command) > 20 else ""),
            cmd.command_type,
            str(cmd.return_code),
            f"{cmd.execution_time}s"
        )

    if output_file:
        # Dla pliku używamy prostego formatu tekstowego
        content = []
        content.append("Failed Commands Export")
        content.append("=" * 50)
        for cmd in commands:
            content.append(f"Title: {cmd.title}")
            content.append(f"Command: {cmd.command}")
            content.append(f"Type: {cmd.command_type}")
            content.append(f"Return Code: {cmd.return_code}")
            content.append(f"Execution Time: {cmd.execution_time}s")
            content.append("-" * 30)

        output_file.write_text("\n".join(content))
        console.print(f"📋 Tabela zapisana do: {output_file}")
    else:
        console.print(table)


def main():
    """Główna funkcja CLI."""
    cli()


if __name__ == "__main__":
    main()