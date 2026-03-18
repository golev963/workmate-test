"""Report generators for student session data."""

from statistics import median
from typing import Protocol

from tabulate import tabulate


class Report(Protocol):
    """Protocol defining the interface for all report types."""

    def generate(self, rows: list[dict]) -> str:
        """Generate a formatted report string from CSV rows."""
        ...


class MedianCoffeeReport:
    """Report showing median coffee spending per student, sorted descending."""

    def generate(self, rows: list[dict]) -> str:
        spending: dict[str, list[float]] = {}
        for row in rows:
            name = row["student"]
            amount = float(row["coffee_spent"])
            spending.setdefault(name, []).append(amount)

        results = [
            (name, median(amounts)) for name, amounts in spending.items()
        ]
        results.sort(key=lambda x: x[1], reverse=True)

        return tabulate(
            results,
            headers=["student", "median_coffee"],
            tablefmt="grid",
            floatfmt=".0f",
        )


REPORTS: dict[str, Report] = {
    "median-coffee": MedianCoffeeReport(),
}
