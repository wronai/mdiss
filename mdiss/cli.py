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
from .models import GitHubConfig, FailedCommand

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
        # First try the specialized failed commands parser
        command_dicts = parser.parse_failed_commands(str(markdown_file))
        
        # Fall back to the generic parser if no commands were found
        if not command_dicts or (len(command_dicts) == 1 and 'error' in command_dicts[0]):
            command_dicts = parser.parse_file(str(markdown_file))
            
        # Convert dictionaries to FailedCommand objects
        commands = []
        for cmd_dict in command_dicts:
            if isinstance(cmd_dict, dict) and 'error' not in cmd_dict:
                try:
                    # Map the parsed dictionary to FailedCommand fields
                    cmd = FailedCommand(
                        title=cmd_dict.get('title', 'Unknown Command'),
                        command=cmd_dict.get('command', ''),
                        source=cmd_dict.get('source', ''),
                        command_type=cmd_dict.get('command_type', 'shell'),
                        status=cmd_dict.get('status', 'Failed'),
                        return_code=cmd_dict.get('return_code', 1),
                        execution_time=cmd_dict.get('execution_time', 0.0),
                        output=cmd_dict.get('output', ''),
                        error_output=cmd_dict.get('error_output', ''),
                        metadata=cmd_dict.get('metadata', {})
                    )
                    commands.append(cmd)
                except Exception as e:
                    console.print(f"⚠️  Błąd konwersji polecenia: {e}")
                    continue
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
            owner=repo_owner,
            repo=repo_name,
            skip_existing=skip_existing,
            dry_run=False
        )
        console.print(f"\n✅ [green]Pomyślnie utworzono {len(created)} issues[/green]")


@cli.command()
@click.argument('markdown_file', type=click.Path(exists=True, path_type=Path))
@click.option('--verbose', '-v', is_flag=True, help='Pokaż szczegółowe informacje o komendach')
def analyze(markdown_file: Path, verbose: bool):
    """Analizuje plik markdown i pokazuje statystyki.
    
    Przykłady:
        mdiss analyze plik.md         # Podstawowe statystyki
        mdiss analyze plik.md -v      # Szczegółowe informacje o komendach
    """

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
    
    # Calculate additional statistics
    total_commands = len(commands)
    total_time = sum(float(cmd.get('execution_time', 0)) for cmd in commands)
    timeout_count = sum(1 for cmd in commands if cmd.get('status', '').lower() == 'timeout')
    critical_count = sum(1 for cmd in commands if any(
        indicator in (cmd.get('error_output', '') or '').lower()
        for indicator in ['segmentation fault', 'core dumped', 'critical error', 'fatal error', 'system error']
    ))
    
    # Update stats with calculated values
    stats.update({
        'total_commands': total_commands,
        'average_execution_time': round(total_time / total_commands, 2) if total_commands > 0 else 0,
        'timeout_count': timeout_count,
        'critical_count': critical_count
    })
    
    _show_statistics(stats)

    # Analiza błędów
    console.print("\n🔍 [bold]Analiza błędów:[/bold]")
    from .analyzer import ErrorAnalyzer
    analyzer = ErrorAnalyzer()

    category_stats = {}
    priority_stats = {}

    for cmd_data in commands:
        # Convert dictionary to FailedCommand if needed
        if isinstance(cmd_data, dict):
            command = FailedCommand(
                title=cmd_data.get('title', 'Unknown Command'),
                command=cmd_data.get('command', ''),
                source=cmd_data.get('source', ''),
                command_type=cmd_data.get('command_type', 'unknown'),
                status=cmd_data.get('status', 'Failed'),
                return_code=cmd_data.get('return_code', 1),
                execution_time=float(cmd_data.get('execution_time', 0)),
                output=cmd_data.get('output', ''),
                error_output=cmd_data.get('error_output', cmd_data.get('error', '')),
                metadata=cmd_data.get('metadata', {})
            )
        else:
            command = cmd_data
            
        analysis = analyzer.analyze(command)

        # Kategorie
        cat = analysis.category.value
        category_stats[cat] = category_stats.get(cat, 0) + 1

        # Priorytety
        pri = analysis.priority.value
        priority_stats[pri] = priority_stats.get(pri, 0) + 1

    _show_analysis_stats(category_stats, priority_stats)
    
    # Pokaż szczegółowe informacje o komendach, jeśli włączono tryb verbose
    if verbose and commands:
        from rich.table import Table
        
        console.print("\n🔍 [bold]Szczegółowe informacje o komendach:[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Lp.", style="cyan", width=4)
        table.add_column("Komenda", style="white")
        table.add_column("Plik źródłowy", style="green")
        table.add_column("Kategoria", style="yellow")
        table.add_column("Priorytet", style="red")
        
        for i, cmd in enumerate(commands[:20], 1):  # Ogranicz do pierwszych 20 komend
            if isinstance(cmd, dict):
                cmd_text = cmd.get('command', 'Brak komendy')
                source = cmd.get('file', 'Nieznane źródło')
            else:
                cmd_text = getattr(cmd, 'command', 'Brak komendy')
                source = getattr(cmd, 'source', 'Nieznane źródło')
            
            # Analizuj komendę, aby uzyskać kategorię i priorytet
            analysis = analyzer.analyze(cmd)
            
            # Skróć długie komendy
            display_cmd = cmd_text[:50] + "..." if len(cmd_text) > 50 else cmd_text
            
            table.add_row(
                str(i),
                display_cmd,
                str(source)[:30] + "..." if len(str(source)) > 30 else str(source),
                analysis.category.value,
                analysis.priority.value.upper()
            )
        
        console.print(table)
        
        if len(commands) > 20:
            console.print(f"\nℹ️  Pokazano 20 z {len(commands)} znalezionych komend. Użyj filtrowania, aby zawęzić wyniki.")


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
    from rich.panel import Panel
    from rich.markdown import Markdown
    from .analyzer import ErrorAnalyzer
    from .models import FailedCommand
    
    analyzer = ErrorAnalyzer()
    
    console.print("\n🧪 [bold yellow]DRY RUN MODE - PODGLĄD ZGŁOSZEŃ[/bold yellow]")
    console.print("=" * 60)
    
    # Pokaż podsumowanie
    console.print(f"\n📋 [bold]Podsumowanie:[/bold] {len(commands)} zgłoszeń do utworzenia")
    
    # Tabela podsumowująca
    from rich.table import Table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Tytuł", style="white")
    table.add_column("Kategoria", style="green")
    table.add_column("Priorytet", style="yellow")
    
    for i, cmd_data in enumerate(commands, 1):
        # Konwersja na FailedCommand jeśli potrzeba
        if isinstance(cmd_data, dict):
            cmd_text = cmd_data.get('command') or cmd_data.get('code_block') or cmd_data.get('original_line', '')
            cmd_text = cmd_text.strip()
            
            if not cmd_text and 'code_block' in cmd_data:
                first_line = cmd_data['code_block'].split('\n')[0].strip()
                cmd_text = first_line if first_line else 'Brak komendy'
            
            title = cmd_text.split('\n')[0].strip() if cmd_text else 'Nieznana komenda'
            
            command = FailedCommand(
                title=title[:100],
                command=cmd_text,
                source=cmd_data.get('file', 'unknown'),
                command_type=cmd_data.get('command_type', 'shell'),
                status='Failed',
                return_code=cmd_data.get('return_code', 1),
                execution_time=0.0,
                output=cmd_data.get('output', ''),
                error_output=cmd_data.get('error_output', cmd_data.get('error', '')),
                metadata=cmd_data.get('metadata', {})
            )
        else:
            command = cmd_data
        
        analysis = analyzer.analyze(command)
        
        # Dodaj do tabeli podsumowującej
        table.add_row(
            str(i),
            command.title[:50] + ("..." if len(command.title) > 50 else ""),
            analysis.category.value,
            analysis.priority.value.upper()
        )
    
    console.print(table)
    
    # Szczegółowy podgląd każdego zgłoszenia
    console.print("\n🔍 [bold]Szczegółowy podgląd zgłoszeń:[/bold]")
    
    for i, cmd_data in enumerate(commands, 1):
        if isinstance(cmd_data, dict):
            cmd_text = cmd_data.get('command') or cmd_data.get('code_block') or cmd_data.get('original_line', '')
            cmd_text = cmd_text.strip()
            
            if not cmd_text and 'code_block' in cmd_data:
                first_line = cmd_data['code_block'].split('\n')[0].strip()
                cmd_text = first_line if first_line else 'Brak komendy'
            
            title = cmd_text.split('\n')[0].strip() if cmd_text else 'Nieznana komenda'
            
            command = FailedCommand(
                title=title[:100],
                command=cmd_text,
                source=cmd_data.get('file', 'unknown'),
                command_type=cmd_data.get('command_type', 'shell'),
                status='Failed',
                return_code=cmd_data.get('return_code', 1),
                execution_time=0.0,
                output=cmd_data.get('output', ''),
                error_output=cmd_data.get('error_output', cmd_data.get('error', '')),
                metadata=cmd_data.get('metadata', {})
            )
        else:
            command = cmd_data
        
        analysis = analyzer.analyze(command)
        
        # Generate issue title and header
        issue_title = f"Fix: {command.title}"
        
        # Format command section with syntax highlighting
        command_section = f"""## 📋 Command
```bash
{command}
```
""".format(command=command.command.strip())

        # Format standard output if available
        output_section = ""
        if command.output and command.output.strip():
            output_section = f"""**Output:**
```
{output}
```
""".format(output=command.output.strip())

        # Format error output with proper escaping
        error_section = ""
        error_output = command.error_output or ''
        if error_output.strip():
            error_section = f"""
**Error Output:**
```
{error_output.strip()}
```
"""

        # Format solution section if available
        solution_section = ""
        if analysis.suggested_solution:
            solution_section = f"""## 💡 Suggested Solution
{solution}
""".format(solution=analysis.suggested_solution.strip())

        # Format metadata in a clean, organized way
        metadata_section = f"""
---
### 📝 Metadata
| Field | Value |
|-------|-------|
| **Source** | `{source}` |
| **Exit Code** | `{return_code}` |
| **Execution Time** | {exec_time:.2f}s |
| **Category** | `{category}` |
| **Priority** | `{priority}` |
| **Status** | `{status}` |

### 🏷️ Labels
- `priority:{priority_lower}`
- `category:{category_lower}`
- `bug`
""".format(
            source=command.source,
            return_code=command.return_code,
            exec_time=command.execution_time,
            category=analysis.category.value,
            priority=analysis.priority.value.upper(),
            status=command.status,
            priority_lower=analysis.priority.value.lower(),
            category_lower=analysis.category.value.lower()
        )

        # Combine all sections
        issue_body = "\n".join(filter(None, [
            command_section,
            error_section,
            output_section,
            solution_section,
            metadata_section
        ]))
        
        # Wyświetl panel z podglądem zgłoszenia
        console.print(Panel(
            Markdown(issue_body),
            title=f"[bold]Zgłoszenie #{i}: {issue_title}",
            title_align="left",
            border_style="blue",
            padding=(1, 2)
        ))
    
    console.print("\nℹ️  [yellow]TO JEST TYLKO PODGLĄD. Żadne dane nie zostały wysłane na GitHub.[/yellow]")
    console.print(f"ℹ️  Liczba zgłoszeń do utworzenia: [bold]{len(commands)}[/bold]")


def _show_statistics(stats):
    """Pokazuje statystyki parsowania."""
    if not stats:
        console.print("❌ [red]Brak danych statystycznych do wyświetlenia.[/red]")
        return
        
    console.print(f"\n📈 [bold]Statystyki:[/bold]")
    console.print(f"  • Całkowita liczba poleceń: {stats.get('total_commands', 0)}")
    
    # Only show average execution time if it exists
    if 'average_execution_time' in stats:
        console.print(f"  • Średni czas wykonania: {stats['average_execution_time']}s")
    
    # Only show timeout count if it exists
    if 'timeout_count' in stats:
        console.print(f"  • Timeout'y: {stats['timeout_count']}")
    
    # Only show critical count if it exists
    if 'critical_count' in stats:
        console.print(f"  • Krytyczne błędy: {stats['critical_count']}")

    if stats.get('command_types'):
        console.print(f"\n🔧 [bold]Typy poleceń:[/bold]")
        for cmd_type, count in sorted(stats['command_types'].items(), key=lambda x: x[1], reverse=True):
            console.print(f"  • {cmd_type}: {count}")

    if stats.get('return_codes'):
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
@click.argument('issue_number', type=int)
@click.argument('status', type=click.Choice(['open', 'closed', 'in_progress', 'reopened', 'done'], case_sensitive=False))
@click.option('--token', '-t', help='GitHub token (or set GITHUB_TOKEN env var)')
@click.option('--token-file', type=click.Path(exists=True), help='File containing GitHub token')
@click.option('--repo-owner', '-o', required=True, help='Repository owner')
@click.option('--repo-name', '-r', required=True, help='Repository name')
def update_status(issue_number: int, status: str, token: Optional[str], token_file: Optional[Path], 
                repo_owner: str, repo_name: str):
    """Zaktualizuj status zgłoszenia na GitHubie.
    
    Przykłady:
        mdiss update-status 123 in_progress -o wronai -r mdiss
        mdiss update-status 123 done -o wronai -r mdiss --token ghp_xxx
    """
    _load_env()
    token = _get_token(token, token_file)
    
    if not token:
        console.print("❌ [red]Brak tokenu GitHub. Użyj --token lub ustaw GITHUB_TOKEN.[/red]")
        sys.exit(1)
    
    client = GitHubClient(GitHubConfig(token=token, owner=repo_owner, repo=repo_name))
    
    try:
        issue = client.update_issue_status(issue_number, status)
        console.print(f"✅ [green]Zaktualizowano status zgłoszenia #{issue_number} na '{status}'[/green]")
        console.print(f"🔗 [blue]{issue['html_url']}[/blue]")
    except Exception as e:
        console.print(f"❌ [red]Błąd podczas aktualizacji zgłoszenia: {e}[/red]")
        sys.exit(1)


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