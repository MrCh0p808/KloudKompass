# kloudkompass/tui/__init__.py
# --------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Exposes the main TUI entry point and core navigation types.

from kloudkompass.tui.main_menu import launch
from kloudkompass.tui.menu_result import MenuResult, BACK, EXIT, result_next
from kloudkompass.tui.footer import render_footer, get_footer_text

__all__ = [
    "launch",
    "MenuResult",
    "BACK",
    "EXIT",
    "result_next",
    "render_footer",
    "get_footer_text",
]

