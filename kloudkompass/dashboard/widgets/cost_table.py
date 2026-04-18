# kloudkompass/dashboard/widgets/cost_table.py
# ------------------------------------------
# the cost results table widget It displays CostRecord
# data in a scrollable table format.

from typing import List, Optional

from textual.widgets import DataTable
from textual.app import ComposeResult

from kloudkompass.core.cost_base import CostRecord


class CostTable(DataTable):
    """
    Scrollable table for displaying cost records.
    
    Uses Textual's DataTable for efficient rendering of large datasets
    with keyboard navigation and scrolling.
    """
    
    DEFAULT_CSS = """
    CostTable {
        height: 100%;
        border: solid green;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._records: List[CostRecord] = []
    
    def on_mount(self) -> None:
        """Set up table columns when mounted."""
        self.add_columns("Name", "Amount", "Unit", "Period")
        self.cursor_type = "row"
    
    def load_records(self, records: List[CostRecord]) -> None:
        """
        Load cost records into the table.
        
        Clears existing rows and populate with new data.
        """
        self._records = records
        self.clear()
        
        for record in records:
            self.add_row(
                record.name,
                f"${record.amount:,.2f}",
                record.unit,
                record.period,
            )
    
    def clear_records(self) -> None:
        """Clear all records from the table."""
        self._records = []
        self.clear()
    
    @property
    def record_count(self) -> int:
        """Number of records in the table."""
        return len(self._records)
    
    @property
    def total_amount(self) -> float:
        """Sum of all record amounts."""
        return sum(r.amount for r in self._records)
