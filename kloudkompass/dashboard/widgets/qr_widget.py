# kloudkompass/dashboard/widgets/qr_widget.py
# ----------------------------------------
# Terminal-first QR code widget.
# Uses 'segno' to render scannable bridge links for SSO authentication.

from textual.app import ComposeResult
from textual.widgets import Static
from rich.text import Text
import segno

class QRWidget(Static):
    """
    Renders a scannable QR code for a given URL in the terminal.
    """
    
    DEFAULT_CSS = """
    QRWidget {
        width: auto;
        height: auto;
        padding: 1;
        background: $surface;
        color: black; /* High contrast for scanning */
        align: center middle;
    }
    """

    def __init__(self, url: str, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.utf8_mode = True

    def render(self) -> Text:
        """Generate the QR code string using segno."""
        try:
            qr = segno.make_qr(self.url)
            # We use virtual_terminal with a small scale to fit in TUI
            # For better terminal compatibility, we use 'utf8' block characters
            buffer = ""
            # If utf8_mode is on, use block characters. Otherwise use dots.
            if self.utf8_mode:
                # segno's terminal output can be colored or raw
                # We'll use a manually formatted block string for Rich compatibility
                # Each 'module' becomes a block character
                matrix = qr.matrix
                for row in matrix:
                    line = ""
                    for col in row:
                        line += "██" if col else "  "
                    buffer += line + "\n"
            else:
                # Fallback for old terminals
                buffer = qr.terminal(out=None)
                
            return Text(buffer, justify="center")
        except Exception as e:
            return Text(f"QR Error: {e}", style="bold red")

    def toggle_mode(self):
        """Toggle between UTF-8 and ASCII mode."""
        self.utf8_mode = not self.utf8_mode
        self.refresh()
