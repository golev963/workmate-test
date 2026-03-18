"""CLI entry point for session data reports."""

import argparse
import sys
from pathlib import Path

from reader import read_csv_files
from reports import REPORTS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate reports from student session CSV data."
    )
    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        metavar="FILE",
        help="Paths to one or more CSV data files.",
    )
    parser.add_argument(
        "--report",
        required=True,
        choices=list(REPORTS.keys()),
        metavar="REPORT",
        help=f"Report type. Available: {', '.join(REPORTS.keys())}.",
    )
    return parser.parse_args(argv)


def resolve_paths(raw: list[str]) -> list[Path]:
    """Validate that all provided file paths exist."""
    paths: list[Path] = []
    missing: list[str] = []
    for raw_path in raw:
        p = Path(raw_path)
        if not p.exists():
            missing.append(raw_path)
        else:
            paths.append(p)
    if missing:
        print("Error: the following files were not found:", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        sys.exit(1)
    return paths


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    paths = resolve_paths(args.files)
    rows = read_csv_files(paths)
    report = REPORTS[args.report]
    print(report.generate(rows))


if __name__ == "__main__":
    main()
