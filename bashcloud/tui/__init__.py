# bashcloud/tui/__init__.py
# --------------------------
# Exposes the main TUI entry point. The launch() function starts
# the interactive wizard mode.

from bashcloud.tui.main_menu import launch

__all__ = [
    "launch",
]
