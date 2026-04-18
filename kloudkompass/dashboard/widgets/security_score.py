# kloudkompass/dashboard/widgets/security_score.py
# ------------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Security score gauge widget.

from textual.widgets import Static


class SecurityScoreGauge(Static):
    """
    0-100 score gauge with color coding based on severity thresholds.
    """

    DEFAULT_CSS = """
    SecurityScoreGauge {
        dock: top;
        height: 3;
        width: 100%;
        content-align: center middle;
        background: $surface;
        border: solid $secondary;
        margin-bottom: 1;
    }
    
    SecurityScoreGauge.score-high {
        border: solid $success;
        color: $success;
    }
    
    SecurityScoreGauge.score-medium {
        border: solid $warning;
        color: $warning;
    }
    
    SecurityScoreGauge.score-low {
        border: solid $error;
        color: $error;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._score = 100
        self._findings_count = 0

    def on_mount(self) -> None:
        self._render_gauge()

    def set_score(self, score: int, findings_count: int) -> None:
        """Set the score (0-100) and number of findings."""
        self._score = max(0, min(100, score))
        self._findings_count = findings_count
        self._render_gauge()

    def _render_gauge(self) -> None:
        """Calculate and render the 10-segment gauge bar."""
        # Calculate segments (each segment represents 10 points)
        filled_segments = self._score // 10
        empty_segments = 10 - filled_segments
        
        bar = ("█" * filled_segments) + ("░" * empty_segments)
        
        # Determine status icon and CSS class
        icon = "✅"
        css_class = ""
        self.remove_class("score-high", "score-medium", "score-low")
        
        if self._score >= 80:
            icon = "✅"
            self.add_class("score-high")
        elif self._score >= 50:
            icon = "⚠️"
            self.add_class("score-medium")
        else:
            icon = "❌"
            self.add_class("score-low")
            
        status_text = f"Security Posture: [{bar}] {self._score}/100 {icon} ({self._findings_count} findings)"
        self.update(status_text)
