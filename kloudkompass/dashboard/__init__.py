# kloudkompass/dashboard/__init__.py
# --------------------------------
# Exposes the Textual dashboard entry point. Use launch_dashboard()
# to start the full dashboard experience.

from kloudkompass.dashboard.app import launch_dashboard

__all__ = [
    "launch_dashboard",
]
