# bashcloud/utils/formatters.py
# ------------------------------
# I handle output formatting here so the CLI is not tightly coupled to
# Rich tables. Can swap to plain text, JSON passthrough, or other formatters
# without changing CLI code.

from enum import Enum
from typing import List, Optional, Union, Dict, Any

from bashcloud.core.cost_base import CostRecord


class OutputFormat(Enum):
    """Output format options for CLI display."""
    TABLE = "table"
    PLAIN = "plain"
    JSON = "json"
    CSV = "csv"


def format_as_table(
    records: List[CostRecord],
    title: Optional[str] = None,
    show_total: bool = True,
) -> None:
    """
    Print records as a Rich table to the terminal.
    
    I handle empty record lists so the table builder never crashes
    when there are no results.
    """
    try:
        from rich.console import Console
        from rich.table import Table
    except ImportError:
        # I fall back to plain if Rich is not available
        format_as_plain(records, title)
        return
    
    console = Console()
    
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Name", style="white", no_wrap=False)
    table.add_column("Amount", style="green", justify="right")
    table.add_column("Unit", style="dim")
    table.add_column("Period", style="dim")
    
    # I handle empty records by showing a message row
    if not records:
        table.add_row("No records", "-", "-", "-", style="dim italic")
        console.print(table)
        return
    
    total_amount = 0.0
    
    for record in records:
        table.add_row(
            record.name,
            f"{record.amount:.2f}",
            record.unit,
            record.period,
        )
        total_amount += record.amount
    
    if show_total and len(records) > 1:
        table.add_section()
        table.add_row(
            "TOTAL",
            f"{total_amount:.2f}",
            records[0].unit,
            "",
            style="bold yellow",
        )
    
    console.print(table)


def format_as_plain(
    records: List[CostRecord],
    title: Optional[str] = None,
) -> None:
    """
    Print records as plain text.
    
    I use this as a fallback when Rich is not available or user prefers
    simpler output. Works in any terminal.
    """
    if title:
        print(f"\n{title}")
        print("=" * len(title))
    
    # I handle empty records gracefully
    if not records:
        print("No records.")
        print()
        return
    
    # I calculate column widths, handling empty list case
    name_width = max(len(r.name) for r in records)
    name_width = max(name_width, 4)  # At least "Name" header width
    name_width = min(name_width, 50)  # Cap width for readability
    
    # I print header
    print(f"{'Name':<{name_width}}  {'Amount':>12}  {'Unit':<5}  {'Period'}")
    print("-" * (name_width + 35))
    
    total_amount = 0.0
    for record in records:
        name = record.name[:name_width] if len(record.name) > name_width else record.name
        print(f"{name:<{name_width}}  {record.amount:>12.2f}  {record.unit:<5}  {record.period}")
        total_amount += record.amount
    
    if len(records) > 1:
        print("-" * (name_width + 35))
        print(f"{'TOTAL':<{name_width}}  {total_amount:>12.2f}")
    
    print()


def format_as_json(records: List[CostRecord]) -> None:
    """
    Print records as JSON to stdout.
    
    I output valid JSON even for empty lists so piping to jq works.
    """
    import json
    data = [r.to_dict() for r in records]
    print(json.dumps(data, indent=2))


def format_as_csv(records: List[CostRecord], include_header: bool = True) -> None:
    """
    Print records as CSV to stdout.
    
    I always print headers even for empty records so the output is valid CSV.
    """
    import csv
    import sys
    
    writer = csv.writer(sys.stdout)
    
    if include_header:
        writer.writerow(["Name", "Amount", "Unit", "Period"])
    
    for record in records:
        writer.writerow([record.name, record.amount, record.unit, record.period])


def format_records(
    records: List[CostRecord],
    format: OutputFormat,
    title: Optional[str] = None,
) -> None:
    """
    Format and print records in the specified format.
    
    I route to the appropriate formatter based on format enum.
    All formatters handle empty lists gracefully.
    """
    if format == OutputFormat.TABLE:
        format_as_table(records, title)
    elif format == OutputFormat.PLAIN:
        format_as_plain(records, title)
    elif format == OutputFormat.JSON:
        format_as_json(records)
    elif format == OutputFormat.CSV:
        format_as_csv(records)
    else:
        # I default to table
        format_as_table(records, title)
