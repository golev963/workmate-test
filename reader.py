"""CSV file reading utilities."""

import csv
from pathlib import Path


def read_csv_files(paths: list[Path]) -> list[dict]:
    """Read and combine rows from multiple CSV files."""
    rows: list[dict] = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows.extend(reader)
    return rows
