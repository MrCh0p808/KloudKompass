# kloudkompass/core/updater.py
# ----------------------------
# Auto-updater version check (Feature 50).
# Performs a non-blocking background check against PyPI to detect
# if a newer version of kloudkompass has been published.

import urllib.request
import json
from typing import Optional, Tuple


PYPI_URL = "https://pypi.org/pypi/kloudkompass/json"


def get_current_version() -> str:
    """Get the currently installed version."""
    try:
        from importlib.metadata import version
        return version("kloudkompass")
    except Exception:
        return "0.1.0"


def check_for_update() -> Tuple[bool, Optional[str]]:
    """
    Check PyPI for a newer version of kloudkompass.

    Returns:
        (update_available: bool, latest_version: str | None)
    """
    try:
        current = get_current_version()
        req = urllib.request.Request(PYPI_URL, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode("utf-8"))
            latest = data.get("info", {}).get("version", current)

            if _compare_versions(latest, current) > 0:
                return True, latest
            return False, current
    except Exception:
        return False, None


def _compare_versions(a: str, b: str) -> int:
    """
    Simple semver comparison.
    Returns >0 if a > b, 0 if equal, <0 if a < b.
    """
    try:
        a_parts = [int(x) for x in a.split(".")]
        b_parts = [int(x) for x in b.split(".")]

        # Pad to same length
        while len(a_parts) < len(b_parts):
            a_parts.append(0)
        while len(b_parts) < len(a_parts):
            b_parts.append(0)

        for ap, bp in zip(a_parts, b_parts):
            if ap > bp:
                return 1
            elif ap < bp:
                return -1
        return 0
    except (ValueError, AttributeError):
        return 0
