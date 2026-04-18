# kloudkompass/tui/footer.py
# ------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Single source of truth for all attribution text.
# This module provides centralized constants for legal attribution
# used across CLI, TUI, and dashboard contexts.

from typing import Optional


# ============================================================
# ATTRIBUTION CONSTANTS - SINGLE SOURCE OF TRUTH
# ============================================================
# These exact strings are required by the Master Engineering Brief.
# DO NOT modify without legal approval.

ATTRIBUTION_LINE1 = "© 2026 TTox.Tech | Licensed under MIT"
ATTRIBUTION_LINE2 = ""

# Combined full attribution for multi-line contexts
ATTRIBUTION_FULL = ATTRIBUTION_LINE1

# Short version for space-constrained contexts (still legal)
ATTRIBUTION_SHORT = "© 2026 TTox.Tech"

# Legacy constants for backward compatibility
FOOTER_TEXT = ATTRIBUTION_LINE1
FOOTER_LEGAL = ATTRIBUTION_LINE2


def render_footer(console: Optional[object] = None) -> None:
    """
    Render the persistent footer with legal attribution.
    
    This is called ONCE at TUI exit (not at startup, not on every screen).
    Uses plain print for TUI context, Rich Console if provided.
    
    Args:
        console: Optional Rich Console for styled output. If None, uses print().
    """
    if console is not None:
        # Rich Console path (for future use)
        from rich.text import Text
        console.print()
        console.rule(style="dim")
        console.print(
            Text(ATTRIBUTION_LINE1, style="dim"),
            justify="center"
        )
    else:
        # Plain print path for TUI
        print("-" * 50)
        print(f"  {ATTRIBUTION_LINE1}")
        print("-" * 50)


def get_footer_text() -> str:
    """Return the full attribution text for embedding in other contexts."""
    return ATTRIBUTION_FULL


def get_attribution_lines() -> tuple:
    """Return attribution as tuple (line1, line2) for flexible rendering."""
    return (ATTRIBUTION_LINE1, "")
