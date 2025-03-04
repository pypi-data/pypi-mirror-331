from collections import defaultdict
from enum import StrEnum
from pathlib import Path
from typing import Literal, TypedDict

from rich import print  # noqa: A004


class SortBy(StrEnum):
    EXT = "ext"
    COUNT = "count"
    TOTAL = "total"
    MAX = "max"


class ExtensionStats(TypedDict):
    count: int
    max: int
    total: int


def gather_file_extension_stats(
    directory: Path,
) -> dict[str, ExtensionStats]:
    stats: dict[str, ExtensionStats] = defaultdict(
        lambda: {"count": 0, "max": 0, "total": 0}
    )
    for file in directory.rglob("*"):
        if not file.is_file():
            continue

        ext = file.suffix.lower() if file.suffix else "no extension"
        try:
            size = file.stat().st_size
        # Would ideally catch a more specific exception here, but the exact error is
        # unknown
        except Exception as e:  # noqa: BLE001
            print(f"[red]Warning:[/] Unable to access {file}: {e}")
            continue

        stats[ext]["count"] += 1
        stats[ext]["total"] += size
        stats[ext]["max"] = max(stats[ext]["max"], size)

    return stats


def _sort_extensions_by_key(
    file_extension_stats: dict[str, ExtensionStats],
    key: Literal["count", "total", "max"],
) -> list[str]:
    return sorted(
        file_extension_stats.keys(),
        key=lambda ext: file_extension_stats[ext][key],
        reverse=True,
    )


def get_sorted_extensions(
    file_extension_stats: dict[str, ExtensionStats], sort_by: SortBy
) -> list[str]:
    # This function looks like it could be simplified by passing the sort_by value
    # directly to the _sort_extensions_by_key function, but it's risky, as the SortBy
    # enum could be modified in the future with new values that don't correspond to the
    # keys in the ExtensionStats dict.
    if sort_by == SortBy.COUNT:
        return _sort_extensions_by_key(file_extension_stats, "count")
    if sort_by == SortBy.TOTAL:
        return _sort_extensions_by_key(file_extension_stats, "total")
    if sort_by == SortBy.MAX:
        return _sort_extensions_by_key(file_extension_stats, "max")
    return sorted(file_extension_stats.keys())
