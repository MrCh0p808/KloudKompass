# kloudkompass/tui/menu_result.py
# -----------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Frozen dataclass for deterministic navigation.
# All prompts must return MenuResult, not raw values.

from dataclasses import dataclass
from typing import Any, Literal


# Valid navigation actions
Action = Literal["next", "back", "exit"]


@dataclass(frozen=True)
class MenuResult:
    """
    Immutable result from any TUI prompt or menu.
    
    Every prompt must return a MenuResult. This ensures deterministic
    navigation and prevents implicit state changes.
    
    Args:
        value: The selected value (can be None for navigation-only actions)
        action: One of "next", "back", or "exit"
    
    Invariant:
        - action MUST be one of the valid Action literals
        - value interpretation depends on the calling screen
    """
    value: Any
    action: Action
    
    def __post_init__(self):
        """Validate action is one of the allowed values."""
        valid_actions = ("next", "back", "exit")
        if self.action not in valid_actions:
            raise ValueError(
                f"Invalid action '{self.action}'. Must be one of: {valid_actions}"
            )
    
    @property
    def is_next(self) -> bool:
        """Check if action is to proceed forward."""
        return self.action == "next"
    
    @property
    def is_back(self) -> bool:
        """Check if action is to go back."""
        return self.action == "back"
    
    @property
    def is_exit(self) -> bool:
        """Check if action is to exit."""
        return self.action == "exit"


# Pre-built results for common navigation actions
BACK = MenuResult(value=None, action="back")
EXIT = MenuResult(value=None, action="exit")


def result_next(value: Any) -> MenuResult:
    """Create a MenuResult with action='next'."""
    return MenuResult(value=value, action="next")
