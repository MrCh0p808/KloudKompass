# bashcloud/tui/screens.py
# -------------------------
# the Screen base class definition that all TUI screens inherit from.
# This gives me a consistent interface for display and input handling.

from abc import ABC, abstractmethod
from typing import Optional

from bashcloud.tui.session import SessionState, get_session
from bashcloud.tui.navigation import Navigator, get_navigator


class Screen(ABC):
    """
    Abstract base class for all TUI screens.
    
    Each screen represents one step in the wizard flow. Screens display
    content and handle user input. They use the session for state and
    the navigator for screen transitions.
    """
    
    # Screen title displayed at the top
    title: str = "BashCloud"
    
    def __init__(self):
        pass
    
    @property
    def session(self) -> SessionState:
        """Get the current session state."""
        return get_session()
    
    @property
    def navigator(self) -> Navigator:
        """Get the navigator for screen transitions."""
        return get_navigator()
    
    @abstractmethod
    def display(self) -> None:
        """
        Display the screen content.
        
        Called when entering the screen. It should print the UI
        and any current state to the terminal.
        """
        pass
    
    @abstractmethod
    def handle_input(self) -> Optional["Screen"]:
        """
        Handle user input and return the next screen.
        
        Returns:
            - A Screen instance to navigate to
            - None to stay on the current screen
            - 'back' triggers navigator.pop()
            - 'exit' requests application exit
        """
        pass
    
    def run(self) -> Optional["Screen"]:
        """
        Main screen loop: display then handle input.
        
        Keeps looping until the screen returns a new screen or
        signals to go back/exit.
        """
        while True:
            self.display()
            result = self.handle_input()
            
            if result == "back":
                return self.navigator.pop()
            elif result == "exit":
                self.navigator.request_exit()
                return None
            elif result is not None:
                return result
            # If None, loop and redisplay
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        print("\033[2J\033[H", end="")
    
    def print_header(self) -> None:
        """Print a standard header with the screen title."""
        print()
        print("=" * 50)
        print(f"  {self.title}")
        print("=" * 50)
        print()
    
    def print_divider(self) -> None:
        """Print a horizontal divider."""
        print("-" * 50)
    
    def print_error(self, message: str) -> None:
        """Print an error message in red."""
        print(f"\n[ERROR] {message}\n")
    
    def print_success(self, message: str) -> None:
        """Print a success message in green."""
        print(f"\n[OK] {message}\n")
    
    def prompt(self, message: str, default: Optional[str] = None) -> str:
        """
        Prompt for text input.
        
        Shows default value if provided.
        """
        if default:
            prompt_text = f"{message} [{default}]: "
        else:
            prompt_text = f"{message}: "
        
        value = input(prompt_text).strip()
        return value if value else (default or "")
    
    def confirm(self, message: str, default: bool = True) -> bool:
        """
        Prompt for yes/no confirmation.
        """
        default_hint = "Y/n" if default else "y/N"
        response = input(f"{message} ({default_hint}): ").strip().lower()
        
        if not response:
            return default
        return response in ("y", "yes")
