"""Tests for reports, reader, and CLI."""

import textwrap
from pathlib import Path

import pytest

from reader import read_csv_files
from reports import MedianCoffeeReport
from main import main, parse_args, resolve_paths


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_rows() -> list[dict]:
    return [
        {"student": "Анна", "coffee_spent": "100", "date": "2024-06-01"},
        {"student": "Анна", "coffee_spent": "200", "date": "2024-06-02"},
        {"student": "Анна", "coffee_spent": "300", "date": "2024-06-03"},
        {"student": "Борис", "coffee_spent": "500", "date": "2024-06-01"},
        {"student": "Борис", "coffee_spent": "700", "date": "2024-06-02"},
    ]


@pytest.fixture()
def csv_file(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        student,date,coffee_spent,sleep_hours,study_hours,mood,exam
        Анна,2024-06-01,100,7.0,5,норм,Математика
        Анна,2024-06-02,200,6.5,6,норм,Математика
        Анна,2024-06-03,300,6.0,7,норм,Математика
        Борис,2024-06-01,500,5.0,10,устал,Математика
        Борис,2024-06-02,700,4.5,12,зомби,Математика
    """)
    f = tmp_path / "session.csv"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture()
def second_csv_file(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        student,date,coffee_spent,sleep_hours,study_hours,mood,exam
        Анна,2024-06-10,150,7.0,5,норм,Физика
        Борис,2024-06-10,800,4.0,13,зомби,Физика
    """)
    f = tmp_path / "session2.csv"
    f.write_text(content, encoding="utf-8")
    return f


# ---------------------------------------------------------------------------
# reader
# ---------------------------------------------------------------------------

class TestReadCsvFiles:
    def test_reads_all_rows(self, csv_file: Path) -> None:
        rows = read_csv_files([csv_file])
        assert len(rows) == 5

    def test_combines_multiple_files(self, csv_file: Path, second_csv_file: Path) -> None:
        rows = read_csv_files([csv_file, second_csv_file])
        assert len(rows) == 7

    def test_row_keys(self, csv_file: Path) -> None:
        rows = read_csv_files([csv_file])
        assert set(rows[0].keys()) == {
            "student", "date", "coffee_spent", "sleep_hours",
            "study_hours", "mood", "exam",
        }


# ---------------------------------------------------------------------------
# MedianCoffeeReport
# ---------------------------------------------------------------------------

class TestMedianCoffeeReport:
    def test_correct_median_odd(self, sample_rows: list[dict]) -> None:
        # Анна: [100, 200, 300] → median 200
        report = MedianCoffeeReport()
        output = report.generate(sample_rows)
        assert "Анна" in output
        assert "200" in output

    def test_correct_median_even(self, sample_rows: list[dict]) -> None:
        # Борис: [500, 700] → median 600
        report = MedianCoffeeReport()
        output = report.generate(sample_rows)
        assert "Борис" in output
        assert "600" in output

    def test_sorted_descending(self, sample_rows: list[dict]) -> None:
        report = MedianCoffeeReport()
        output = report.generate(sample_rows)
        lines = [line for line in output.splitlines() if line.strip()]
        # Skip header and separator lines; find data rows
        data_lines = [l for l in lines if "Анна" in l or "Борис" in l]
        assert "Борис" in data_lines[0], "Борис (600) should be first"
        assert "Анна" in data_lines[1], "Анна (200) should be second"

    def test_single_entry_per_student(self) -> None:
        rows = [{"student": "Алиса", "coffee_spent": "350"}]
        report = MedianCoffeeReport()
        output = report.generate(rows)
        assert "Алиса" in output
        assert "350" in output

    def test_empty_rows_returns_table(self) -> None:
        report = MedianCoffeeReport()
        output = report.generate([])
        # Should still return a string (empty table with headers)
        assert isinstance(output, str)


# ---------------------------------------------------------------------------
# CLI – parse_args
# ---------------------------------------------------------------------------

class TestParseArgs:
    def test_valid_args(self, csv_file: Path) -> None:
        args = parse_args(["--files", str(csv_file), "--report", "median-coffee"])
        assert args.report == "median-coffee"
        assert args.files == [str(csv_file)]

    def test_missing_files_flag(self) -> None:
        with pytest.raises(SystemExit):
            parse_args(["--report", "median-coffee"])

    def test_missing_report_flag(self, csv_file: Path) -> None:
        with pytest.raises(SystemExit):
            parse_args(["--files", str(csv_file)])

    def test_invalid_report(self, csv_file: Path) -> None:
        with pytest.raises(SystemExit):
            parse_args(["--files", str(csv_file), "--report", "nonexistent-report"])


# ---------------------------------------------------------------------------
# CLI – resolve_paths
# ---------------------------------------------------------------------------

class TestResolvePaths:
    def test_existing_file(self, csv_file: Path) -> None:
        paths = resolve_paths([str(csv_file)])
        assert paths == [csv_file]

    def test_missing_file_exits(self) -> None:
        with pytest.raises(SystemExit):
            resolve_paths(["/no/such/file.csv"])


# ---------------------------------------------------------------------------
# CLI – integration (main)
# ---------------------------------------------------------------------------

class TestMain:
    def test_end_to_end(self, csv_file: Path, capsys: pytest.CaptureFixture) -> None:
        main(["--files", str(csv_file), "--report", "median-coffee"])
        captured = capsys.readouterr()
        assert "Борис" in captured.out
        assert "Анна" in captured.out

    def test_two_files(
        self,
        csv_file: Path,
        second_csv_file: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        main(["--files", str(csv_file), str(second_csv_file), "--report", "median-coffee"])
        captured = capsys.readouterr()
        assert "Борис" in captured.out
        assert "Анна" in captured.out

    def test_missing_file_exits(self) -> None:
        with pytest.raises(SystemExit):
            main(["--files", "ghost.csv", "--report", "median-coffee"])
