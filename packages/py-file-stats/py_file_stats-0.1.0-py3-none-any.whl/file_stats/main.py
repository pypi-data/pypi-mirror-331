from pathlib import Path
from typing import Annotated

import typer

from file_stats.output import OutputType, print_pretty, print_table
from file_stats.stats import (
    SortBy,
    gather_file_extension_stats,
    get_sorted_extensions,
)

app = typer.Typer(rich_markup_mode="rich")


@app.command(
    help=(
        """
        [bold]Scans all files in the given directory (recursively) and collects
        statistics by file extension.[/bold]

        - [cyan]Number of files[/cyan] with each extension
        - [magenta]Size in bytes of the largest file[/magenta] with each extension
        - [green]Total file size in bytes of all files[/green] with each extension
        """
    )
)
def scan(
    directory: Annotated[
        Path | None,
        typer.Argument(
            help="Directory to scan. Defaults to current working directory.",
            exists=True,
            file_okay=False,
            dir_okay=True,
            resolve_path=True,
        ),
    ] = None,
    output: Annotated[
        OutputType,
        typer.Option("--output", "-o", help="Output format", case_sensitive=False),
    ] = OutputType.TABLE,
    sort_by: Annotated[
        SortBy,
        typer.Option(
            "--sort-by",
            "-s",
            help="Sort by field: ext, count, total, max",
            case_sensitive=False,
        ),
    ] = SortBy.EXT,
) -> None:
    """
    Scans all files in the given directory (recursively) and collects
    statistics by file extension
    """
    if directory is None:
        directory = Path.cwd()

    file_extension_stats = gather_file_extension_stats(directory)
    sorted_extensions = get_sorted_extensions(file_extension_stats, sort_by)

    if output == OutputType.TABLE:
        print_table(file_extension_stats, sorted_extensions)
    else:
        print_pretty(file_extension_stats, sorted_extensions)


if __name__ == "__main__":
    app()
