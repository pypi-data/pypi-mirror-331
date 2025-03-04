from enum import StrEnum

from rich import print  # noqa: A004
from rich.table import Table

from file_stats.stats import ExtensionStats


class OutputType(StrEnum):
    TABLE = "table"
    PRETTY = "pretty"


def print_table(
    file_extension_stats: dict[str, ExtensionStats],
    sorted_extensions: list[str] | None = None,
) -> None:
    table = Table(title="File Statistics")
    table.add_column("Extension", style="cyan")
    table.add_column("Count", style="magenta")
    table.add_column("Largest File Size", style="green")
    table.add_column("Total File Size", style="yellow")

    for ext in sorted_extensions or sorted(file_extension_stats.keys()):
        table.add_row(
            ext,
            f"{file_extension_stats[ext]['count']:,}",
            f"{file_extension_stats[ext]['max']:,} bytes",
            f"{file_extension_stats[ext]['total']:,} bytes",
        )

    print(table)


def print_pretty(
    file_extension_stats: dict[str, ExtensionStats],
    sorted_extensions: list[str] | None = None,
) -> None:
    for ext in sorted_extensions or sorted(file_extension_stats.keys()):
        print(f"Extension: {ext}")
        print(f"  Count: {file_extension_stats[ext]['count']:,}")
        print(f"  Largest File Size: {file_extension_stats[ext]['max']:,} bytes")
        print(f"  Total File Size: {file_extension_stats[ext]['total']:,} bytes\n")
