# kloudkompass/tui/screens.py
# -------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Screen base class with lifecycle contract for all TUI screens.
# Implements mount()/render()/unmount() pattern.
# Phase 2.6: Global navigation model with InputResult.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Literal

from kloudkompass.tui.session import SessionState, get_session
from kloudkompass.tui.navigation import Navigator, get_navigator


# ============================================================
# BRANDING CONSTANTS - SINGLE SOURCE OF TRUTH
# ============================================================

BRAND_TITLE = "Kloud Kompass – Multicloud Analytix"
BRAND_SHORT = "Kloud Kompass"

BRAND_BANNER = (
    "╦╔═ ╦  ╔═╗╦ ╦╔╦╗  ╦╔═╔═╗╔╦╗╔═╗╔═╗╔═╗╔═╗\n"
    "╠╩╗ ║  ║ ║║ ║ ║║  ╠╩╗║ ║║║║╠═╝╠═╣╚═╗╚═╗\n"
    "╩ ╩ ╩═╝╚═╝╚═╝═╩╝  ╩ ╩╚═╝╩ ╩╩  ╩ ╩╚═╝╚═╝\n"
    "     Your Cloud Console On Terminal "
)


# Standardized navigation hints - single source of truth
NAV_HINT = "[B] Back    [Q] Quit"


# ============================================================
# INPUT HANDLING - PHASE 2.6 NAVIGATION MODEL
# ============================================================

@dataclass
class InputResult:
    """
    Structured result from get_input().
    
    Preserves raw input while surfacing navigation intents.
    Screens must use this instead of calling input() directly.
    """
    raw: str
    intent: Optional[Literal["quit", "back"]] = None
    
    @property
    def is_navigation(self) -> bool:
        """True if this is a navigation intent, not a menu choice."""
        return self.intent is not None
    
    @property
    def is_quit(self) -> bool:
        """True if user wants to quit."""
        return self.intent == "quit"
    
    @property
    def is_back(self) -> bool:
        """True if user wants to go back."""
        return self.intent == "back"


def confirm_quit() -> bool:
    """
    Ask user to confirm quitting.
    
    Returns True if user confirms, False otherwise.
    Default is No (don't quit) for safety.
    """
    print("\n  Do you want to quit? (y/N): ", end="")
    response = input().strip().lower()
    return response in ("y", "yes")


class Screen(ABC):
    """
    Abstract base class for all TUI screens.
    
    Lifecycle Contract:
        mount()   - One-time setup: header (runs once)
        render()  - Dynamic content only (called on each loop)
        unmount() - Cleanup only if needed
    
    Navigation Contract (Phase 2.6):
        - Screens must use get_input() not input()
        - q/Q triggers quit confirmation
        - b/B triggers back navigation
        - Navigation stack owns root behavior
    
    Invariants:
        - Header renders only in mount()
        - render() never prints headers/footers
        - _mounted guard prevents duplicate mount
    """
    
    # Screen title - uses centralized branding
    title: str = BRAND_TITLE
    
    # Lifecycle guard - prevents duplicate mount
    _mounted: bool = False
    
    def __init__(self):
        self._mounted = False
    
    @property
    def session(self) -> SessionState:
        """Get the current session state."""
        return get_session()
    
    @property
    def navigator(self) -> Navigator:
        """Get the navigator for screen transitions."""
        return get_navigator()
    
    def get_input(self, prompt: str = "Enter choice: ") -> InputResult:
        """
        Get user input with global navigation interception.
        
        This is the ONLY way screens should get input.
        Preserves raw input while detecting q/b navigation intents.
        
        Returns:
            InputResult with raw input and optional navigation intent.
        """
        raw = input(prompt).strip()
        raw_lower = raw.lower()
        
        # Check for quit intent
        if raw_lower in ("q", "quit"):
            return InputResult(raw=raw, intent="quit")
        
        # Check for back intent
        if raw_lower in ("b", "back"):
            return InputResult(raw=raw, intent="back")
        
        return InputResult(raw=raw)
    
    def mount(self) -> None:
        """
        One-time setup when screen becomes active.
        
        Renders header. This runs exactly once per screen instance.
        """
        if self._mounted:
            return
        
        self.print_header()
        self._mounted = True
    
    @abstractmethod
    def render(self) -> None:
        """
        Render dynamic content only.
        
        Called on each display loop. Must NOT print header, footer,
        or attribution. Those are handled by mount()/launch().
        """
        pass
    
    def unmount(self) -> None:
        """
        Cleanup when leaving screen.
        
        Override only if cleanup is needed. Default is no-op.
        """
        pass
    
    @abstractmethod
    def handle_input(self) -> Optional["Screen"]:
        """
        Handle user input and return the next screen.
        
        Must use self.get_input() to capture input.
        
        Returns:
            - A Screen instance to navigate to
            - None to stay on the current screen
            - 'back' triggers navigator.pop()
            - 'exit' requests application exit
        """
        pass
    
    def display(self) -> None:
        """
        Display the screen - calls mount() then render().
        
        This is the main display entry point called by run().
        Ensures lifecycle is respected.
        """
        self.mount()
        self.render()
    
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
                self.unmount()
                # Navigation stack handles root behavior
                popped = self.navigator.pop()
                if popped is None and self.navigator.depth == 0:
                    # At root, back means quit confirmation
                    if confirm_quit():
                        self.navigator.request_exit()
                        return None
                    # User cancelled quit, stay on screen
                    self._mounted = False  # Re-mount on next display
                    continue
                return popped
            elif result == "exit":
                self.unmount()
                self.navigator.request_exit()
                return None
            elif result is not None:
                self.unmount()
                return result
            # If None, loop and redisplay (render only, mount already done)
    
    def print_header(self) -> None:
        """Print a standard header with the screen title."""
        print("\033[2J\033[H", end="")  # Clear screen before header
        print()
        # Custom Kloud Kompass ASCII art header
        print(r"     ____  __.__                   .___  ____  __.                                         ")
        print(r"    |    |/ _|  |   ____  __ __  __| _/ |    |/ _|____   _____ ___________    ______ ______")
        print(r"    |      < |  |  /  _ \|  |  \/ __ |  |      < /  _ \ /     \\____ \__  \  /  ___//  ___/")
        print(r"    |    |  \|  |_(  <_> )  |  / /_/ |  |    |  (  <_> )  Y Y  \  |_> > __ \_\___ \ \___ \ ")
        print(r"    |____|__ \____/\____/|____/\____ |  |____|__ \____/|__|_|  /   __(____  /____  >____  >")
        print(r"            \/                      \/          \/           \/|__|       \/     \/     \/ ")
        print("-" * 92)
        print(f"  {self.title}")
        print("-" * 92)
        print()
    
    def print_nav_hint(self) -> None:
        """Print standardized navigation hint."""
        print()
        print(f"  {NAV_HINT}")
        print()
    
    def print_divider(self) -> None:
        """Print a horizontal divider."""
        print("-" * 50)
    
    def print_error(self, message: str) -> None:
        """Print an error message."""
        print(f"\n[ERROR] {message}\n")
    
    def print_success(self, message: str) -> None:
        """Print a success message."""
        print(f"\n[OK] {message}\n")
    
    def prompt(self, message: str, default: Optional[str] = None) -> str:
        """
        Prompt for text input using get_input().
        
        Shows default value if provided.
        """
        if default:
            prompt_text = f"{message} [{default}]: "
        else:
            prompt_text = f"{message}: "
        
        result = self.get_input(prompt_text)
        if result.is_navigation:
            return result.raw  # Let caller handle navigation
        return result.raw if result.raw else (default or "")
    
    def confirm(self, message: str, default: bool = True) -> bool:
        """
        Prompt for yes/no confirmation.
        """
        default_hint = "Y/n" if default else "y/N"
        result = self.get_input(f"{message} ({default_hint}): ")
        
        if result.is_navigation:
            return False  # Cancel on navigation intent
        
        response = result.raw.lower()
        if not response:
            return default
        return response in ("y", "yes")
