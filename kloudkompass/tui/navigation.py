# kloudkompass/tui/navigation.py
# ----------------------------
# a simple stack-based navigation controller
# This lets users go back to previous screens without losing state.

from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from kloudkompass.tui.screens import Screen


class Navigator:
    """
    Stack-based navigation controller.
    
    Maintains a stack of screens so that 'back' navigation works
    naturally. When the user chooses back. Pops the current screen
    and show the previous one.
    """
    
    def __init__(self):
        self._stack: List["Screen"] = []
        self._should_exit: bool = False
    
    def push(self, screen: "Screen") -> None:
        """
        Push a new screen onto the stack.
        
        The new screen becomes the current screen.
        """
        self._stack.append(screen)
    
    def pop(self) -> Optional["Screen"]:
        """
        Pop the current screen and return the previous one.
        
        Returns None if the stack is empty after popping.
        """
        if self._stack:
            self._stack.pop()
        return self.current()
    
    def current(self) -> Optional["Screen"]:
        """Get the current (topmost) screen."""
        return self._stack[-1] if self._stack else None
    
    def clear(self) -> None:
        """Clear the entire navigation stack."""
        self._stack.clear()
    
    def reset_to(self, screen: "Screen") -> None:
        """
        Clear the stack and set a new root screen.
        
        Useful for returning to the main menu from anywhere.
        """
        self._stack.clear()
        self._stack.append(screen)
    
    def request_exit(self) -> None:
        """Signal that the application should exit."""
        self._should_exit = True
    
    def should_exit(self) -> bool:
        """Check if exit has been requested."""
        return self._should_exit
    
    @property
    def depth(self) -> int:
        """Current stack depth."""
        return len(self._stack)
    
    @property
    def can_go_back(self) -> bool:
        """True if there is a screen to go back to."""
        return len(self._stack) > 1


# Global navigator instance
_navigator: Optional[Navigator] = None


def get_navigator() -> Navigator:
    """Get the global navigator instance."""
    global _navigator
    if _navigator is None:
        _navigator = Navigator()
    return _navigator


def reset_navigator() -> Navigator:
    """Create a fresh navigator."""
    global _navigator
    _navigator = Navigator()
    return _navigator
