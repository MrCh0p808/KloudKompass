# kloudkompass/dashboard/widgets/cost_chart.py
# --------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Cost trend chart widget using ASCII sparklines.

from typing import List, Tuple
from textual.app import ComposeResult
from textual.widgets import Static
from textual.containers import Vertical


class CostChart(Static):
    """
    ASCII sparkline widget for rendering cost trends over time.
    """

    DEFAULT_CSS = """
    CostChart {
        height: auto;
        padding: 1 2;
        background: $surface;
        border: solid $primary;
        margin-top: 1;
    }

    CostChart .chart-title {
        text-style: bold;
        text-align: center;
        width: 100%;
        margin-bottom: 1;
    }

    CostChart .chart-body {
        width: 100%;
        color: $accent;
    }
    
    CostChart .chart-labels {
        width: 100%;
        color: $text-muted;
    }
    """

    # Unicode blocks from 1/8 to full block
    BLOCKS = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data: List[Tuple[str, float]] = []

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Daily Cost Trend", classes="chart-title", id="chart_title")
            yield Static("No data available.", classes="chart-body", id="chart_body")
            yield Static("", classes="chart-labels", id="chart_labels")

    def load_data(self, points: List[Tuple[str, float]]) -> None:
        """
        Load coordinate data into the chart and render.
        Args:
            points: List of (label, value) tuples
        """
        self._data = points
        self._render_chart()

    def clear_data(self) -> None:
        """Clear chart data."""
        self._data = []
        self._render_chart()

    def _render_chart(self) -> None:
        """Calculate and render the ASCII blocks."""
        body = self.query_one("#chart_body", Static)
        labels = self.query_one("#chart_labels", Static)
        
        if not self._data:
            body.update("No data available.")
            labels.update("")
            return

        # Extract values
        values = [v for _, v in self._data]
        max_val = max(values) if values else 1.0
        if max_val == 0:
            max_val = 1.0

        # Generate sparkline string
        sparkline = ""
        label_line = ""
        
        for label, val in self._data:
            # Normalize 0.0 to 1.0
            normalized = val / max_val
            # Map to 0-8 scale for blocks
            block_idx = int(normalized * 8)
            # Ensure within bounds
            block_idx = max(0, min(8, block_idx))
            
            # Use block
            sparkline += self.BLOCKS[block_idx] + " "
            
            # Format label (shortened)
            short_label = str(label)[-2:] if str(label) else " "
            label_line += short_label.ljust(2)

        body.update(sparkline)
        labels.update(label_line)
