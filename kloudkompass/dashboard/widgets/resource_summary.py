# kloudkompass/dashboard/widgets/resource_summary.py
# --------------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Resource summary widget for high-level environment counts.

from typing import Dict
from textual.widgets import Static


class ResourceSummary(Static):
    """
    Compact horizontal bar showing aggregate resource counts.
    """

    DEFAULT_CSS = """
    ResourceSummary {
        dock: top;
        height: auto;
        width: 100%;
        padding: 1 2;
        content-align: center middle;
        background: $surface;
        border-bottom: solid $primary;
        color: $text;
        text-style: bold;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._counts: Dict[str, int] = {}
        
    def on_mount(self) -> None:
        self._render_summary()

    def set_counts(self, counts: Dict[str, int]) -> None:
        """Update counts dictionary and render."""
        self._counts = counts
        self._render_summary()

    def _render_summary(self) -> None:
        """Render the dictionary as a pipe-separated string."""
        if not self._counts:
            self.update("Loading Resource Summary...")
            return

        segments = []
        for resource, count in self._counts.items():
            segments.append(f"{resource}: {count}")

        summary_text = " │ ".join(segments)
        self.update(summary_text)
