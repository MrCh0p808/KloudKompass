# bashcloud/dashboard/widgets/filter_panel.py
# --------------------------------------------
# the filter panel widget It contains controls for
# selecting provider, dates, breakdown type, and threshold.

from datetime import date, timedelta
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Select, Input, Button, Label
from textual.message import Message


class FilterPanel(Vertical):
    """
    Filter panel with controls for cost query parameters.
    
    Contains:
    - Provider selector
    - Start date input
    - End date input
    - Breakdown selector
    - Threshold input
    - Run button
    """
    
    DEFAULT_CSS = """
    FilterPanel {
        width: 100%;
        height: auto;
        padding: 1;
        background: $surface;
        border: solid $primary;
    }
    
    FilterPanel Label {
        padding: 0 1;
    }
    
    FilterPanel Input {
        width: 100%;
        margin-bottom: 1;
    }
    
    FilterPanel Select {
        width: 100%;
        margin-bottom: 1;
    }
    
    FilterPanel Button {
        width: 100%;
        margin-top: 1;
    }
    """
    
    class QueryRequested(Message):
        """Sent when user clicks Run."""
        
        def __init__(
            self,
            provider: str,
            start_date: str,
            end_date: str,
            breakdown: str,
            threshold: float,
        ):
            super().__init__()
            self.provider = provider
            self.start_date = start_date
            self.end_date = end_date
            self.breakdown = breakdown
            self.threshold = threshold
    
    def compose(self) -> ComposeResult:
        """Build the filter panel UI."""
        # Default dates: last 30 days
        end = date.today()
        start = end - timedelta(days=30)
        
        yield Label("Provider")
        yield Select(
            [
                ("AWS", "aws"),
                ("Azure", "azure"),
                ("GCP", "gcp"),
            ],
            id="provider_select",
            value="aws",
        )
        
        yield Label("Start Date")
        yield Input(
            placeholder="YYYY-MM-DD",
            value=start.isoformat(),
            id="start_date",
        )
        
        yield Label("End Date")
        yield Input(
            placeholder="YYYY-MM-DD",
            value=end.isoformat(),
            id="end_date",
        )
        
        yield Label("Breakdown")
        yield Select(
            [
                ("By Service", "service"),
                ("Total", "total"),
                ("By Usage Type", "usage"),
                ("Daily", "daily"),
            ],
            id="breakdown_select",
            value="service",
        )
        
        yield Label("Threshold ($)")
        yield Input(
            placeholder="0.00",
            value="0",
            id="threshold",
        )
        
        yield Button("Run Query", id="run_button", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle Run button click."""
        if event.button.id == "run_button":
            self._submit_query()
    
    def _submit_query(self) -> None:
        """Collect values and post query message."""
        provider_select = self.query_one("#provider_select", Select)
        start_input = self.query_one("#start_date", Input)
        end_input = self.query_one("#end_date", Input)
        breakdown_select = self.query_one("#breakdown_select", Select)
        threshold_input = self.query_one("#threshold", Input)
        
        # Parse threshold
        try:
            threshold = float(threshold_input.value or "0")
        except ValueError:
            threshold = 0.0
        
        self.post_message(self.QueryRequested(
            provider=str(provider_select.value),
            start_date=start_input.value,
            end_date=end_input.value,
            breakdown=str(breakdown_select.value),
            threshold=threshold,
        ))
