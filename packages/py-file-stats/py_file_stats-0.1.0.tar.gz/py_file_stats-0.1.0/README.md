# File Stats CLI

A command-line tool to recursively scan a directory and collect file extension statistics. It reports:

- **Count:** Number of files with each extension.
- **Max:** Size in bytes of the largest file for each extension.
- **Total:** Total file size in bytes of all files for each extension.

The output can be rendered as a rich table or as plain "pretty" text. You can also sort the results by file extension, count, total size, or max size.

---

## Features

- **Recursive Scanning:** Traverses directories and subdirectories.
- **Multiple Output Formats:** Choose between a rich table and a pretty text output.
- **Custom Sorting:** Sort results by extension (`ext`), file count (`count`), total size (`total`), or maximum file size (`max`).
- **Modern CLI:** Built with [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/).

---

## Requirements

- Python 3.13+
- [Typer](https://typer.tiangolo.com/)
- [Rich](https://rich.readthedocs.io/)

---

## Usage

Examples:

```bash
# Scan the current working directory with default options:
poetry run file-stats

# Scan a specific directory:
poetry run file-stats /path/to/directory

# Choose output format ("table" or "pretty"):
poetry run file-stats --output pretty

# Sort the results by a specific field:
poetry run file-stats --sort-by count
poetry run file-stats --sort-by total
poetry run file-stats --sort-by max

# Combine options; for example, scan /tmp sorted by max in pretty format:
poetry run file-stats /tmp --sort-by max --output pretty
```

---

## Makefile Commands

The provided `Makefile` includes commands for installation, formatting, linting and testing:

```makefile
install:
	poetry install --sync

format:
	poetry run ruff check --fix-only .
	poetry run ruff format .

lint:
	poetry run ruff check .
	poetry run ruff format --diff .
	poetry run mypy .

test:
    poetry run pytest file_stats_tests -vv
```

---

## Building the Package
Developers can build the project for distribution using Poetry. This will create a source distribution and a wheel in the dist directory.

```bash
poetry bu

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

- Built using [Typer](https://typer.tiangolo.com/) for CLI management.
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output.
