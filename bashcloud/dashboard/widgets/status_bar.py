# bashcloud/dashboard/widgets/status_bar.py
# ------------------------------------------
# the status bar widget It shows current operation
# status, record count, and totals.

from textual.widgets import Static


class StatusBar(Static):
    """
    Status bar showing current state information.
    
    Displays: status message, record count, total amount
    """
    
    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text;
        padding: 0 1;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._status = "Ready"
        self._record_count = 0
        self._total_amount = 0.0
    
    def on_mount(self) -> None:
        """Initial render."""
        self._update_display()
    
    def set_status(self, message: str) -> None:
        """Set the status message."""
        self._status = message
        self._update_display()
    
    def set_results(self, count: int, total: float) -> None:
        """Set result statistics."""
        self._record_count = count
        self._total_amount = total
        self._update_display()
    
    def clear_results(self) -> None:
        """Clear result statistics."""
        self._record_count = 0
        self._total_amount = 0.0
        self._update_display()
    
    def _update_display(self) -> None:
        """Update the displayed text."""
        if self._record_count > 0:
            text = f"{self._status} | {self._record_count} records | Total: ${self._total_amount:,.2f}"
        else:
            text = self._status
        
        self.update(text)
