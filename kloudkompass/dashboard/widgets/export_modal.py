# kloudkompass/dashboard/widgets/export_modal.py
# --------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Export modal for dashboard - export current view to CSV/JSON/Markdown.

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Static, RadioSet, RadioButton


# Export directory
EXPORT_DIR = Path.home() / ".kloudkompass" / "exports"


class ExportModal(ModalScreen[Optional[str]]):
    """
    Modal dialog for export format selection.
    
    Phase 2.6: Export current view to CSV, JSON, or Markdown.
    Returns the export path on success, None on cancel.
    """
    
    DEFAULT_CSS = """
    ExportModal {
        align: center middle;
    }
    
    ExportModal > Vertical {
        width: 45%;
        min-width: 45;
        max-width: 70;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }
    
    ExportModal Static {
        width: 100%;
        text-align: center;
        margin-bottom: 1;
    }
    
    ExportModal .title {
        text-style: bold;
    }
    
    ExportModal RadioSet {
        width: 100%;
        height: 6;
        margin: 1 0;
    }
    
    ExportModal Horizontal {
        width: 100%;
        height: 3;
        align: center middle;
    }
    
    ExportModal Button {
        margin: 0 2;
    }
    """
    
    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, view_name: str = "dashboard", data: dict = None, **kwargs):
        super().__init__(**kwargs)
        self.view_name = view_name
        self.data = data or {}
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Export Dashboard", classes="title")
            yield Static("")
            yield Static("Select format:")
            with RadioSet(id="format_select"):
                yield RadioButton("CSV (Spreadsheet)", id="fmt_csv", value=True)
                yield RadioButton("JSON (Structured)", id="fmt_json")
                yield RadioButton("Markdown (Report)", id="fmt_md")
            with Horizontal():
                yield Button("Cancel", id="btn_cancel")
                yield Button("Export", id="btn_export", variant="primary")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn_export":
            self._do_export()
        else:
            self.dismiss(None)
    
    def action_cancel(self) -> None:
        """Cancel export."""
        self.dismiss(None)
    
    def _do_export(self) -> None:
        """Perform the export."""
        # Get selected format
        radio_set = self.query_one("#format_select", RadioSet)
        selected = radio_set.pressed_button
        
        if selected is None or selected.id == "fmt_csv":
            ext = "csv"
        elif selected.id == "fmt_json":
            ext = "json"
        else:
            ext = "md"
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"kloudkompass_{self.view_name}_{timestamp}.{ext}"
        
        # Ensure export directory exists
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        export_path = EXPORT_DIR / filename
        
        # Write file based on format
        try:
            if ext == "csv":
                self._write_csv(export_path)
            elif ext == "json":
                self._write_json(export_path)
            else:
                self._write_markdown(export_path)
            
            self.dismiss(str(export_path))
        except Exception as e:
            self.app.notify(f"Export failed: {e}", severity="error")
            self.dismiss(None)
    
    def _write_csv(self, path: Path) -> None:
        """Write data as CSV."""
        import csv
        
        with open(path, 'w', newline='') as f:
            if not self.data:
                f.write("No data to export\n")
                return
            
            writer = csv.writer(f)
            
            # Write headers
            if 'headers' in self.data:
                writer.writerow(self.data['headers'])
            
            # Write rows
            if 'rows' in self.data:
                for row in self.data['rows']:
                    writer.writerow(row)
    
    def _write_json(self, path: Path) -> None:
        """Write data as JSON."""
        import json
        
        export_data = {
            'view': self.view_name,
            'exported_at': datetime.now().isoformat(),
            'data': self.data,
        }
        
        with open(path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
    
    def _write_markdown(self, path: Path) -> None:
        """Write data as Markdown."""
        from kloudkompass.tui.screens import BRAND_TITLE
        
        with open(path, 'w') as f:
            f.write(f"# {BRAND_TITLE} Export\n\n")
            f.write(f"**View:** {self.view_name}\n")
            f.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if not self.data:
                f.write("*No data to export*\n")
                return
            
            # Write as table if we have headers and rows
            if 'headers' in self.data and 'rows' in self.data:
                headers = self.data['headers']
                rows = self.data['rows']
                
                # Header row
                f.write("| " + " | ".join(str(h) for h in headers) + " |\n")
                f.write("| " + " | ".join("---" for _ in headers) + " |\n")
                
                # Data rows
                for row in rows:
                    f.write("| " + " | ".join(str(c) for c in row) + " |\n")
